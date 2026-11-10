# Team

Nhóm điền phần **Thông tin nhóm** và **Thành viên**. Mỗi người tự điền phần của mình trong **Cá nhân**.

## Thông tin nhóm

- Tên nhóm: D4
- Đề tài / Mục tiêu: Xây dựng và đánh giá Research Agent hỗ trợ nghiên cứu đa nguồn (Web, Twitter/X, GitHub, arXiv), tối ưu qua các vòng lặp evidence-driven (v0 -> v3), đảm bảo guardrail an toàn xác nhận khi gửi tin Telegram và đạt 100% unit tests.
- Trạng thái kỹ thuật: Toàn bộ các thành viên đều cài đặt được môi trường và kết nối thành công API.

## Thành viên

| STT | Họ và tên | MSSV | Vai trò trong nhóm | Tài khoản GitHub |
|---:|---|---|---|---|
| 1 | Nguyễn Thành Liêm | 2A202603358 | Nhóm trưởng, Prompt & Tooling, Merge & Release | Liemt0165 |
| 2 | Dương Thanh Bình | 2A202603531 | Phát triển Tool GitHub Search, Xây dựng UI Streamlit, Eval | BinhThanh313 |
| 3 | Đinh Thị Hường | 2A202603569 | Phát triển Tool Deduplicate, Phân tích routing v3 | dihnhuonq130104 |
| 4 | Nguyễn Diệu Vy | 2A202603381 | Thành viên nhóm | *(tự điền)* |
| 5 | Mạnh Linh | *(tự điền)* | Thành viên nhóm | *(tự điền)* |

Không ghi email hay số điện thoại vào bảng này, vì repo có thể để public.

---

## Cá nhân

Mỗi thành viên thêm một mục theo mẫu dưới đây, tiêu đề là `HoVaTen-MSSV`.

### NguyenThanhLiem-2A202603358

**Phần việc phụ trách:**
- Chạy test v1, tối ưu hóa System Prompt đạt 100% accuracy trên base suite.
- Chuẩn hóa mô tả công cụ (`tools.yaml`).
- Thêm và tích hợp tool mới `weather` (tra cứu thời tiết thời gian thực qua `wttr.in`) kèm unit tests.
- Xây dựng Poster trình bày (`poster.html`), tổng hợp và hoàn thiện báo cáo nhóm (`REPORT.md`).
- Đồng bộ, lọc sạch và quản lý merge nhánh `team-merged` sang `main`.

**Đóng góp cụ thể** (mình đã làm gì, ra sản phẩm gì):
- Thiết lập adapter OpenAI-compatible kết nối endpoint `https://api.xah.io/v1` chạy model `gpt-5.4`.
- Chạy baseline v0 đạt 65% (13/20 cases), phân tích 7 cases thất bại để xác định giả thuyết cải tiến cho v1.
- Sửa `artifacts/system_prompt.md` bổ sung quy tắc clarify khi thiếu URL/account, chốt chặn xác nhận Yes/No trước khi gửi tin, kỷ luật query ngắn gọn, đưa độ chính xác v1 lên 20/20 (100.0%).
- Viết tool `weather/` gồm `tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`.
- Bổ sung 3 unit tests cho tool `weather` và phát hiện, sửa lỗi ép kiểu boolean trong `send/tool.py` (`if confirmed is not True`), nâng toàn bộ suite lên 119/119 tests xanh (100% PASS, 0 failed, 0 skipped).
- Tạo file poster infographic `starter_v0/artifacts/poster.html` và hoàn thiện Báo cáo `REPORT.md` (Phần A trước 16:30 và Phần B đầy đủ bằng chứng).
- Kiểm tra toàn bộ repo, loại bỏ các file rác/nháp của các nhánh phụ, merge sạch sẽ lên `main` và push lên GitHub.

**Bằng chứng** (phần nào trong `REPORT.md`, file nào trong `tools/`, commit nào):
- Thư mục tool: `starter_v0/tools/weather/` (`tool.py`, `TOOL.md`).
- Khai báo & Prompt: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`.
- Báo cáo & Poster: `starter_v0/artifacts/REPORT.md`, `starter_v0/artifacts/poster.html`.
- File run log thực nghiệm: `starter_v0/runs/v0_B_base_openai_20261110T100441663938.json`, `starter_v0/runs/v1_B_base_openai_20261110T104801876153.json`, `starter_v0/runs/v3_B_base_openai_20261110T144630583026.json`.
- Unit tests: `starter_v0/tests/test_tools_todo.py` (119/119 pass).
- Các commit trên nhánh `ntl`, `team-merged` và `main`.

**Điều mình học được từ phần nhóm:**
- Hiểu sâu sắc phương pháp tiếp cận *"Evidence-driven Prompt Engineering"* (dựa trên log thật để cải tiến từng giả thuyết, không phỏng đoán).
- Nắm vững cơ chế gọi công cụ (Tool Calling / Function Calling), tầm quan trọng của việc kiểm tra hợp đồng schema giữa `tools.yaml` và code thực thi, cũng như thiết lập guardrail an toàn bắt buộc trước khi thực hiện các hành động ghi/gửi ra bên ngoài (Action tools).

---

### DuongThanhBinh-2A202603531

*(Thành viên tự điền phần việc và đóng góp cụ thể của mình tại đây)*

---

### DinhThiHuong-2A202603569

*(Thành viên tự điền phần việc và đóng góp cụ thể của mình tại đây)*

---

### NguyenDieuVy-2A202603381

*(Thành viên tự điền phần việc và đóng góp cụ thể của mình tại đây)*

---

### ManhLinh

*(Thành viên tự điền MSSV, phần việc và đóng góp cụ thể của mình tại đây)*

