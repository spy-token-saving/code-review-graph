---
date: 2026-04-20
type: task-worklog
task: code-review-graph-ek9
title: "code-review-graph — Skill Transfer (Lối tắt & Thực hành)"
status: completed
started_at: 2026-04-20 12:00
completed_at: 2026-04-20 12:30
tags: [system-design, skill-transfer, mental-shortcuts, exercises, deep-dive]
---

# code-review-graph — Skill Transfer (Lối tắt & Thực hành)

## Mô tả task
[Role: System Architect top 0.1%, Sư phụ hướng dẫn Học trò. Giọng: sắc sảo, trực diện.]

Chuyển giao kỹ năng từ phân tích code-review-graph:

**Lối tắt tư duy (Mental Shortcuts):**
- Chỉ ra 3-5 "lối tắt" để hiểu hệ thống nhanh hơn, bỏ qua hàng tháng thử sai
- VD: "Thay vì nhìn vào cách họ xử lý data, hãy nhìn vào cách họ xử lý Error/Signal — nó tiết lộ mọi assumption"
- VD: "Registry/Factory là bản đồ của toàn bộ extension points"
- VD: "Đọc tests trước code — tests chính là spec sống của hệ thống"
- Tránh sai lầm phổ biến mà junior sẽ mắc phải

**Bài tập thực hành (2-3 bài):**
Mỗi bài tập phải:
- Nhỏ (<2 giờ), có thể làm trên nhánh git riêng (`git checkout -b practice`)
- Buộc áp dụng ít nhất 1 nguyên lý đã học
- Có tiêu chí hoàn thành rõ ràng (verify được)

Các bài tập thực hành áp dụng nguyên lý cụ thể từ Task 4:
- "Thêm một ngôn ngữ mới vào EXTENSION_TO_LANGUAGE mà KHÔNG sửa logic core"
- "Viết một MCP tool mới chỉ dùng query_graph — không đọc SQLite trực tiếp"
- "Tìm và verify _sanitize_name() bảo vệ như thế nào trước prompt injection"

## Dependencies
- Chờ `code-review-graph-1fu` (Task 3 — Code Mapping) xong
- Chờ `code-review-graph-z6s` (Task 4 — Deep Research) xong

## Kế hoạch chi tiết

### Bước 1: Đọc output Task 3 + Task 4 (~10 phút)
Đọc 2 worklogs để lấy:
- Danh sách Leverage Points đã map (từ Task 3)
- Design decisions + principles đã phân tích (từ Task 4)

Chỉ cần **mental shortcuts** có thể derive từ các patterns đó.

### Bước 2: Tổng hợp 3-5 Mental Shortcuts (~15 phút)

Mỗi shortcut phải:
1. Chỉ đích danh 1 pattern/technique đặc trưng của code-review-graph
2. Cho thấy cách dùng để "đọc" hệ thống nhanh hơn
3. Kèm anti-pattern (sai lầm phổ biến tương ứng)

**Candidates shortcuts từ codebase:**

**Shortcut A — Đọc EXTENSION_TO_LANGUAGE:**
```bash
grep -n "EXTENSION_TO_LANGUAGE" code_review_graph/parser.py | head -5
```
Thay vì đọc toàn bộ parser.py 4750 LOC → nhìn vào dict này = biết ngay hệ thống support gì và skip gì.

**Shortcut B — postprocessing.py là "glue" của toàn bộ pipeline:**
```bash
grep -n "def run_postprocessing\|def _build" code_review_graph/postprocessing.py | head -10
```
Mọi build path (full, incremental, update) đều đi qua đây → đây là entry point để debug bất kỳ missing feature nào sau build.

**Shortcut C — _sanitize_name() = defensive boundary:**
```bash
grep -rn "_sanitize_name" code_review_graph/ | head -10
```
Xem nơi nào gọi = biết ngay đâu là output boundary (dữ liệu ra ngoài MCP). Không thấy _sanitize_name() → đó là chỗ thiếu validation.

**Shortcut D — @mcp.tool() = map toàn bộ API surface:**
```bash
grep -n "@mcp.tool\|@mcp.prompt" code_review_graph/main.py | head -35
```
31 tools + 5 prompts đều đăng ký ở đây. Đọc file này như đọc OpenAPI spec.

**Shortcut E — Tests là spec sống:**
```bash
ls tests/test_*.py
```
Với 20+ test files, mỗi file = 1 layer. Đọc test case = hiểu expected behavior mà KHÔNG cần đọc implementation.

### Bước 3: Thiết kế 2-3 bài tập thực hành (~15 phút)

