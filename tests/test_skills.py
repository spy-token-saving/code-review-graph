"""Tests for skills and hooks auto-install."""

import json
import stat
from unittest.mock import patch

from code_review_graph.skills import (
    _CLAUDE_MD_SECTION_MARKER,
    PLATFORMS,
    _cursor_hook_scripts,
    generate_cursor_hooks_config,
    generate_hooks_config,
    generate_skills,
    inject_claude_md,
    install_cursor_hooks,
    install_hooks,
    install_platform_configs,
)


class TestGenerateSkills:
    def test_creates_skills_directory(self, tmp_path):
        result = generate_skills(tmp_path)
        assert result.is_dir()
        assert result == tmp_path / ".claude" / "skills"

    def test_creates_four_skill_files(self, tmp_path):
        skills_dir = generate_skills(tmp_path)
        files = sorted(f.name for f in skills_dir.iterdir())
        assert files == [
            "debug-issue.md",
            "explore-codebase.md",
            "refactor-safely.md",
            "review-changes.md",
        ]

    def test_skill_files_have_frontmatter(self, tmp_path):
        skills_dir = generate_skills(tmp_path)
        for path in skills_dir.iterdir():
            content = path.read_text()
            assert content.startswith("---\n")
            assert "name:" in content
            assert "description:" in content
            # Frontmatter closes
            lines = content.split("\n")
            assert lines[0] == "---"
            closing_idx = content.index("---", 4)
            assert closing_idx > 0

    def test_custom_skills_dir(self, tmp_path):
        custom = tmp_path / "my-skills"
        result = generate_skills(tmp_path, skills_dir=custom)
        assert result == custom
        assert result.is_dir()
        assert len(list(result.iterdir())) == 4

    def test_skill_content_includes_get_minimal_context(self, tmp_path):
        """Every skill template must reference get_minimal_context."""
        skills_dir = generate_skills(tmp_path)
        for path in skills_dir.iterdir():
            content = path.read_text()
            assert "get_minimal_context" in content, (
                f"{path.name} missing get_minimal_context reference"
            )

    def test_skill_content_includes_detail_level(self, tmp_path):
        """Every skill template must reference detail_level."""
        skills_dir = generate_skills(tmp_path)
        for path in skills_dir.iterdir():
            content = path.read_text()
            assert "detail_level" in content, f"{path.name} missing detail_level reference"

    def test_idempotent(self, tmp_path):
        """Running twice should not fail and files should still be valid."""
        generate_skills(tmp_path)
        generate_skills(tmp_path)
        skills_dir = tmp_path / ".claude" / "skills"
        assert len(list(skills_dir.iterdir())) == 4


class TestGenerateHooksConfig:
    def test_returns_dict_with_hooks(self):
        config = generate_hooks_config()
        assert "hooks" in config

    def test_has_post_tool_use(self):
        config = generate_hooks_config()
        assert "PostToolUse" in config["hooks"]
        hooks = config["hooks"]["PostToolUse"]
        assert len(hooks) >= 1
        assert hooks[0]["matcher"] == "Edit|Write|Bash"
        assert "update" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 5000

    def test_has_session_start(self):
        config = generate_hooks_config()
        assert "SessionStart" in config["hooks"]
        hooks = config["hooks"]["SessionStart"]
        assert len(hooks) >= 1
        assert "status" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 3000

    def test_has_pre_commit(self):
        config = generate_hooks_config()
        assert "PreCommit" in config["hooks"]
        hooks = config["hooks"]["PreCommit"]
        assert len(hooks) >= 1
        assert "detect-changes" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 10000

    def test_has_all_three_hook_types(self):
        config = generate_hooks_config()
        hook_types = set(config["hooks"].keys())
        assert hook_types == {"PostToolUse", "SessionStart", "PreCommit"}


class TestInstallHooks:
    def test_creates_settings_file(self, tmp_path):
        install_hooks(tmp_path)
        settings_path = tmp_path / ".claude" / "settings.json"
        assert settings_path.exists()
        data = json.loads(settings_path.read_text())
        assert "hooks" in data

    def test_merges_with_existing(self, tmp_path):
        settings_dir = tmp_path / ".claude"
        settings_dir.mkdir(parents=True)
        existing = {"customSetting": True, "hooks": {"OtherHook": []}}
        (settings_dir / "settings.json").write_text(json.dumps(existing))

        install_hooks(tmp_path)

        data = json.loads((settings_dir / "settings.json").read_text())
        assert data["customSetting"] is True
        assert "PostToolUse" in data["hooks"]
        assert "SessionStart" in data["hooks"]
        assert "PreCommit" in data["hooks"]

    def test_creates_claude_directory(self, tmp_path):
        install_hooks(tmp_path)
        assert (tmp_path / ".claude").is_dir()


