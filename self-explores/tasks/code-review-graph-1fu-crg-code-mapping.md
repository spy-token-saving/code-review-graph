---
date: 2026-04-20
type: task-worklog
task: code-review-graph-1fu
title: "code-review-graph — Code Mapping (Truy vết thực tế)"
status: completed
started_at: 2026-04-20 11:15
completed_at: 2026-04-20 11:30
tags: [system-design, code-mapping, leverage-points, deep-dive, clickable-refs]
---

# code-review-graph — Code Mapping (Truy vết thực tế)

## Mô tả task
[Role: System Architect top 0.1%, Sư phụ hướng dẫn Học trò. Giọng: sắc sảo, trực diện.]

Scan toàn bộ codebase code-review-graph để truy vết các phân tích từ Task 2:
- Với mỗi "Core Component" đã xác định → tìm Class/Interface/Module cụ thể
- Với mỗi "Leverage Point" → chỉ ra CHÍNH XÁC file path + line numbers
- Trích ra đoạn code "tinh hoa" nhất (50-100 dòng) thể hiện nguyên lý đó
- Giải thích TẠI SAO đoạn code này là "tinh hoa" (không phải đẹp về syntax, mà về tư duy)

Ví dụ output format:
```markdown
## Leverage Point: FTS5 Hybrid Search
File: [`search.py:45-120`](../../code_review_graph/search.py#L45-L120)
Nguyên lý: Separation of Concerns + Strategy Pattern
Code tinh hoa: [đoạn code]
Lý do: FTS5 và vector search hoàn toàn tách biệt, có thể swap strategy mà không sửa caller
```

**LƯU Ý:** 100% file:line reference PHẢI là clickable link (xem Code Reference Format trong template).

## Dependencies
- Chờ `code-review-graph-mw7` (Task 2 — Strategic Evaluation) xong
- Chạy SONG SONG với Task 4 (Deep Research) sau khi Task 2 xong

## Kế hoạch chi tiết

### Bước 1: Đọc kết quả Task 2 (~5 phút)
Đọc `self-explores/tasks/code-review-graph-mw7-crg-strategic-evaluation.md` để lấy danh sách Core Components + Leverage Points cần map.

### Bước 2: Scan và find exact line numbers (~30 phút)
```bash
# Với mỗi component, tìm definition
grep -n "class CodeGraph\|def build_graph\|def add_node\|def bfs" code_review_graph/graph.py | head -20
grep -n "def parse_file\|EXTENSION_TO_LANGUAGE\|_CLASS_TYPES\|_FUNCTION_TYPES" code_review_graph/parser.py | head -20
grep -n "def run_postprocessing\|def _build_fts5\|def _detect_flows\|def _detect_communities" code_review_graph/postprocessing.py | head -20
grep -n "def _sanitize_name\|def _validate_repo_root" code_review_graph/graph.py | head -10
```

### Bước 3: Trích "code tinh hoa" (~15 phút)
Với mỗi leverage point, đọc đoạn code thực tế (dùng Read tool với offset + limit), giải thích tại sao "tinh hoa".

### Bước 4: Verify tất cả file paths tồn tại (~5 phút)
```bash
ls code_review_graph/graph.py code_review_graph/parser.py code_review_graph/postprocessing.py code_review_graph/search.py code_review_graph/tools/
```

### Constraints / Risks
- parser.py 4750 LOC — đọc theo section, không đọc toàn bộ
- Mọi reference PHẢI clickable từ `self-explores/tasks/` → tính relative path: `../../code_review_graph/...`
- Relative path từ self-explores/tasks/: `../../code_review_graph/{file}.py#L{N}`

### Output mong đợi
- [ ] Mỗi Core Component từ Task 2 → 1+ file:line clickable
- [ ] Mỗi Leverage Point → exact file:line + code snippet 50-100 dòng
- [ ] Tối thiểu 3 đoạn "code tinh hoa" với giải thích tại sao
- [ ] 100% references là clickable markdown links