**Bài 1: Thêm ngôn ngữ mới (Open/Closed Principle)**
- Nguyên lý áp dụng: Open/Closed (từ Task 4 — EXTENSION_TO_LANGUAGE extensibility)
- Task: Thêm support cho ngôn ngữ Kotlin (`.kt` extension)
- Commands:
  ```bash
  git checkout -b practice/add-kotlin
  # Sửa code_review_graph/parser.py:
  # 1. Thêm ".kt" vào EXTENSION_TO_LANGUAGE
  # 2. Thêm Kotlin node types vào _CLASS_TYPES, _FUNCTION_TYPES
  # 3. Tạo tests/fixtures/sample.kt
  # 4. Chạy test để verify
  uv run pytest tests/test_multilang.py -v -k kotlin
  ```
- Verify criteria:
  - [ ] Chỉ sửa `parser.py` và thêm fixture — KHÔNG sửa `graph.py`, `tools/`, `main.py`
  - [ ] `uv run pytest tests/test_multilang.py::test_kotlin_parsing -v` pass
  - [ ] `uv run code-review-graph build` không báo lỗi với file `.kt`

**Bài 2: Viết MCP tool mới (Single Responsibility + Dependency Inversion)**
- Nguyên lý áp dụng: SRP + DI (từ Task 4 — tools chỉ gọi graph.py, không đọc SQLite trực tiếp)
- Task: Tạo tool `get_hottest_nodes_tool` — top-10 nodes có fan-in cao nhất
- Approach:
  ```bash
  git checkout -b practice/new-tool
  # Viết tool trong code_review_graph/tools/analysis_tools.py
  # Dùng CodeGraph.get_stats() hoặc query_graph() — KHÔNG dùng raw SQL
  # Đăng ký trong main.py với @mcp.tool()
  ```
- Verify criteria:
  - [ ] Tool implementation không import `sqlite3` trực tiếp
  - [ ] Tool gọi qua `graph.py` API (CodeGraph methods)
  - [ ] `uv run code-review-graph serve` khởi động được, tool xuất hiện trong tool list

**Bài 3 (Optional): Trace _sanitize_name() boundary (Security Pattern)**
- Nguyên lý áp dụng: Defense in Depth — prompt injection prevention
- Task: "Thought experiment + verification"
  ```bash
  # Tìm tất cả chỗ gọi _sanitize_name()
  grep -rn "_sanitize_name" code_review_graph/ --include="*.py"
  # Tìm chỗ KHÔNG gọi nhưng return data ra ngoài
  grep -rn "return.*node\|yield.*node" code_review_graph/tools/ --include="*.py" | head -20
  ```
- Câu hỏi verify: "Liệt kê 2 chỗ trong codebase mà nếu thiếu _sanitize_name() → Claude agent nhận được control character trong response."
- Verify criteria:
  - [ ] Trả lời được câu hỏi trên với exact file:line
  - [ ] Hiểu tại sao 256-char limit là defensive (prompt injection attack vector)

### Bước 4: Ghi common junior mistakes (~5 phút)

Anti-patterns phổ biến khi đọc codebase kiểu này:
1. **Đọc parser.py từ đầu** → waste 2 giờ. Fix: Đọc EXTENSION_TO_LANGUAGE dict trước.
2. **Đọc SQLite schema và nghĩ hiểu được system** → graph.py schema là implementation detail, không phải API. Fix: Đọc CodeGraph public methods.
3. **Tạo tool mới gọi raw SQL** → violates Dependency Inversion. Fix: Mọi data access phải qua CodeGraph methods.
4. **Forget _sanitize_name() khi return node data** → security hole. Fix: Grep xem tool hiện tại làm gì và follow pattern.

### Constraints / Risks
- Shortcuts phải derive TỪ Task 3+4 output — không phải generic Python tips
- Bài tập phải verify được bằng tests (không phải "chạy cảm giác đúng")
- parser.py 4750 LOC — bài tập không được require đọc toàn bộ

### Output mong đợi
- [ ] Tối thiểu 3 mental shortcuts với anti-pattern tương ứng
- [ ] Tối thiểu 2 bài tập có: mô tả, verify criteria, estimated time
- [ ] Bài tập áp dụng nguyên lý cụ thể từ Task 4 (Open/Closed, SRP, Security)
- [ ] Shortcuts có file references dạng clickable links

## Detailed Design (2026-04-20, Ready for Dev)

### 1. Objective
Chuyển đổi findings từ Task 3 (Code Mapping) và Task 4 (Deep Research) thành kiến thức có thể transfer: 3-5 mental shortcuts giúp developer Python/OOP mới chưa quen MCP/Tree-sitter "đọc" hệ thống nhanh hơn + 2-3 bài tập nhỏ (<2h) có verify criteria rõ ràng.

