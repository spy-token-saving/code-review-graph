---
created: 2026-04-20
updated: 2026-04-20
---

# Project Context Index — code-review-graph

Folder này lưu trữ learnings, decisions, và context quan trọng của dự án.
Claude sessions sau sẽ đọc folder này để hiểu bối cảnh.

## Cấu trúc
- `decisions/` — Quyết định quan trọng
- `learnings/` — Kiến thức học được
- `context/` — Bối cảnh dự án
- `daily/` — Nhật ký hàng ngày
- `tasks/` — Context cho từng task (worklog theo task-id)
- `leverage/` — Phân tích đòn bẩy bất đối xứng
- `history/` — Lịch sử tương tác /viec (JSONL, rollover theo ngày)

## Cách sử dụng
- `/viec ghi` — Ghi chép learnings, decisions, context mới
- `/viec doc` — Đọc lại context đã ghi
- `/viec bat-dau` — Nhận task, tạo worklog tự động
- `/viec xong` — Đóng task, auto-capture output
- `/viec review` — Tổng hợp vào daily log

## Recent Updates
*(Sẽ được cập nhật tự động khi có ghi chép mới)*