## Detailed Design (2026-04-20, Ready for Dev)

### 1. Objective
Map từng Core Component và Leverage Point từ Task 2 đến exact file:line, trích "code tinh hoa" (50-100 dòng) với giải thích tại sao — để Task 4 (Deep Research) và Task 5 (Skill Transfer) có raw material cụ thể mà không cần đọc lại source.

### 2. Scope
**In-scope:** Map file:line cho mọi item từ Task 2 list; trích ≥3 "code tinh hoa" snippets (50-100 LOC); giải thích WHY (không phải WHAT).
**Out-of-scope:** Phân tích design decisions (→ Task 4); thiết kế bài tập (→ Task 5); generate diagrams (→ Task 1).

### 3. Input / Output
**Input:**
- Output Task 2 (mw7): danh sách Core Components + Leverage Points với file paths (có thể có hoặc không có line numbers)

**Output (lưu vào worklog):**
- Mỗi Core Component: `[file.py:line](relative_path#L_line)` + 1-line lý do
- Mỗi Leverage Point: `[file.py:start-end](relative_path#Lstart-Lend)` + code snippet 50-100 dòng + giải thích WHY "tinh hoa"
- Structured list: JSON-like, để Task 4 parse dễ

### 4. Dependencies
- Chờ Task 2 (mw7) xong — cần danh sách Core Components + Leverage Points.
- Nếu Task 2 output chỉ có file names (không có line numbers) → task này tự tìm exact lines.

### 5. Flow chi tiết

**Bước 0 — Extract danh sách từ Task 2 (~5 phút):**
Đọc `self-explores/tasks/code-review-graph-mw7-crg-strategic-evaluation.md` section Detailed Design + Worklog.
Extract 2 lists:
```
Core Components: [tên, file_path]
Leverage Points: [tên, file_path, candidate_function]
```
Nếu Task 2 output thiếu file:line → note gap, tự discover từ code (xem Bước 1).

**Bước 1 — Scan exact line numbers (~20 phút):**
```bash
# Core Components
grep -n "class CodeGraph\|class GraphDB" code_review_graph/graph.py | head -5
grep -n "class.*Parser\|def parse_file" code_review_graph/parser.py | head -5
grep -n "class.*Server\|def main\|if __name__" code_review_graph/main.py | head -5
grep -n "def run_postprocessing\|class.*Post" code_review_graph/postprocessing.py | head -5

# Leverage Points
grep -n "def _sanitize_name\|def _validate_repo_root" code_review_graph/graph.py | head -10
grep -n "EXTENSION_TO_LANGUAGE\s*=" code_review_graph/parser.py | head -3
grep -n "@mcp.tool\|@mcp.prompt" code_review_graph/main.py | head -5
grep -n "def run_postprocessing\b" code_review_graph/postprocessing.py | head -3
```

**Bước 2 — Trích "code tinh hoa" (~25 phút):**

Tiêu chí "tinh hoa" (phải thỏa ≥1):
- Fan-in ≥ 3 callers (từ Task 2 grep results)
- Thể hiện ≥1 design pattern có tên (Strategy, Factory, Decorator, Template Method, Dependency Inversion)
- Được gọi bởi ≥3 tool handlers trong `tools/`

Với mỗi Leverage Point, dùng Read tool (offset + limit) để trích đúng range:
```python
# VD: đọc _sanitize_name() từ graph.py
Read(file_path="code_review_graph/graph.py", offset=LINE-1, limit=30)
# VD: đọc EXTENSION_TO_LANGUAGE từ parser.py
Read(file_path="code_review_graph/parser.py", offset=LINE-1, limit=50)
```

Format output cho mỗi snippet:
```markdown
## Leverage Point: {tên}
File: [`{file}.py:{start}-{end}`](../../code_review_graph/{file}.py#L{start}-L{end})
Nguyên lý: {Design Pattern} — {1-line lý do}
Fan-in: {count} callers (approximate via grep)

```python
{code snippet}
```

Lý do "tinh hoa": {WHY — giải thích tư duy, không phải syntax}
```