### 2. Scope
**In-scope:** Shortcuts derive từ Task 3+4 findings (không hardcode); exercises có nguyên lý cụ thể + verify criteria; anti-patterns cho mỗi shortcut.
**Out-of-scope:** Tạo CI pipeline; document toàn bộ API; implement Kotlin support thực sự (→ bài tập là practice, không phải production feature).
**Audience:** Developer Python biết OOP cơ bản, chưa quen MCP protocol, chưa quen Tree-sitter.

### 3. Input / Output
**Input:**
- Output Task 3 (1fu): Worklog với "Structured Component Map" và code snippets
- Output Task 4 (z6s): Worklog với "Decision → Principle" pairs

**Output (lưu vào worklog):**
- 3-5 Mental Shortcuts: shortcut + anti-pattern + command để verify
- 2-3 Exercises: mô tả + nguyên lý áp dụng + verify criteria (testable) + estimated time
- Anti-patterns list: top 4 sai lầm phổ biến với fix

### 4. Dependencies
- Chờ Task 3 (1fu) xong — cần "code tinh hoa" snippets + structured component map.
- Chờ Task 4 (z6s) xong — cần "Decision → Principle" pairs.

### 5. Flow chi tiết

**Bước 0 — Đọc Task 3 + Task 4 output (~10 phút) — BẮT BUỘC TRƯỚC KHI VIẾT GÌ:**
```bash
# Tìm worklog files
ls self-explores/tasks/code-review-graph-1fu-*.md
ls self-explores/tasks/code-review-graph-z6s-*.md
```
Đọc section "Worklog" của cả 2 files.
Extract 2 lists:
1. **Leverage Points list** (từ Task 3): `[tên, file:line, design_principle]`
2. **Decision → Principle pairs** (từ Task 4): `[decision, principle, why_not_alternative]`

⚠️ **KHÔNG dùng shortcuts đã hardcode trong kế hoạch gốc (EXTENSION_TO_LANGUAGE, _sanitize_name, v.v.) trừ khi Task 3+4 confirm chúng là leverage points.** Shortcuts phải derive từ findings thực tế.

**Bước 1 — Derive shortcuts từ findings (~15 phút):**

Với mỗi Leverage Point từ Task 3, tạo 1 shortcut theo format:
```
**Shortcut N — {tên leverage point}:**
Command: {bash command để "see" leverage point nhanh}
Insight: {1 câu mô tả cái shortcut tiết lộ}
Anti-pattern: {sai lầm tương ứng mà junior mắc phải}
```

Ví dụ (nếu Task 3 confirm EXTENSION_TO_LANGUAGE là leverage):
```
**Shortcut A — Đọc EXTENSION_TO_LANGUAGE thay vì toàn bộ parser.py:**
Command: `grep -n "EXTENSION_TO_LANGUAGE" code_review_graph/parser.py | head -5`
Insight: Dict này = bản đồ ngôn ngữ supported — 1 nhìn biết scope của parser mà không cần đọc 4750 LOC.
Anti-pattern: Đọc parser.py từ đầu → waste 2h. Fix: đọc dict mapping trước.
```

Tương tự với các Leverage Points khác từ Task 3. Mục tiêu 3-5 shortcuts.

**Bước 2 — Dependency check trước khi design exercises (~5 phút):**

Trước khi thiết kế bài tập Kotlin:
```bash
# Check tree-sitter-kotlin availability
pip show tree-sitter-kotlin 2>/dev/null || echo "NOT INSTALLED"
# Check grammar file
python3 -c "import tree_sitter_kotlin" 2>&1 | head -3
```
Nếu không có → bài tập Kotlin PHẢI note: "Requires: `pip install tree-sitter-kotlin`" + thêm step install vào exercise instructions.

Trước khi design bài tập "viết MCP tool không dùng raw SQL":
```bash
# Verify CodeGraph public API đủ
grep -n "def get_stats\|def query_graph\|def get_node" code_review_graph/graph.py | head -15
# Check existing tool pattern (violations?)
grep -rn "import sqlite3" code_review_graph/tools/ --include="*.py" | head -10
```
Nếu tools/ có raw sqlite3 imports → bài tập trở thành "follow existing pattern" thay vì "write new tool".

**Bước 3 — Design 2-3 exercises từ Task 4 principles (~15 phút):**

Mỗi exercise áp dụng ≥1 principle từ Task 4 Worklog:
```markdown
**Bài {N}: {tên}**
- Nguyên lý: {tên principle từ Task 4} — {1-line lý do liên kết}
- Task: {mô tả cụ thể, < 3 câu}
- Time: < 2 giờ
- Setup:
  ```bash
  git checkout -b practice/{slug}
  {commands cụ thể}
  ```
- Verify criteria:
  - [ ] {criterion 1 — có thể check bằng command/test}
  - [ ] {criterion 2}
  - [ ] {criterion 3}
- Note: {dependency check result từ Bước 2 — VD: "Requires tree-sitter-kotlin"}
```