class TestInjectClaudeMd:
    def test_creates_section_in_new_file(self, tmp_path):
        inject_claude_md(tmp_path)
        content = (tmp_path / "CLAUDE.md").read_text()
        assert _CLAUDE_MD_SECTION_MARKER in content
        assert "MCP Tools" in content

    def test_appends_to_existing_file(self, tmp_path):
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting content.\n")

        inject_claude_md(tmp_path)

        content = claude_md.read_text()
        assert "# My Project" in content
        assert "Existing content." in content
        assert _CLAUDE_MD_SECTION_MARKER in content

    def test_idempotent(self, tmp_path):
        """Running twice should not duplicate the section."""
        inject_claude_md(tmp_path)
        first_content = (tmp_path / "CLAUDE.md").read_text()

        inject_claude_md(tmp_path)
        second_content = (tmp_path / "CLAUDE.md").read_text()

        assert first_content == second_content
        assert second_content.count(_CLAUDE_MD_SECTION_MARKER) == 1

    def test_idempotent_with_existing_content(self, tmp_path):
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Existing\n")

        inject_claude_md(tmp_path)
        first_content = claude_md.read_text()

        inject_claude_md(tmp_path)
        second_content = claude_md.read_text()

        assert first_content == second_content
        assert second_content.count(_CLAUDE_MD_SECTION_MARKER) == 1