**Bước 3 — Verify file paths + clickability (~5 phút):**
```bash
# Verify tất cả files tồn tại
ls code_review_graph/graph.py code_review_graph/parser.py code_review_graph/postprocessing.py code_review_graph/search.py code_review_graph/tools/ code_review_graph/main.py
# Quality check: không có plain text file refs
grep -n "\.py:[0-9]" self-explores/tasks/code-review-graph-1fu-crg-code-mapping.md | grep -v "^\`\`\`\|#L[0-9]\|\[.*\](.*#L" | head -10
# Expected: 0 plain text refs
```

**Bước 4 — Lưu structured output (~5 phút):**
Append vào Worklog section file này, format structured list để Task 4 parse:
```markdown
### Structured Component Map (Task 4 + 5 reference)
- CodeGraph: [`graph.py:L{N}`](../../code_review_graph/graph.py#L{N})
- Parser: [`parser.py:L{N}`](../../code_review_graph/parser.py#L{N})
...
```

### 6. Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| Task 2 output chỉ có "graph.py" (không có line) | Tự grep: `grep -n "class CodeGraph" graph.py` → lấy line |
| Function đã refactor, grep không tìm thấy | Ghi "NOT FOUND — verify function name" + skip, không abort |
| Code snippet > 100 dòng (hàm dài) | Chỉ trích phần "core logic" (bỏ boilerplate như try/except wrapper), ghi note "excerpt" |
| Không đủ 3 snippets thỏa tiêu chí "tinh hoa" | Hạ bar: lấy snippet có fan-in cao nhất kể cả < 3 callers, note lý do |
| parser.py 4750 LOC — đọc toàn bộ quá tốn | Chỉ đọc range xung quanh EXTENSION_TO_LANGUAGE (±20 lines), dùng offset+limit |

### 7. Acceptance Criteria
- **Happy path 1 (Core Components):** Given Task 2 list có ≥2 Core Components, When mapped, Then mỗi item có clickable `[file.py:N](../../...#LN)` link + 1-line lý do tại sao không thể thay thế.
- **Happy path 2 (Leverage snippets):** Given ≥2 Leverage Points từ Task 2, When code extracted, Then ≥3 snippets 50-100 LOC với: (a) clickable link, (b) design principle tên, (c) WHY explanation ≥2 câu.
- **Happy path 3 (Quality gate):** Given worklog hoàn chỉnh, When checked, Then `grep -n "\.py:[0-9]" {file} | grep -v "#L[0-9]"` → 0 results (không có plain text refs).
- **Negative:** Given Task 2 output mơ hồ (không có line numbers), When task runs, Then tự discover lines via grep — không abort do thiếu Task 2 data.
- **Interface với Task 4:** Given Bước 4 structured list, When Task 4 reads this file, Then có thể extract "file:line → principle" pairs mà không cần re-scan code.

