# v1 — nền NTL dùng để xây v2

Nguồn chính: v1 NTL tại commit 71f235c. Log đo có sẵn thuộc prompt trước đó tại commit 77d11cd; xem V2_BASELINE_SOURCE.md.
Chỉ sửa system_prompt.md so với starter; tool declarations vẫn là bản gốc.

| Bản NTL | Case | Routing | Arguments | Multi-turn |
|---|---:|---:|---:|---:|
| v0 | 13/20 (65%) | 85% | 65% | 4/6 |
| v1 | 20/20 (100%) | 100% | 100% | 6/6 |

NTL dùng gpt-5.4 qua provider tương thích OpenAI. Đây là log được kéo từ branch
NTL, không phải lượt đo mới của máy này. Commit 71f235c bỏ few-shot sau lượt
20/20, nên không gán điểm đó cho prompt mới chưa có log riêng. V2 hiện đo bằng
gpt-5.4 qua OpenAI trực tiếp.

Prompt v1 bỏ đoán thông tin, hỏi clarify khi thiếu URL/tài khoản, hỏi xác nhận
trước gửi, chuẩn hóa query ngắn gọn, handle không @ và ưu tiên sửa ở lượt mới nhất.

Bằng chứng:
- runs/v0_B_base_openai_20261110T100441663938.json
- runs/v1_B_base_openai_20261110T104801876153.json
- artifacts/versions/v1: snapshot bản NTL 71f235c mới nhất.
- artifacts/versions/history/ntl_77d11cd: snapshot khớp run v1 20/20 đã đo.
- artifacts/version_log.csv: các dòng v0/v1 do NTL ghi.
- CHANGELOG.md ở root: ghi chép gốc của NTL.

Các lượt local trước khi đổi nền (v0 70%, v1/v1-tool 75%, v2 sơ bộ 95%) vẫn giữ
trong runs và artifacts/local_history_before_ntl. Không dùng chúng thay baseline
NTL; các nhãn v1-tool cũ được giữ để bảo toàn bằng chứng lịch sử.
V2 kế thừa prompt này, bổ sung tool mới, 10 case nhóm và unit tests theo yêu cầu.
