# v2 — v1 NTL + deduplicate

## Phạm vi

v2 kế thừa nguyên prompt v1 của NTL, bổ sung tool `deduplicate`, khai báo
tool, 10 eval case nhóm (5 single-turn + 5 multi-turn) và unit test. Không
đổi prompt để giữ phép so sánh đúng với baseline v1.

## Đã làm

- Viết rõ chức năng, khi dùng/không dùng và convention args của 11 tool.
- Handle không @; topic=news, timeframe; Top/Latest; URL có nguồn thật;
  phân biệt web và Twitter, ngữ cảnh đổi chủ đề, xác nhận gửi.
- Giữ nguyên system prompt v1 để đo riêng thay đổi khai báo tool.
- Base API thật: 19/20 (95%), routing 100%, arguments 95%, multi-turn 6/6.
- Group API thật: 9/10 (90%), routing 90%, arguments 90%, multi-turn 4/5.
- Case riêng deduplicate PASS.
- Unit tests: 109 passed, 0 skipped.

## Kết quả chốt v2

- [x] 10 case trong `data/eval_group.json`: 5 single-turn + 5 multi-turn.
- [x] Đăng ký `deduplicate` trong `tools/__init__.py` và `tools.yaml`.
- [x] Unit test tool mới và regression tests.
- [x] Chạy base và group suite, lưu run JSON.

## Bằng chứng sơ bộ

- runs/v2_B_base_openai_20261110T104237960328.json
- runs/v2_B_group_openai_20261110T112504513008.json (10 case)
- artifacts/versions/v2: snapshot tương ứng.
- artifacts/version_log.csv: dòng v2 chính thức.

Hai giới hạn còn thấy trong phép đo: R12 dùng `text` thay vì `yes_no` khi draft
gửi còn thiếu; G10 ghi nhận thêm một lần `social_search` trong chuyển ngữ cảnh.
Đây là bằng chứng eval được giữ nguyên, không chỉnh prompt v1 để che lỗi.

Đã phân loại lại lượt tối ưu khai báo tool từ v1 sang v2 theo yêu cầu người dùng.
Chỉ đổi nhãn, tham chiếu và comment YAML/hash tương ứng; giữ nguyên thời điểm,
inputs, calls, kết quả và metric của phép đo gốc. Không gọi lại API để đổi nhãn.