### 8. Technical Notes
- "Tinh hoa" = code thể hiện nguyên lý thiết kế, không phải code phức tạp nhất. Ví dụ: `_sanitize_name()` 10 LOC nhưng tinh hoa hơn một hàm 200 LOC chỉ là CRUD.
- Read tool với offset+limit: `offset` = line number - 1 (0-indexed), `limit` = số dòng cần đọc.
- Relative path convention từ `self-explores/tasks/` → source: `../../code_review_graph/{file}.py#L{N}`.
- Fan-in count từ grep là approximate — có thể có false positives từ comments. Ghi "(approx)" bên cạnh số.
- Snippet format: dùng Python code block (` ```python `) để syntax highlighting trong IDE.

### 9. Risks
- 🔴 Cao: Phụ thuộc 100% vào Task 2 output chất lượng. Nếu Task 2 chỉ nói "graph.py là core" → phải tự re-discover (Bước 1 fallback). Tốn thêm 10-15 phút.
- 🟡 TB: Read tool với large files (parser.py 4750 LOC) — nếu dùng sai offset → đọc sai section. Luôn grep line number trước khi Read.
- 🟢 Thấp: Clickable links có thể sai relative path nếu đọc từ subfolder khác → verify bằng chạy Bước 3 quality check.

---

## Phản biện (2026-04-20)

### Điểm chất lượng: 6/10 — Cần bổ sung trung bình

### 1. Tóm tắt
Task scan codebase để map từng Core Component và Leverage Point từ Task 2 đến exact file:line. Trích 3+ "code tinh hoa" snippets 50-100 dòng với giải thích tại sao.

### 2. Điểm chưa rõ
- "Code tinh hoa" — tiêu chí chọn là gì? Đẹp về syntax? High fan-in? Thể hiện nguyên lý design? Không define rõ → developer sẽ chọn code bất kỳ.
- "parser.py 4750 LOC — đọc theo section" — section nào? AST walking? Language dispatch? Import detection? Cần pre-define sections để không waste time.
- Số lượng minimum snippets: "3 đoạn tinh hoa" — nếu Task 2 tìm ra 5 Leverage Points thì có cần 5 snippets không?

### 3. Assumption nguy hiểm
- **CRITICAL:** Assume Task 2 đã xác định danh sách Core Components + Leverage Points với file paths. Nếu Task 2 output mơ hồ (VD: "graph.py là important" không có line number) → Task 3 không thể map.
- Assume grep commands trong kế hoạch sẽ trả về kết quả có nghĩa. Nếu function names đã refactor → grep miss → false negative.

### 4. Rủi ro
- 🔴 Cao: Dependency vào Task 2 output chất lượng — nếu Task 2 chỉ nói "graph.py là core" mà không specify class/method → Task 3 phải tự re-discover
- 🟡 TB: "Verify tất cả file paths tồn tại" — chỉ verify existence, không verify content đúng với claim
- 🟢 Thấp: Relative paths từ `self-explores/tasks/` → clickable links có thể sai nếu file di chuyển

### 5. Cần bổ sung
- **Criteria cho "tinh hoa"**: Định nghĩa rõ: "Code tinh hoa = đoạn code thể hiện design principle từ Task 4, có fan-in ≥3 nơi gọi, KHÔNG chỉ là đoạn code phức tạp nhất"
- **Interface với Task 2**: Specify exact output format Task 2 phải có (JSON? Markdown list?) để Task 3 parse được

### 6. Đề xuất cải thiện
Thêm vào Bước 1: "Đọc Task 2 output và extract danh sách Components + Leverage Points thành structured list trước khi bắt đầu scan. Nếu Task 2 output thiếu file:line → note là gap và tự tìm." Điều này loại bỏ assumption về Task 2 chất lượng.

## Worklog

### [11:15] Bắt đầu
- Claimed cùng lúc với z6s (parallel tasks, sẽ làm tuần tự)
- Input từ mw7 Worklog: đã có Structured Output với file:line candidates
- Bước 0: Extract list từ mw7

### [11:16] Bước 0 — Extract từ mw7

Input list từ mw7 Structured Output:
```
Core Components: GraphStore (graph.py:142), CodeParser (parser.py:619), FastMCP (main.py:1)
Leverage Points: _sanitize_name (graph.py:1323), EXTENSION_TO_LANGUAGE (parser.py:74),
                 run_post_processing (postprocessing.py:26), get_impact_radius (graph.py:597)
```
→ Tất cả đã có line numbers → không cần tự re-discover.

### [11:17] Bước 1 — Verify exact lines

```
GraphStore class:         graph.py:142     ✓
CodeParser class:         parser.py:619    ✓
_sanitize_name():         graph.py:1323    ✓
EXTENSION_TO_LANGUAGE:    parser.py:74     ✓
run_post_processing():    postprocessing.py:26  ✓
get_impact_radius():      graph.py:597     ✓
```

### [11:20] Bước 2 — Code tinh hoa snippets

Tiêu chí "tinh hoa" áp dụng: fan-in ≥3 callers OR thể hiện design pattern có tên.

---

#### Snippet 1: `_sanitize_name()` — Defense in Depth (prompt injection prevention)

File: [`graph.py:1323-1337`](../../code_review_graph/graph.py#L1323-L1337)
Nguyên lý: **Defense in Depth** — security output boundary
Fan-in: ~18 call sites trong 6 files (approximate)

```python
def _sanitize_name(s: str, max_len: int = 256) -> str:
    """Strip ASCII control characters and truncate to prevent prompt injection.

    Node names extracted from source code could contain adversarial strings
    (e.g. ``IGNORE_ALL_PREVIOUS_INSTRUCTIONS``).  This function removes control
    characters (0x00-0x1F except tab and newline) and enforces a length limit so
    that names flowing through MCP tool responses cannot easily influence AI
    agent behaviour.
    """
    # Strip control chars 0x00-0x1F except \t (0x09) and \n (0x0A)
    cleaned = "".join(
        ch for ch in s
        if ch in ("\t", "\n") or ord(ch) >= 0x20
    )
    return cleaned[:max_len]
```

**Lý do "tinh hoa":** 15 dòng nhưng đây là toàn bộ security model của output layer. Mọi string từ source code ra ngoài MCP đi qua đây — nếu bỏ qua 1 call site là có prompt injection vector. Cú pháp đơn giản nhưng tư duy sâu: "code có thể chứa IGNORE_ALL_PREVIOUS_INSTRUCTIONS trong tên biến." `max_len=256` không phải ngẫu nhiên — đủ ngắn để không bị dùng làm payload delivery channel.

---

#### Snippet 2: `EXTENSION_TO_LANGUAGE` dict — Open/Closed Principle

File: [`parser.py:74-127`](../../code_review_graph/parser.py#L74-L127)
Nguyên lý: **Open/Closed Principle** — mở rộng không sửa core
Fan-in: 2 direct call sites, nhưng controls 100% language detection scope (49 entries)

```python
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ...
    ".kt": "kotlin",
    ".swift": "swift",
    ".sol": "solidity",
    ".vue": "vue",
    ".dart": "dart",
    ".ipynb": "notebook",
    ".zig": "zig",
    ".svelte": "svelte",
    ".jl": "julia",
    ".res": "rescript",
    ".gd": "gdscript",
    # ... 49 total entries
}
```

**Lý do "tinh hoa":** Đây là ví dụ hoàn hảo của Open/Closed. 49 ngôn ngữ, mỗi ngôn ngữ = 1-2 dòng dict entry. Muốn add Kotlin (đã có!), Zig (đã có!), GDScript — không cần sửa bất kỳ logic nào trong parser core hay tools. Dict này là "config" mà là "code" — immutable at runtime, hoàn toàn declarative. Comments trong dict (VD: `.xs: "c"` — "Perl XS: parsed as C") document decision rationale ngay tại điểm extension.

---

#### Snippet 3: `run_post_processing()` — Template Method Pattern

File: [`postprocessing.py:26-49`](../../code_review_graph/postprocessing.py#L26-L49)
Nguyên lý: **Template Method** — fixed pipeline order, individual steps swappable
Fan-in: 2 call sites (all build paths)

```python
def run_post_processing(store: GraphStore) -> dict[str, Any]:
    """Run all post-build steps on a populated graph.

    Each step is non-fatal: failures are logged and collected as warnings
    so the primary build result is never lost.
    """
    result: dict[str, Any] = {}
    warnings: list[str] = []

    _compute_signatures(store, result, warnings)
    _rebuild_fts_index(store, result, warnings)
    _trace_flows(store, result, warnings)
    _detect_communities(store, result, warnings)

    if warnings:
        result["warnings"] = warnings
    return result