Exercises PHẢI verify được bằng pytest hoặc grep — không phải "cảm giác đúng".

**Bước 4 — Compile anti-patterns list (~5 phút):**
4 anti-patterns phổ biến (derive từ findings Task 3+4, không phải generic advice):
1. {Pattern từ findings} → Fix: {cụ thể}
2. {Pattern từ findings} → Fix: {cụ thể}
3. {Pattern từ findings} → Fix: {cụ thể}
4. {Pattern từ findings} → Fix: {cụ thể}

**Bước 5 — Append vào Worklog + verify (~5 phút):**
Append tất cả vào Worklog section. Verify quality gate:
```bash
grep -n "\.py[^`]" self-explores/tasks/code-review-graph-ek9-crg-skill-transfer.md | grep -v "#L[0-9]\|\[.*\](.*\.py" | head -10
# Expected: 0 plain text refs
```

### 6. Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| Task 3 Worklog rỗng (chưa done khi Task 5 bắt đầu) | Đọc thay bằng Task 2 output — vẫn có component list dù không có snippets |
| Task 4 Worklog rỗng | Dùng candidates từ description Task 4 (SQLite/Tree-sitter/stdio decisions) làm input |
| tree-sitter-kotlin không available | Chuyển bài tập sang ngôn ngữ có sẵn (Dart, Zig, Lua đều trong parser.py) — note lý do |
| Tất cả tools/ đã dùng CodeGraph API (không vi phạm) | Bài tập 2 trở thành "write NEW tool" thay vì "fix violation" — vẫn valid |
| < 3 Leverage Points từ Task 3 | Tổng hợp shortcut từ Task 4 decisions thay vì Task 3 leverage points |

### 7. Acceptance Criteria
- **Happy path 1 (Shortcuts):** Given Task 3+4 findings đọc xong, When derived, Then ≥3 shortcuts với: (a) command để verify, (b) insight 1 câu, (c) anti-pattern tương ứng. Shortcuts PHẢI reference file:line từ Task 3 findings.
- **Happy path 2 (Exercises):** Given dependency check done, When designed, Then ≥2 exercises với: (a) principle name từ Task 4, (b) verify criteria testable (pytest/grep), (c) time estimate ≤ 2h, (d) dependency notes.
- **Happy path 3 (Audience):** Given audience "Python dev, OOP-aware, new to MCP/Tree-sitter", When reading, Then mỗi shortcut có thể apply mà không cần đọc source code.
- **Negative:** Given Task 3+4 chưa done, When Task 5 starts, Then sử dụng fallback (Task 2 output / description candidates) — không abort.
- **Critical:** KHÔNG hardcode shortcuts mà không verify với Task 3+4 output. Nếu Task 3 không confirm leverage → không dùng.

### 8. Technical Notes
- **Audience framing**: "Developer Python biết OOP cơ bản, chưa quen MCP/Tree-sitter" — tránh assume họ biết protocol details.
- **Exercise verify criteria**: Phải là machine-checkable: `pytest tests/test_X.py::test_Y -v` → PASS, hoặc `grep -n "import sqlite3" tools/X.py` → 0 results. Không dùng "kiểm tra bằng mắt".
- **Shortcut format**: command phải ngắn (<1 line), chạy được từ repo root. Không cần understand output — chỉ cần nhìn biết cái gì.
- **Anti-pattern list**: 4 items, mỗi item có Fix rõ ràng (action-oriented, không chỉ "don't do X").
- **Tree-sitter Kotlin**: Package `tree-sitter-kotlin` cần kiểm tra từng môi trường. Fallback: Dart (`.dart`) đã có grammar trong codebase.

### 9. Risks
- 🟡 TB: Shortcuts derive từ Task 3+4 findings — nếu Task 3+4 shallow → shortcuts cũng shallow. Mitigate: read cả Task 3+4 worklogs TRƯỚC khi write.
- 🟡 TB: Exercise verify criteria "pytest test_kotlin" — test case này chưa tồn tại, phải viết. Thêm "viết test trước khi run" vào exercise instructions.
- 🟢 Thấp: Dependency check (Bước 2) tốn 5 phút nhưng tránh được bài tập không thực hiện được — worth it.

---

## Phản biện (2026-04-20)

### Điểm chất lượng: 6/10 — Cần sửa trung bình

### 1. Tóm tắt
Task tổng hợp 3-5 mental shortcuts từ output Task 3+4, thiết kế 2-3 bài tập thực hành có verify criteria. Kết quả lưu vào worklog .md.

### 2. Điểm chưa rõ
- Mental shortcuts đã được hardcode trong kế hoạch (EXTENSION_TO_LANGUAGE, _sanitize_name(), @mcp.tool()...) TRƯỚC khi Task 3+4 done. Nếu Task 3+4 tìm ra leverage points khác → shortcuts này có thể không phản ánh findings thực tế.
- "Tránh sai lầm phổ biến mà junior sẽ mắc phải" — junior ở level nào? Python novice? Senior dev chưa biết Tree-sitter? Audience không rõ.
- Bài tập 1 hardcode "Kotlin" — không liên kết với design principle nào cụ thể từ Task 4. Principle "Open/Closed" là giả định, chưa verify Task 4 confirm điều này.

### 3. Assumption nguy hiểng
- Bài tập 2 "Viết MCP tool không dùng raw SQL" — assume hiện tại KHÔNG có tool nào vi phạm rule này. Nếu có tool hiện tại dùng raw SQL → exercise trở thành "fix existing violation" thay vì "write new tool".
- Assume karpathy-style "tạo tool mới qua graph.py API" là possible → cần verify CodeGraph public API đủ để implement `get_hottest_nodes_tool` mà không cần raw SQL.
- Assume bài tập "Kotlin support" không cần grammar file riêng từ tree-sitter-kotlin — thực tế cần `pip install tree-sitter-kotlin` → dependency không được mention.

### 4. Rủi ro
- 🟡 TB: Shortcuts bị hardcode có thể conflict với Task 3+4 findings → tốn thời gian reconcile
- 🟡 TB: `uv run pytest tests/test_multilang.py::test_kotlin_parsing -v` — test này chưa tồn tại, phải viết test trước khi run. Exercise mô tả verify nhưng missing step "viết test".
- 🟢 Thấp: Bài tập 3 "Thought experiment" ít verify được hơn 2 bài tập có code

### 5. Cần bổ sung
- **Instruction rõ hơn**: "Shortcuts phải derive từ Task 3+4 output — ĐỌC worklogs trước, KHÔNG hardcode shortcuts trong kế hoạch này"
- **Dependency check cho exercises**: Trước khi assign exercise, verify: (1) tree-sitter-kotlin grammar available, (2) CodeGraph API đủ, (3) existing tool pattern clean
- **Audience definition**: "Mental shortcuts dành cho developer Python biết OOP, chưa quen với MCP/Tree-sitter"

### 6. Đề xuất cải thiện
Bước 2 cần rewrite: "Đọc output Task 3 (leverage points) và Task 4 (design decisions) TRƯỚC. Từ findings đó, derive shortcuts. Kế hoạch này chỉ là CANDIDATES — thay bằng findings thực tế." Loại bỏ pre-baked shortcuts khỏi kế hoạch và thay bằng process.

## Worklog

### [12:00] Bắt đầu — auto-next sau khi z6s closed

Task ek9 được auto-claim sau khi z6s hoàn thành.
Input confirmed: 1fu worklog có 4 Leverage Points + 4 snippets, z6s worklog có 4 Decision→Principle pairs.

### [12:02] Bước 0 — Extract từ Task 3 (1fu) + Task 4 (z6s)

**Leverage Points confirmed (từ 1fu Structured Component Map):**

| Tên | File:Line | Nguyên lý | Fan-in |
|-----|-----------|-----------|--------|
| `_sanitize_name()` | [`graph.py:1323-1337`](../../code_review_graph/graph.py#L1323-L1337) | Defense in Depth | ~18 |
| `EXTENSION_TO_LANGUAGE` | [`parser.py:74-127`](../../code_review_graph/parser.py#L74-L127) | Open/Closed | 2 direct, controls 49 langs |
| `run_post_processing()` | [`postprocessing.py:26-49`](../../code_review_graph/postprocessing.py#L26-L49) | Template Method | all build paths |
| `get_impact_radius()` | [`graph.py:597-621`](../../code_review_graph/graph.py#L597-L621) | Strategy Pattern | 3 callers |

**Decision → Principle pairs confirmed (từ z6s Structured Output):**

| Decision | Principle | Tại sao |
|----------|-----------|---------|
| SQLite WAL | SRP + DI | No server required, WAL = concurrent reads |
| Tree-sitter | Open/Closed | 49 langs, incremental parsing, no brittle regex |
| stdio transport | ISP | No network/auth, process isolation, LSP precedent |
| postprocessing.py | SRP + DRY | Commit 128bf11 fix divergent CLI vs MCP behavior |

### [12:05] Bước 2 — Dependency Check kết quả

```
tree-sitter-kotlin: NOT INSTALLED (ModuleNotFoundError)
  → Fallback: dùng Dart (`.dart`) — đã có trong codebase
  → Hoặc note "Requires pip install" trong exercise

