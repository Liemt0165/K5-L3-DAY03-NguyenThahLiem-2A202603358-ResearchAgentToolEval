# Nguồn nền v2

Theo yêu cầu người dùng, bỏ v1 local khỏi luồng chính và dùng v1 của NTL.

- Commit nền cố định: 71f235c166ac58bdfac6ef2030202d1ecaa05584 (V1 prompt).
- Main đã fast-forward tới commit này; prompt v2 giữ nguyên nội dung prompt NTL.
- V2 thêm deduplicate, khai báo tool rõ ràng, 10 eval case và unit tests.
- Model đánh giá/UI hiện tại: gpt-5.4 qua api.openai.com, cấu hình OPENAI_MODEL
  trong .env. Không thay API key hoặc chuyển sang endpoint bên ngoài.

## Bằng chứng v1 NTL

NTL có log v0 13/20 và v1 20/20 tại commit 77d11cd (prompt có few-shot).
Commit 71f235c sau đó bỏ few-shot; không có log mới tương ứng trong branch.
Vì vậy không coi 20/20 là kết quả đã đo trên prompt 71f235c.
NTL dùng gpt-5.4 qua api.xah.io; các lượt v2 ở máy này dùng OpenAI trực tiếp.

- runs/v0_B_base_openai_20261110T100441663938.json
- runs/v1_B_base_openai_20261110T104801876153.json
- artifacts/versions/history/ntl_77d11cd: snapshot khớp hashes log v1 đã đo.
- artifacts/versions/v1: snapshot bản v1 NTL mới nhất (71f235c).
- artifacts/versions/v2: snapshot v2 hiện tại, giữ prompt nền mới nhất.

## Lịch sử trước khi đổi nền/model

Artifacts và phân tích local cũ được lưu trong artifacts/local_history_before_ntl.
Các run local cũ vẫn giữ trong runs, không phải baseline NTL đang dùng.
Có git stash giữ prompt/version log local trước khi tích hợp NTL.

Các lượt v2 gpt-4o-mini trên prompt NTL 77d11cd (base 19/20, group 9/10) chỉ là
thử nghiệm trước yêu cầu đổi model. Lượt gpt-4o-mini trên prompt 71f235c đã dừng
khi người dùng yêu cầu dùng gpt-5.4; không gán kết quả cho lượt chưa hoàn tất.
Kết quả v2 cuối phải lấy từ các run có model=gpt-5.4 và prompt_hash hiện tại.