class TestInstallPlatformConfigs:
    def test_install_cursor_config(self, tmp_path):
        with patch.dict(
            PLATFORMS,
            {
                "cursor": {**PLATFORMS["cursor"], "detect": lambda: True},
            },
        ):
            configured = install_platform_configs(tmp_path, target="cursor")
        assert "Cursor" in configured
        config_path = tmp_path / ".cursor" / "mcp.json"
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert "code-review-graph" in data["mcpServers"]
        assert data["mcpServers"]["code-review-graph"]["type"] == "stdio"

    def test_install_windsurf_config(self, tmp_path):
        windsurf_dir = tmp_path / ".codeium" / "windsurf"
        windsurf_dir.mkdir(parents=True)
        config_path = windsurf_dir / "mcp_config.json"
        with patch.dict(
            PLATFORMS,
            {
                "windsurf": {
                    **PLATFORMS["windsurf"],
                    "config_path": lambda root: config_path,
                    "detect": lambda: True,
                },
            },
        ):
            configured = install_platform_configs(tmp_path, target="windsurf")
        assert "Windsurf" in configured
        data = json.loads(config_path.read_text())
        entry = data["mcpServers"]["code-review-graph"]
        assert "type" not in entry
        import shutil

        expected_cmd = "uvx" if shutil.which("uvx") else "code-review-graph"
        assert entry["command"] == expected_cmd

    def test_install_zed_config(self, tmp_path):
        zed_settings = tmp_path / "zed" / "settings.json"
        zed_settings.parent.mkdir(parents=True)
        with patch.dict(
            PLATFORMS,
            {
                "zed": {
                    **PLATFORMS["zed"],
                    "config_path": lambda root: zed_settings,
                    "detect": lambda: True,
                },
            },
        ):
            configured = install_platform_configs(tmp_path, target="zed")
        assert "Zed" in configured
        data = json.loads(zed_settings.read_text())
        assert "context_servers" in data
        assert "code-review-graph" in data["context_servers"]

    def test_install_continue_config(self, tmp_path):
        continue_dir = tmp_path / ".continue"
        continue_dir.mkdir()
        config_path = continue_dir / "config.json"
        with patch.dict(
            PLATFORMS,
            {
                "continue": {
                    **PLATFORMS["continue"],
                    "config_path": lambda root: config_path,
                    "detect": lambda: True,
                },
            },
        ):
            configured = install_platform_configs(tmp_path, target="continue")
        assert "Continue" in configured
        data = json.loads(config_path.read_text())
        assert isinstance(data["mcpServers"], list)
        assert data["mcpServers"][0]["name"] == "code-review-graph"
        assert data["mcpServers"][0]["type"] == "stdio"

    def test_install_opencode_config(self, tmp_path):
        configured = install_platform_configs(tmp_path, target="opencode")
        assert "OpenCode" in configured
        config_path = tmp_path / ".opencode.json"
        data = json.loads(config_path.read_text())
        entry = data["mcpServers"]["code-review-graph"]
        assert entry["type"] == "stdio"
        assert entry["env"] == []

    def test_install_all_detected(self, tmp_path):
        """Installing 'all' configures claude and opencode (always detected)."""
        configured = install_platform_configs(tmp_path, target="all")
        assert "Claude Code" in configured
        assert "OpenCode" in configured
        assert (tmp_path / ".mcp.json").exists()
        assert (tmp_path / ".opencode.json").exists()

    def test_merge_existing_servers(self, tmp_path):
        """Should not overwrite existing MCP servers."""
        mcp_path = tmp_path / ".mcp.json"
        existing = {"mcpServers": {"other-server": {"command": "other"}}}
        mcp_path.write_text(json.dumps(existing))
        install_platform_configs(tmp_path, target="claude")
        data = json.loads(mcp_path.read_text())
        assert "other-server" in data["mcpServers"]
        assert "code-review-graph" in data["mcpServers"]

    def test_dry_run_no_write(self, tmp_path):
        configured = install_platform_configs(tmp_path, target="claude", dry_run=True)
        assert "Claude Code" in configured
        assert not (tmp_path / ".mcp.json").exists()

    def test_already_configured_skips(self, tmp_path):
        install_platform_configs(tmp_path, target="claude")
        configured = install_platform_configs(tmp_path, target="claude")
        assert "Claude Code" in configured

    def test_continue_array_no_duplicate(self, tmp_path):
        config_path = tmp_path / ".continue" / "config.json"
        config_path.parent.mkdir(parents=True)
        existing = {
            "mcpServers": [{"name": "code-review-graph", "command": "uvx", "args": ["serve"]}]
        }
        config_path.write_text(json.dumps(existing))
        with patch.dict(
            PLATFORMS,
            {
                "continue": {
                    **PLATFORMS["continue"],
                    "config_path": lambda root: config_path,
                    "detect": lambda: True,
                },
            },
        ):
            install_platform_configs(tmp_path, target="continue")
        data = json.loads(config_path.read_text())
        assert len(data["mcpServers"]) == 1


class TestCursorHooksConfig:
    """Tests for generate_cursor_hooks_config()."""

    def test_has_version_1(self):
        config = generate_cursor_hooks_config()
        assert config["version"] == 1

    def test_has_after_file_edit(self):
        config = generate_cursor_hooks_config()
        hooks = config["hooks"]["afterFileEdit"]
        assert len(hooks) >= 1
        assert "crg-update.sh" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 5

    def test_has_session_start(self):
        config = generate_cursor_hooks_config()
        hooks = config["hooks"]["sessionStart"]
        assert len(hooks) >= 1
        assert "crg-session-start.sh" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 5

    def test_has_before_shell_execution(self):
        config = generate_cursor_hooks_config()
        hooks = config["hooks"]["beforeShellExecution"]
        assert len(hooks) >= 1
        assert "crg-pre-commit.sh" in hooks[0]["command"]
        assert hooks[0]["timeout"] == 10
        assert hooks[0]["matcher"] == "^git\\s+commit"

    def test_has_all_three_hook_types(self):
        config = generate_cursor_hooks_config()
        hook_types = set(config["hooks"].keys())
        assert hook_types == {"afterFileEdit", "sessionStart", "beforeShellExecution"}

    def test_commands_point_to_home_cursor_hooks(self):
        config = generate_cursor_hooks_config()
        from pathlib import Path

        hooks_dir = str(Path.home() / ".cursor" / "hooks")
        for event, entries in config["hooks"].items():
            for entry in entries:
                assert entry["command"].startswith(hooks_dir), (
                    f"{event} command does not start with {hooks_dir}"
                )


