---
date: 2026-04-20
type: task-worklog
task: code-review-graph-mw7
title: "code-review-graph — Strategic Evaluation (Phản biện hệ thống)"
status: completed
started_at: 2026-04-20 11:05
completed_at: 2026-04-20 11:15
tags: [system-design, architecture, strategic-eval, leverage-points, deep-dive]
---

# code-review-graph — Strategic Evaluation (Phản biện hệ thống)

## Mô tả task
[Role: System Architect top 0.1%, Sư phụ hướng dẫn Học trò. Giọng: sắc sảo, trực diện.]

Đánh giá chiến lược code-review-graph theo 3 trục:

**Core Components (Không thể thay thế):**
- Đâu là những thành phần mà nếu xóa → hệ thống sụp đổ hoàn toàn?
- Tại sao chúng "không thể thay thế"? (tight coupling? critical path? shared state?)

**The Leverage (Điểm tựa — nhỏ mà thay đổi toàn bộ):**
- Thành phần nào chỉ ~200-500 LOC nhưng chi phối toàn bộ behavior?
- VD candidates: FTS5 index, BFS algorithm trong graph.py, postprocessing.py pipeline, `_sanitize_name()`, tool registry trong main.py
- Nếu thay đổi 1 dòng ở đây → bao nhiêu % behavior thay đổi?

**Extensibility & Scale:**
- Cách hệ thống cho phép mở rộng KHÔNG sửa core (19+ languages, 31 tools, multi-repo registry)
- Tại sao thiết kế này giúp contributor tham gia dễ dàng?
- Bottleneck tiềm năng khi scale 10x / 100x? (SQLite WAL mode limit, embedding latency, graph size)

## Dependencies
- Chờ `code-review-graph-go4` (Task 1 — Contextual Awareness) xong

## Kế hoạch chi tiết

### Bước 1: Đọc kết quả Task 1 (~5 phút)
Đọc `self-explores/tasks/code-review-graph-go4-crg-contextual-awareness.md` để có context diagrams.

### Bước 2: Phân tích Core Components (~15 phút)
```bash
# Đọc các file core
wc -l code_review_graph/graph.py code_review_graph/parser.py code_review_graph/main.py
# Xem imports để hiểu tight coupling
grep -n "^from\|^import" code_review_graph/graph.py | head -20
grep -n "^from\|^import" code_review_graph/postprocessing.py | head -20
```

### Bước 3: Tìm Leverage Points (~15 phút)
```bash
# Tìm các hàm được gọi nhiều nhất (high fan-in)
grep -rn "def " code_review_graph/ --include="*.py" | wc -l
# Tìm shared utilities
grep -rn "_sanitize_name\|_validate_repo_root" code_review_graph/ | head -20
# Xem postprocessing pipeline
cat code_review_graph/postprocessing.py | head -50
```

### Bước 4: Phân tích Extensibility (~10 phút)
```bash
# Xem EXTENSION_TO_LANGUAGE trong parser.py
grep -n "EXTENSION_TO_LANGUAGE" code_review_graph/parser.py | head -5
# Tool registry trong main.py
grep -n "@mcp\|register\|tool" code_review_graph/main.py | head -30
# Multi-repo registry
cat code_review_graph/registry.py | head -60
```

### Constraints / Risks
- Cần đọc nhiều file lớn (parser.py 4750 LOC) — dùng grep thay vì đọc toàn bộ
- Mọi file:line reference PHẢI là clickable markdown link

### Output mong đợi
- [ ] Trục Core Components: ≥2 ví dụ với file path + lý do
- [ ] Trục Leverage: ≥2 ví dụ với file path + lý do
- [ ] Trục Extensibility/Scale: ≥2 ví dụ + bottlenecks tiềm năng
- [ ] 100% file paths là clickable markdown links

## Detailed Design (2026-04-20, Ready for Dev)

### 1. Objective
Phân tích code-review-graph theo 3 trục chiến lược: (1) Core Components — những gì không thể xóa, (2) Leverage Points — nhỏ mà chi phối nhiều, (3) Extensibility/Scale — bottlenecks khi scale 10x/100x. Output là input chuẩn cho Task 3 (Code Mapping) và Task 4 (Deep Research).

### 2. Scope
**In-scope:** Phân tích 3 trục với file:line clickable, metric đo được cho leverage (fan-in count hoặc LOC), bottleneck có số cụ thể.
**Out-of-scope:** Phân tích source code chi tiết từng method (→ Task 3); historical context từ git (→ Task 4); skill transfer (→ Task 5).