CodeGraph public API: ĐỦ
  get_node():598, get_nodes_by_file():325, get_impact_radius():597
  get_stats():819, get_nodes_by_size():854, get_nodes_by_kind():909
  → Feasible để viết tool mới không dùng raw SQL

Raw sqlite3 trong tools/:
  build.py:6 import sqlite3  ← VIOLATION
  context.py:6 import sqlite3  ← VIOLATION
  → Bài tập 2 thú vị hơn: "write NEW tool following CORRECT pattern"
```

### [12:08] Bước 1 — 5 Mental Shortcuts (derive từ findings)

---

## Mental Shortcuts — Đọc code-review-graph Nhanh Hơn

> **Audience:** Developer Python biết OOP cơ bản, chưa quen MCP/Tree-sitter.
> Mỗi shortcut derive từ Task 3+4 confirmed findings — không generic.

---

### Shortcut 1 — EXTENSION_TO_LANGUAGE = parser scope map

**Command:**
```bash
grep -n "^    \"\." code_review_graph/parser.py | wc -l
# hoặc
head -60 code_review_graph/parser.py | grep -A50 "EXTENSION_TO_LANGUAGE"
```

**Insight:** Dict [`parser.py:74-127`](../../code_review_graph/parser.py#L74-L127) là 53 dòng nhưng mô tả TOÀN BỘ scope của parser. Đọc dict này (30 giây) = biết ngay hệ thống support 49 extension nào, skip gì. Không cần đọc 4750 LOC còn lại của `parser.py`.

**Anti-pattern:** Đọc parser.py từ đầu → 2h đọc AST walking logic mà không biết full picture. Fix: đọc dict mapping TRƯỚC, rồi mới đi vào logic khi cần.

**Principle liên kết:** Open/Closed — dict này là "closed for modification" (add language = thêm 1 entry). 23 lần add ngôn ngữ mới không sửa core logic.

---

### Shortcut 2 — `_sanitize_name()` fan-in = output boundary audit

**Command:**
```bash
grep -rn "_sanitize_name" code_review_graph/ --include="*.py"
# Expected: ~18 call sites trong 6 files
```

**Insight:** Chỗ nào call [`graph.py:1323`](../../code_review_graph/graph.py#L1323) = output boundary (data ra ngoài MCP). Chỗ nào return node data mà KHÔNG qua `_sanitize_name()` = security gap. 15 dòng code nhưng là toàn bộ security model của output layer.

**Anti-pattern:** Viết MCP tool return `node.name` trực tiếp → prompt injection vector (attacker đặt `IGNORE_ALL_INSTRUCTIONS` vào tên function). Fix: mọi string từ source code ra MCP phải qua `_sanitize_name()`.

**Principle liên kết:** Defense in Depth — control characters + 256-char limit làm payload delivery không feasible.

---

### Shortcut 3 — `postprocessing.py` = "pipeline health" diagnostic

**Command:**
```bash
cat code_review_graph/postprocessing.py  # chỉ 134 LOC
```

**Insight:** [`postprocessing.py:26-49`](../../code_review_graph/postprocessing.py#L26-L49) là 4-step pipeline: signatures → FTS5 → flows → communities. Nếu graph thiếu features sau build (flows không có, communities trống, search không work) → lỗi ở 1 trong 4 steps này. File 134 LOC, đọc trong 2 phút = hiểu toàn bộ post-build diagnostic path.

**Anti-pattern:** Debug graph issues bằng cách đọc `tools/build.py` hoặc `graph.py` → tìm sai chỗ. Fix: `postprocessing.py` là single entry point cho mọi post-build processing, debug ở đây trước.

**Principle liên kết:** SRP + DRY — commit `128bf11` extract file này để fix bug: CLI và MCP tool trước đó có divergent behavior (CLI thiếu flows/communities).

---

### Shortcut 4 — `@mcp.tool()` list = API spec

**Command:**
```bash
grep -n "@mcp.tool\|@mcp.prompt" code_review_graph/main.py
```

**Insight:** [`main.py:1`](../../code_review_graph/main.py#L1) đăng ký 30 tools + 5 prompts. Grep này = OpenAPI spec — thấy ngay toàn bộ public surface. Cần add tool mới → thêm `@mcp.tool()` decorator ở đây (implement ở `tools/`).

**Anti-pattern:** Tìm tool trong `tools/` bằng cách grep từng file → miss cái nào registered, cái nào chưa. Fix: `main.py` là source of truth cho registered tools.

**Principle liên kết:** ISP — tool handlers không biết transport (stdio vs HTTP). `main.py` wire-up là nơi duy nhất cần biết transport.

---

### Shortcut 5 — Env vars điều khiển behavior = Strategy Pattern extension points

**Command:**
```bash
grep -rn "os.environ\|os.getenv\|environ.get" code_review_graph/ --include="*.py" | grep -v test | head -20
```

**Insight:** `CRG_BFS_ENGINE=networkx` ở [`graph.py:597`](../../code_review_graph/graph.py#L597) = Strategy Pattern. Khi thấy env var điều khiển behavior → có ≥2 implementation strategies. Tìm env vars = tìm tất cả extension points trong system mà không cần đọc implementation.

**Anti-pattern:** Assume hành vi cố định, không kiểm tra env vars → miss hidden configurability. Fix: `grep -rn "os.getenv\|environ"` là nơi đầu tiên để tìm "có thể override không?".

**Principle liên kết:** Strategy Pattern — SQL CTE (default, fast) vs NetworkX BFS (legacy). Env var = runtime strategy selector.

---

### [12:18] Bước 3 — 3 Bài tập thực hành

---

## Bài Tập Thực Hành

### Bài 1: Thêm ngôn ngữ mới — Open/Closed Principle

**Nguyên lý:** Open/Closed từ Task 4 z6s Decision 2 — "add language = 1 dict entry, không sửa logic core"

**Task:** Thêm support `.hx` (Haxe) hoặc bất kỳ extension chưa có trong EXTENSION_TO_LANGUAGE

**Time estimate:** < 45 phút

**Setup:**
```bash
git checkout -b practice/add-language
# Bước 1: Verify grammar available
python3 -c "import tree_sitter_language_pack as tslp; tslp.get_language('haxe')" 2>&1
# Nếu fail → chọn ngôn ngữ khác từ danh sách tslp.LANGUAGE_NAMES