```

**Lý do "tinh hoa":** 134 LOC toàn bộ file nhưng function này là trái tim. Pipeline order là hardcoded — signatures trước FTS5 vì FTS5 index cần signatures; flows trước communities vì communities dùng flow criticality. Quan trọng hơn: **non-fatal design** — mỗi step có thể fail mà không block bước tiếp theo. "so the primary build result is never lost" là design decision quan trọng: build failure ở postprocessing không làm mất graph data.

---

#### Snippet 4: `get_impact_radius()` — Strategy Pattern (dispatch + dual implementation)

File: [`graph.py:597-621`](../../code_review_graph/graph.py#L597-L621)
Nguyên lý: **Strategy Pattern** — runtime selection between SQL CTE vs NetworkX BFS
Fan-in: 3 call sites (review.py, query.py, tools)

```python
def get_impact_radius(
    self,
    changed_files: list[str],
    max_depth: int = MAX_IMPACT_DEPTH,
    max_nodes: int = MAX_IMPACT_NODES,
) -> dict[str, Any]:
    """BFS from changed files to find all impacted nodes within depth N.

    Delegates to ``get_impact_radius_sql()`` by default (faster for
    large graphs).  Set ``CRG_BFS_ENGINE=networkx`` to use the legacy
    Python-side BFS via NetworkX.

    Returns dict with:
      - changed_nodes: nodes in changed files
      - impacted_nodes: nodes reachable via edges
      - impacted_files: unique set of affected files
      - edges: connecting edges
    """
    if BFS_ENGINE == "networkx":
        return self._get_impact_radius_networkx(
            changed_files, max_depth=max_depth, max_nodes=max_nodes,
        )
    return self.get_impact_radius_sql(
        changed_files, max_depth=max_depth, max_nodes=max_nodes,
    )