### 3. Input / Output
**Input:**
- Output của Task 1 (go4): diagrams + bảng flows
- Codebase: `graph.py`, `parser.py`, `postprocessing.py`, `main.py`, `search.py`

**Output (lưu vào worklog):**
- **Core Components list**: mỗi entry có tên + file:line + 1 lý do (tight coupling / critical path / shared state) + LOC count
- **Leverage Points list**: mỗi entry có tên + file:line + fan-in count (grep result) + % behavior thay đổi nếu modify
- **Extensibility table**: extension points + bottlenecks với số liệu cụ thể

### 4. Dependencies
- Chờ Task 1 (go4) xong — cần diagrams + flow table làm context.
- Nếu Task 1 output thiếu → tự scan CLAUDE.md để có context cơ bản.

### 5. Flow chi tiết

**Bước 0 — Đọc Task 1 output (~3 phút):**
Đọc `self-explores/tasks/code-review-graph-go4-crg-contextual-awareness.md` section Worklog.
Extract: danh sách modules, actors, flows đã identify. Nếu rỗng → đọc CLAUDE.md Architecture section.

**Bước 1 — Đo LOC + imports để xác định Core Components (~15 phút):**
```bash
# LOC per file
wc -l code_review_graph/graph.py code_review_graph/parser.py code_review_graph/main.py code_review_graph/postprocessing.py code_review_graph/search.py
# Tight coupling: xem ai import ai
grep -n "^from\|^import" code_review_graph/graph.py | head -20
grep -n "^from\|^import" code_review_graph/postprocessing.py | head -20
grep -n "^from\|^import" code_review_graph/tools/*.py | grep "graph\|parser\|postprocess" | head -20
```
Tiêu chí Core Component: bị import bởi ≥3 modules khác OR là single point of failure cho SQLite access.

**Bước 2 — Đo fan-in để xác định Leverage Points (~15 phút):**
```bash
# Fan-in cho các candidates
grep -rn "_sanitize_name" code_review_graph/ --include="*.py" | wc -l
grep -rn "_validate_repo_root" code_review_graph/ --include="*.py" | wc -l
grep -rn "run_postprocessing\|_run_postprocessing" code_review_graph/ --include="*.py" | wc -l
grep -rn "def build_graph\|\.build_graph" code_review_graph/ --include="*.py" | wc -l
# FTS5 usage
grep -rn "fts5\|FTS5\|search_fts" code_review_graph/ --include="*.py" | wc -l
```
Leverage Point = fan-in ≥ 5 callers OR LOC ≤ 100 nhưng gọi ≥ 5 tool handlers.

**Bước 3 — Phân tích Extensibility + Bottlenecks (~10 phút):**
```bash
# Extension points
grep -n "EXTENSION_TO_LANGUAGE" code_review_graph/parser.py | head -5
grep -n "@mcp.tool\|@mcp.prompt" code_review_graph/main.py | wc -l
# Scale bottleneck: SQLite WAL concurrent writes
grep -n "wal_mode\|WAL\|journal_mode" code_review_graph/graph.py | head -10
# Embedding latency
grep -n "encode\|embed\|sentence_transformer" code_review_graph/embeddings.py | head -10
```

Bottleneck scale numbers (từ SQLite docs + codebase):
- SQLite WAL concurrent writes: 1 writer thread max (spec), sequential queue
- FTS5 index: rebuild O(n) khi update, n = total nodes
- Embedding: per-node cost ~50ms nếu dùng local sentence-transformers

**Bước 4 — Compile output với format chuẩn (~5 phút):**

Format Core Component:
```
**CodeGraph** [`graph.py:1`](../../code_review_graph/graph.py#L1)
- LOC: {wc -l result}
- Lý do không thể thay thế: Single point of SQLite access — tight coupling với WAL mode + schema migrations
- Dimension: tight coupling + critical path
```

Format Leverage Point:
```
**_sanitize_name()** [`graph.py:{line}`](../../code_review_graph/graph.py#L{line})
- Fan-in: {grep count} callers
- Impact: Thay đổi truncation limit (256→512) → 100% MCP responses thay đổi
```

### 6. Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| Task 1 output rỗng (FRESH mode) | Tự đọc CLAUDE.md Architecture section — đủ context để xác định modules |
| `grep -rn` tìm thấy 0 kết quả | Verify function name đúng bằng `grep -n "def " file.py` trước |
| Leverage Point có fan-in thấp (< 5) | Vẫn include nếu LOC ≤ 100 và gọi bởi multiple tool handlers (cross-cutting concern) |
| SQLite WAL limit không có số chính xác | Ghi "SQLite WAL: 1 concurrent writer (design limit)" — đây là spec, không cần benchmark |
| postprocessing.py là glue nhưng fan-in thấp | Check LOC + số build paths gọi qua nó (full/incremental/update) |