class TestCursorHookScripts:
    """Tests for _cursor_hook_scripts()."""

    def test_returns_three_scripts(self):
        scripts = _cursor_hook_scripts()
        assert set(scripts.keys()) == {
            "crg-update.sh",
            "crg-session-start.sh",
            "crg-pre-commit.sh",
        }

    def test_scripts_start_with_shebang(self):
        scripts = _cursor_hook_scripts()
        for name, content in scripts.items():
            assert content.startswith("#!/usr/bin/env bash"), f"{name} missing shebang line"

    def test_scripts_exit_zero(self):
        """Each script must end with exit 0 for graceful failure."""
        scripts = _cursor_hook_scripts()
        for name, content in scripts.items():
            assert "exit 0" in content, f"{name} missing 'exit 0'"

    def test_scripts_consume_stdin(self):
        """Each script must consume stdin (Cursor protocol)."""
        scripts = _cursor_hook_scripts()
        for name, content in scripts.items():
            assert "cat > /dev/null" in content, f"{name} missing stdin consumption"

    def test_update_script_runs_update(self):
        scripts = _cursor_hook_scripts()
        assert "code-review-graph update --skip-flows" in scripts["crg-update.sh"]

    def test_session_start_script_runs_status(self):
        scripts = _cursor_hook_scripts()
        assert "code-review-graph status" in scripts["crg-session-start.sh"]

    def test_pre_commit_script_runs_detect_changes(self):
        scripts = _cursor_hook_scripts()
        assert "code-review-graph detect-changes --brief" in scripts["crg-pre-commit.sh"]


class TestInstallCursorHooks:
    """Tests for install_cursor_hooks()."""

    def test_creates_hooks_json(self, tmp_path):
        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            result = install_cursor_hooks()
        hooks_json = tmp_path / ".cursor" / "hooks.json"
        assert hooks_json.exists()
        assert result == hooks_json
        data = json.loads(hooks_json.read_text())
        assert data["version"] == 1
        assert "afterFileEdit" in data["hooks"]

    def test_creates_hook_scripts(self, tmp_path):
        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            install_cursor_hooks()
        hooks_dir = tmp_path / ".cursor" / "hooks"
        assert (hooks_dir / "crg-update.sh").exists()
        assert (hooks_dir / "crg-session-start.sh").exists()
        assert (hooks_dir / "crg-pre-commit.sh").exists()

    def test_scripts_are_executable(self, tmp_path):
        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            install_cursor_hooks()
        hooks_dir = tmp_path / ".cursor" / "hooks"
        for script in hooks_dir.iterdir():
            mode = script.stat().st_mode
            assert mode & stat.S_IXUSR, f"{script.name} not executable by owner"
            assert mode & stat.S_IXGRP, f"{script.name} not executable by group"

    def test_merges_with_existing_hooks_json(self, tmp_path):
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir(parents=True)
        existing = {
            "version": 1,
            "hooks": {
                "afterFileEdit": [{"command": "/some/other/hook.sh", "timeout": 3}],
                "stop": [{"command": "/some/stop-hook.sh", "timeout": 2}],
            },
        }
        (cursor_dir / "hooks.json").write_text(json.dumps(existing))

        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            install_cursor_hooks()

        data = json.loads((cursor_dir / "hooks.json").read_text())
        # Original hook preserved
        commands = [h["command"] for h in data["hooks"]["afterFileEdit"]]
        assert "/some/other/hook.sh" in commands
        # Our hook added
        assert any("crg-update.sh" in c for c in commands)
        # Unrelated hook type preserved
        assert "stop" in data["hooks"]

    def test_no_duplicate_on_reinstall(self, tmp_path):
        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            install_cursor_hooks()
            install_cursor_hooks()

        data = json.loads((tmp_path / ".cursor" / "hooks.json").read_text())
        # Each event type should have exactly 1 crg hook
        for event, entries in data["hooks"].items():
            crg_hooks = [h for h in entries if "crg-" in h.get("command", "")]
            assert len(crg_hooks) == 1, f"{event} has {len(crg_hooks)} crg hooks after reinstall"

    def test_handles_corrupt_existing_json(self, tmp_path):
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir(parents=True)
        (cursor_dir / "hooks.json").write_text("not valid json{{{")

        with patch("code_review_graph.skills.Path.home", return_value=tmp_path):
            result = install_cursor_hooks()

        assert result.exists()
        data = json.loads(result.read_text())
        assert data["version"] == 1