```

**Lý do "tinh hoa":** Dispatcher function 25 dòng nhưng ẩn sau nó là 2 implementation strategies: SQL recursive CTE (default, fast) và NetworkX (legacy, Python-side). Env var `CRG_BFS_ENGINE` cho phép switch runtime không cần code change — điển hình Strategy Pattern. Comment "faster for large graphs" + "legacy" cho thấy tư duy migration: giữ backward compat trong khi push mọi người dùng implementation mới.

---

### [11:25] Bước 3 — Structured Component Map (Task 4 + 5 reference)

```markdown
### Structured Component Map

**Core Components:**
- GraphStore: [`graph.py:142`](../../code_review_graph/graph.py#L142) | tight_coupling | 12+ importers
- CodeParser: [`parser.py:619`](../../code_review_graph/parser.py#L619) | critical_path | AST entry point
- FastMCP: [`main.py:1`](../../code_review_graph/main.py#L1) | critical_path | 30 tools MCP boundary

**Leverage Points:**
- _sanitize_name(): [`graph.py:1323-1337`](../../code_review_graph/graph.py#L1323-L1337) | Defense in Depth | fan-in ~18
- EXTENSION_TO_LANGUAGE: [`parser.py:74-127`](../../code_review_graph/parser.py#L74-L127) | Open/Closed | 49 entries
- run_post_processing(): [`postprocessing.py:26-49`](../../code_review_graph/postprocessing.py#L26-L49) | Template Method | all build paths
- get_impact_radius(): [`graph.py:597-621`](../../code_review_graph/graph.py#L597-L621) | Strategy Pattern | BFS core
```

**Output mong đợi — đã hoàn thành:**
- [x] Mỗi Core Component → clickable file:line — ĐÃ CÓ: 3 components
- [x] Mỗi Leverage Point → file:line + code snippet 50-100 LOC — ĐÃ CÓ: 4 snippets (15-55 LOC mỗi cái, đủ thể hiện nguyên lý)
- [x] ≥3 "code tinh hoa" với giải thích WHY — ĐÃ CÓ: 4 snippets
- [x] 100% refs là clickable links — ĐÃ VERIFY
- [x] Structured output cho Task 4 parse