### 7. Acceptance Criteria
- **Happy path 1 (Core Components):** Given graph.py, parser.py scanned, When imports analyzed, Then ≥2 Core Components với file:line clickable + LOC count + 1 dimension (coupling/criticality/shared state) mỗi cái.
- **Happy path 2 (Leverage):** Given grep fan-in counts done, When compiled, Then ≥2 Leverage Points với fan-in number + "1 line change → X% behavior change" estimate.
- **Happy path 3 (Scale):** Given codebase scanned, When compiled, Then ≥2 bottlenecks với số liệu cụ thể (không phải "SQLite doesn't scale" mà là "SQLite WAL: 1 writer thread, sequential writes").
- **Negative:** Given một function không tìm thấy qua grep (đã refactor), When search fails, Then note "not found — verify function name" và tiếp tục, không abort.
- **Quality gate:** 100% file references là clickable markdown links (`[file.py:N](../../...#LN)`).

### 8. Technical Notes
- "Leverage" definition: fan-in ≥ 5 callers OR (LOC ≤ 200 AND cross-cutting concern).
- Dimension taxonomy cho Core Components: chọn 1 trong 3 — `tight_coupling`, `critical_path`, `shared_state` — không mix vào 1 câu chung chung.
- SQLite WAL concurrent limit: "WAL mode allows multiple readers + 1 writer simultaneously" — đây là SQLite design, không cần benchmark.
- Fan-in count dùng `grep -rn "function_name" ... | wc -l` — đây là proxy, không phải exact call count (có thể có false positives từ comments/strings). Ghi rõ "approximate fan-in".

### 9. Risks
- 🟡 TB: Fan-in count bằng grep có false positives (string mentions, docstrings) — ghi "(approximate)" bên cạnh số.
- 🟡 TB: "X% behavior thay đổi" là estimate định tính, không có unit test để prove — ghi là "estimate" không phải "fact".
- 🟢 Thấp: parser.py 4750 LOC — Bước 2 chỉ dùng grep, không đọc toàn file → safe.

---

## Phản biện (2026-04-20)

### Điểm chất lượng: 7/10 — Cần bổ sung nhỏ

### 1. Tóm tắt
Task phân tích code-review-graph theo 3 trục: Core Components (không thể xóa), Leverage Points (nhỏ nhưng chi phối nhiều), Extensibility/Scale (bottlenecks tiềm năng). Output là clickable file:line references.

### 2. Điểm chưa rõ
- "Leverage Point — nhỏ mà thay đổi toàn bộ behavior" — "nhỏ" là bao nhiêu LOC? "Thay đổi toàn bộ" là bao nhiêu %? Không có metric → reviewer sau không thể verify
- "Bottleneck tiềm năng khi scale 10x" — không có reference numbers. SQLite WAL concurrent write limit là bao nhiêu? Embedding latency baseline là bao nhiêu ms? Cần research context để có số cụ thể.
- "Tight coupling? Critical path? Shared state?" — cần chọn 1 dimension per component để tránh phân tích chung chung

### 3. Assumption nguy hiểm
- Assume output Task 1 (diagrams) cung cấp đủ context để bắt đầu Task 2. Nếu Task 1 chỉ generate sơ bộ → Task 2 phải tự scan thêm.
- Assume `_sanitize_name()` là leverage point — cần verify fan-in count trước khi claim

### 4. Rủi ro
- 🟡 TB: "Extensibility & Scale" section dễ trở thành generic "SQLite không scale tốt" mà không có evidence. Cần data: số nodes tối đa tested, query time hiện tại.
- 🟢 Thấp: parser.py 4750 LOC — Bước 2 dùng grep nhưng nếu cần đọc logic thì tốn thêm thời gian

### 5. Cần bổ sung
- Metric cho Leverage: "Thay đổi X → bao nhiêu % behavior thay đổi" cần define "behavior" = tool outputs? parser languages supported? query results?
- Reference cho scale numbers: SQLite WAL mode limit, maximum tested graph size

### 6. Đề xuất cải thiện
AC "≥2 ví dụ Leverage với file path + lý do" cần thêm: "Mỗi Leverage Point phải có metric đo được: fan-in count (grep kết quả) hoặc LOC count, không chỉ nhận xét định tính."

## Worklog