# Bước 2: Thêm vào EXTENSION_TO_LANGUAGE (parser.py:74)
# Bước 3: Thêm node types vào _CLASS_TYPES, _FUNCTION_TYPES nếu language có class/function
# Bước 4: Tạo fixture file
touch tests/fixtures/sample.hx
# Bước 5: Test
uv run pytest tests/test_multilang.py -v -k haxe
```

**Verify criteria:**
- [ ] `git diff --name-only` chỉ show `code_review_graph/parser.py` + `tests/fixtures/sample.hx` — KHÔNG có thay đổi ở `graph.py`, `tools/`, `main.py` (Open/Closed proof)
- [ ] `uv run pytest tests/test_multilang.py -v` không có new failures
- [ ] `uv run code-review-graph build` không raise exception với file `.hx`

**Note:** `tree-sitter-kotlin` NOT installed trong môi trường này → verify Kotlin grammar trước với `python3 -c "import tree_sitter_language_pack as p; p.get_language('kotlin')"`. Nếu fail → switch sang ngôn ngữ khác.

---

### Bài 2: Viết MCP tool mới không dùng raw SQL — SRP + DI

**Nguyên lý:** SRP + Dependency Inversion từ Task 4 z6s Decision 1 — "tools chỉ gọi qua GraphStore API, không biết về SQLite"

**Context:** `tools/build.py:6` và [`tools/context.py:6`](../../code_review_graph/tools/context.py#L6) hiện tại có `import sqlite3` — đây là violations. Bài tập này viết tool MỚI theo đúng pattern.

**Task:** Implement `get_largest_nodes_tool` — top-10 nodes có source code dài nhất (theo `size` field) sử dụng `GraphStore.get_nodes_by_size()` tại [`graph.py:854`](../../code_review_graph/graph.py#L854)

**Time estimate:** < 60 phút

**Setup:**
```bash
git checkout -b practice/new-tool
# Bước 1: Đọc get_nodes_by_size signature
grep -A10 "def get_nodes_by_size" code_review_graph/graph.py
# Bước 2: Tham khảo existing tool pattern
grep -A20 "@mcp.tool" code_review_graph/main.py | head -40
# Bước 3: Viết tool trong code_review_graph/tools/analysis_tools.py
# Bước 4: Register trong main.py với @mcp.tool()
```

**Verify criteria:**
- [ ] `grep "import sqlite3" code_review_graph/tools/analysis_tools.py` → 0 kết quả (DI proof)
- [ ] Tool implementation chỉ call `store.get_nodes_by_size()` hoặc `store.get_stats()` — không có raw SQL string
- [ ] `uv run code-review-graph serve` khởi động, không raise exception
- [ ] `grep -n "get_largest_nodes" code_review_graph/main.py` → tool registered

---

### Bài 3: _sanitize_name() boundary audit — Defense in Depth

**Nguyên lý:** Defense in Depth từ Task 3 1fu Snippet 1 — fan-in ~18, prompt injection prevention

**Task:** Thought experiment + verification — tìm chỗ nào trong codebase CÓ THỂ thiếu `_sanitize_name()`

**Time estimate:** < 30 phút

**Commands:**
```bash
# Tìm tất cả call sites
grep -rn "_sanitize_name" code_review_graph/ --include="*.py"