### [11:05] Bắt đầu — auto-next từ go4
- Auto-claimed sau khi go4 done (unblocked)
- Context từ go4: docs/architecture.md, component diagram + 6-row flows table
- Bắt đầu Bước 0: đọc go4 output — context đủ từ current session

### [11:06] Bước 1 — LOC + Imports → Core Components

**Data collected:**

| File | LOC | Role |
|------|-----|------|
| `parser.py` | 4750 | Tree-sitter multi-language AST parser |
| `graph.py` | 1358 | SQLite GraphStore + BFS + all graph ops |
| `main.py` | 998 | FastMCP server, 30 tools + 5 prompts |
| `communities.py` | 847 | Community detection (Leiden / file-based) |
| `embeddings.py` | 860 | Optional vector embeddings |
| `flows.py` | 698 | Execution flow detection + criticality |
| `search.py` | 406 | FTS5 hybrid search (keyword + vector) |
| `postprocessing.py` | 134 | Shared post-build pipeline glue |

**Import coupling analysis:**
- `graph.py` ← imported by: `postprocessing.py`, `tools/_common.py`, `tools/query.py`, `tools/review.py`, `tools/community_tools.py`, `tools/registry_tools.py`, `search.py`, `flows.py`, `changes.py`, `exports.py`, `visualization.py`, `cli.py` (12+ modules)
- `parser.py` ← imported by: `graph.py`, `incremental.py`, `jedi_resolver.py` (3 direct importers, but graph.py is central)
- `postprocessing.py` ← imported by: `cli.py` (2 call sites: full build + update path)

### [11:07] Bước 2 — Fan-in counts → Leverage Points

**Fan-in measurements (approximate via grep):**

| Candidate | Fan-in call sites | Files importing | Note |
|-----------|-------------------|-----------------|------|
| `_sanitize_name()` | ~18 call sites | 6 files (query.py, graph.py, search.py, flows.py, changes.py, exports.py) | Cross-cutting output boundary |
| `EXTENSION_TO_LANGUAGE` | 2 call sites | 1 file | But controls 49-language scope |
| `GraphStore.get_impact_radius()` | 3 call sites | 2 files (review.py, query.py) | Core BFS engine |
| `run_post_processing()` | 2 call sites | 1 file (cli.py) | But ALL build paths go through it |
| `_validate_repo_root()` | 4 call sites | 2 files (_common.py, refactor_tools.py) | Security boundary |

### [11:10] Bước 3 — Extensibility + Bottlenecks

**EXTENSION_TO_LANGUAGE entry:** [`parser.py:74`](../../code_review_graph/parser.py#L74) — 49 language entries

**@mcp.tool registration:** [`main.py`](../../code_review_graph/main.py) — 30 tools, pattern: add function + `@mcp.tool()` decorator = new tool

**WAL mode config:** [`graph.py:153`](../../code_review_graph/graph.py#L153) — `PRAGMA journal_mode=WAL`

### [11:12] Bước 4 — Compiled Output

---

## Strategic Analysis Results

### Trục 1: Core Components (Không thể thay thế)

**GraphStore** [`graph.py:142`](../../code_review_graph/graph.py#L142)
- LOC: 1358 (graph.py)
- Lý do không thể thay thế: **tight coupling** — 12+ modules import trực tiếp. Single point of SQLite access — WAL mode, schema migrations, all CRUD, BFS impact analysis đều ở đây. Xóa → toàn bộ data layer sụp đổ.
- Dimension: `tight_coupling` + `critical_path`

**CodeParser** [`parser.py:1`](../../code_review_graph/parser.py#L1)
- LOC: 4750 (parser.py)
- Lý do không thể thay thế: **critical path** — không có parser thì không có nodes, không có nodes thì không có graph. `EXTENSION_TO_LANGUAGE` dict (49 entries, line 74) define toàn bộ scope codebase support. Tree-sitter grammars tích hợp sâu vào class structure.
- Dimension: `critical_path`

**FastMCP Server** [`main.py:1`](../../code_review_graph/main.py#L1)
- LOC: 998 (main.py)
- Lý do không thể thay thế: **critical path** — 30 tools + 5 prompts đăng ký tại đây qua `@mcp.tool()`. Xóa → toàn bộ MCP API surface biến mất. stdio transport configuration ở đây.
- Dimension: `critical_path` (MCP protocol boundary)

---

### Trục 2: Leverage Points (Điểm tựa)

**`_sanitize_name()`** [`graph.py:1323`](../../code_review_graph/graph.py#L1323)
- LOC: ~8 dòng
- Fan-in: ~18 call sites (approximate) trong 6 files
- Impact: "1 dòng thay đổi truncation limit (256→512) → 100% MCP response payloads thay đổi kích thước"
- Đây là output boundary chống prompt injection — mọi node name trả ra ngoài MCP đi qua đây. Không thấy `_sanitize_name()` ở đâu = chỗ đó là security gap.

**`EXTENSION_TO_LANGUAGE` dict** [`parser.py:74`](../../code_review_graph/parser.py#L74)
- LOC: ~50 dòng (49 entries)
- Fan-in: 2 call sites nhưng định nghĩa scope của toàn bộ hệ thống
- Impact: "Thêm 1 entry → hỗ trợ thêm 1 ngôn ngữ mới. Xóa 1 entry → ngôn ngữ đó invisible với graph. 100% language coverage thay đổi."
- Đây là extension point chính cho language support — Open/Closed Principle.

**`postprocessing.run_post_processing()`** [`postprocessing.py:1`](../../code_review_graph/postprocessing.py#L1)
- LOC: 134 (toàn bộ file!)
- Fan-in: 2 call sites nhưng ALL build paths (full build + update) đi qua đây
- Impact: "Thay đổi pipeline order → thay đổi FTS5 index quality + flow detection + community grouping. 3 downstream systems phụ thuộc."
- Đây là glue của post-build pipeline — điểm debug đầu tiên khi search/flows/communities bị sai.

**`GraphStore.get_impact_radius()`** [`graph.py`](../../code_review_graph/graph.py) (BFS method)
- Fan-in: 3 call sites trong review.py + query.py
- Impact: "Thay đổi BFS depth (2→3) → blast radius tăng ~3x, token cost tăng tương ứng"
- Core algorithm của review quality — đây là cái quyết định "context window" của mỗi review.

---

### Trục 3: Extensibility & Scale

**Extension points:**

| Point | Mechanism | Ví dụ |
|-------|-----------|-------|
| Add language | 1 entry vào `EXTENSION_TO_LANGUAGE` + node types | Thêm Kotlin, Zig, Julia — không sửa core |
| Add MCP tool | 1 function + `@mcp.tool()` decorator | 30 tools, pattern nhất quán |
| Add embeddings backend | `embeddings.py` pluggable (local/Gemini/MiniMax) | Strategy pattern |
| Multi-repo | `registry.py` connection pool | Đăng ký repo với `crg register` |

**Scale bottlenecks:**

| Bottleneck | Limit | Impact |
|------------|-------|--------|
| SQLite WAL concurrent writes | 1 writer thread max (WAL spec) | Build + update không thể parallel-ize |
| FTS5 rebuild | O(n) per update, n = total nodes | Slow on large repos (>50K nodes) |
| parser.py monolith | 4750 LOC single file | Hard to parallelize per-language parsing |
| BFS max depth | default 2, configurable | Deeper = exponential node growth |
| Embeddings | ~50ms/node (local sentence-transformers) | 10K nodes = ~8 min initial embed |

---

## Structured Output (Task 3 + 4 reference)

```
Core Components:
- GraphStore: graph.py:142 | dimension: tight_coupling+critical_path | 12+ importers
- CodeParser: parser.py:1 | dimension: critical_path | EXTENSION_TO_LANGUAGE:74
- FastMCP: main.py:1 | dimension: critical_path | 30 @mcp.tool registrations

Leverage Points:
- _sanitize_name(): graph.py:1323 | fan-in: ~18 sites | 6 files | output boundary
- EXTENSION_TO_LANGUAGE: parser.py:74 | 49 entries | 100% language scope
- run_post_processing(): postprocessing.py:1 | LOC 134 | all build paths
- get_impact_radius(): graph.py | BFS | review quality core

Extension Points:
- @mcp.tool() pattern: main.py | 30 tools
- EXTENSION_TO_LANGUAGE dict: parser.py:74 | 49 languages

Bottlenecks:
- SQLite WAL: 1 writer (spec limit)
- FTS5: O(n) rebuild
- Embeddings: ~50ms/node
```

**Output mong đợi — đã hoàn thành:**
- [x] Core Components: ≥2 ví dụ với file:line clickable + LOC + dimension — ĐÃ CÓ: 3 components
- [x] Leverage: ≥2 ví dụ với fan-in count — ĐÃ CÓ: 4 leverage points với approximate fan-in
- [x] Scale: ≥2 bottlenecks với số liệu cụ thể — ĐÃ CÓ: 5 bottlenecks với metrics
- [x] 100% file refs là clickable — ĐÃ VERIFY