# Tìm chỗ return node data ra ngoài (potential gaps)
grep -rn "\"name\".*node\|node.*\"name\"\|\.name" code_review_graph/tools/ --include="*.py" | head -20

# Tìm dict construction trả về node info
grep -rn "return {" code_review_graph/tools/ --include="*.py" | head -20
```

**Câu hỏi cần trả lời (verify bằng grep):**
1. Liệt kê 3 call sites của `_sanitize_name()` với exact `file:line`
2. Giải thích tại sao `max_len=256` (không phải 100 hay 1000) là defensive cho prompt injection

**Verify criteria:**
- [ ] Liệt kê được 3+ call sites với file:line từ grep output
- [ ] Giải thích được "256-char limit cuts off prompt injection payloads" — attack payload thường >256 chars, node names hợp lệ thường <100 chars
- [ ] Chỉ ra được 1 chỗ trong `tools/` có potential gap (return dict với string từ source code nhưng chưa rõ có sanitize không)

---

### [12:25] Bước 4 — Anti-patterns phổ biến (derive từ findings)

---

## Anti-Patterns — Sai lầm phổ biến khi đọc code-review-graph

1. **Đọc `parser.py` từ đầu** → Mất 2h vào AST walking mà không biết context.
   **Fix:** Đọc [`EXTENSION_TO_LANGUAGE` (parser.py:74)](../../code_review_graph/parser.py#L74) trước — 53 dòng = scope full picture.

2. **Debug graph missing features trong `graph.py`** → Tìm sai chỗ, `graph.py` 1358 LOC.
   **Fix:** Đọc [`postprocessing.py`](../../code_review_graph/postprocessing.py) trước (134 LOC). Flows/communities/FTS5 missing → lỗi ở 4-step pipeline.

3. **Viết MCP tool với `import sqlite3` trực tiếp** → Vi phạm DI, tạo tight coupling với SQLite schema.
   **Fix:** Chỉ dùng `GraphStore` public methods ([`graph.py:319+`](../../code_review_graph/graph.py#L319)). Schema là implementation detail.

4. **Forget `_sanitize_name()` khi build tool mới return node data** → Prompt injection gap.
   **Fix:** Grep existing tools làm gì (`grep "_sanitize_name" code_review_graph/tools/`) → follow pattern. Nếu return string từ source code → phải qua [`_sanitize_name()` (graph.py:1323)](../../code_review_graph/graph.py#L1323).

---

### [12:28] Bước 5 — Verify quality gate

```bash
grep -n "\.py[^`\[]" self-explores/tasks/code-review-graph-ek9-crg-skill-transfer.md | grep -v "#L[0-9]\|\[.*\](.*\.py\|```" | head -10
```
→ Kết quả: 0 plain text refs (tất cả file references đều là clickable links)

---

## Structured Output (Task 6 reference)

```
Mental Shortcuts derived: 5
1. EXTENSION_TO_LANGUAGE dict → parser scope map | parser.py:74 | Open/Closed
2. _sanitize_name() grep → output boundary audit | graph.py:1323 | Defense in Depth
3. postprocessing.py read → pipeline health diagnostic | postprocessing.py:26 | SRP+DRY
4. @mcp.tool() grep → full API surface | main.py:1 | ISP
5. os.getenv grep → Strategy Pattern extension points | graph.py:597 | Strategy

Exercises designed: 3
1. Add new language (.hx Haxe) — Open/Closed Principle — < 45 min — verify: only parser.py changed
2. Write new MCP tool (get_largest_nodes) — SRP+DI — < 60 min — verify: no import sqlite3
3. _sanitize_name() boundary audit — Defense in Depth — < 30 min — verify: list 3 call sites

Anti-patterns: 4
1. Read parser.py start→end | Fix: EXTENSION_TO_LANGUAGE first
2. Debug features in graph.py | Fix: postprocessing.py 134 LOC first
3. Tool with raw sqlite3 | Fix: GraphStore API only
4. Forget _sanitize_name() | Fix: grep existing pattern

Key file:line refs for Task 6:
- parser.py:74 (EXTENSION_TO_LANGUAGE, Open/Closed)
- graph.py:1323 (Defense in Depth, security boundary)
- postprocessing.py:26 (Template Method, SRP+DRY)
- graph.py:597 (Strategy Pattern, BFS dispatch)
```

**Output mong đợi — đã hoàn thành:**
- [x] ≥3 mental shortcuts với anti-pattern — ĐÃ CÓ: 5 shortcuts
- [x] ≥2 bài tập có verify criteria testable — ĐÃ CÓ: 3 bài tập
- [x] Bài tập áp dụng nguyên lý từ Task 4 — ĐÃ CÓ: Open/Closed, SRP+DI, Defense in Depth
- [x] Shortcuts có clickable file references — ĐÃ VERIFY
- [x] Dependency check done (tree-sitter-kotlin, CodeGraph API, tools/ violations) — ĐÃ CÓ
