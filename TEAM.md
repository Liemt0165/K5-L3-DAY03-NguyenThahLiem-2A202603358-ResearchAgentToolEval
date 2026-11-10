# Team

Nhóm điền phần **Thông tin nhóm** và **Thành viên**. Mỗi người tự điền phần của mình trong **Cá nhân**.

## Thông tin nhóm

- Tên nhóm: D4
- Đề tài / Mục tiêu: Xây dựng và đánh giá Research Agent hỗ trợ nghiên cứu đa nguồn (Web, Twitter/X, GitHub, arXiv), tối ưu qua các vòng lặp evidence-driven (v0 -> v3), đảm bảo guardrail an toàn xác nhận khi gửi tin Telegram và đạt 100% unit tests.
- Trạng thái kỹ thuật: Toàn bộ các thành viên đều cài đặt được môi trường và kết nối thành công API.

## Thành viên

| STT | Họ và tên | MSSV | Vai trò trong nhóm | Tài khoản GitHub |
|---:|---|---|---|---|
| 1 | Nguyễn Thành Liêm | 2A202603358 | Nhóm trưởng | Liemt0165 |
| 2 | Dương Thanh Bình | 2A202603531 | Thành viên nhóm | BinhThanh313 |
| 3 | Đinh Thị Hường | 2A202603569 | Thành viên nhóm | dihnhuonq130104 |
| 4 | Nguyễn Diệu Vy | 2A202603381 | Thành viên nhóm | dieuvy2912 |
| 5 | Mạnh Linh | 2A202603539 | Thành viên nhóm | manhlinh46 |

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
- File run log thực nghiệm: `starter_v0/runs/v0_B_base_openai_20261110T100441663938.json`, `starter_v0/runs/v1_B_base_openai_20261110T104801876153.json`,
- Unit tests: `starter_v0/tests/test_tools_todo.py` (119/119 pass).
- Các commit trên nhánh `ntl`, `team-merged` và `main`.

**Điều mình học được từ phần nhóm:**
- Hiểu sâu sắc phương pháp tiếp cận *"Evidence-driven Prompt Engineering"* (dựa trên log thật để cải tiến từng giả thuyết, không phỏng đoán).
- Nắm vững cơ chế gọi công cụ (Tool Calling / Function Calling), tầm quan trọng của việc kiểm tra hợp đồng schema giữa `tools.yaml` và code thực thi, cũng như thiết lập guardrail an toàn bắt buộc trước khi thực hiện các hành động ghi/gửi ra bên ngoài (Action tools).

---

### DuongThanhBinh-2A202603531

## 1. Phần tự thực hiện độc lập (Trước khi merge nhánh nhóm)

### 1.1. Tự chạy và tối ưu chuỗi `v0` → `v1` → `v2` trên nhánh cá nhân
- **`v0` (Baseline):** Chạy đánh giá baseline trên `data/eval_base.json` với provider `openrouter` (`openai/gpt-4o-mini`), đạt **`64.71%` (11/17 cases)** (`runs/v0_B_base_openrouter_20261110T110625205823.json`).
- **`v1` (Tối ưu `artifacts/system_prompt.md`):** Xóa các chỉ dẫn xấu ở bản gốc (ép hoàn thành 1 bước, tự đoán tham số, tự gửi tin nhắn không hỏi xác nhận); bổ sung quy tắc phân loại câu hỏi ngoài phạm vi (out-of-scope) và bắt buộc gọi `clarify` khi thiếu thông tin → Tăng độ chính xác lên **`85.0%` (17/20 cases)** (`runs/v1_B_base_openrouter_20261110T111328770850.json`).
- **`v2` (Tối ưu `artifacts/tools.yaml`):** Viết lại mô tả (`description`) của các tool theo cấu trúc `USE WHEN` / `DO NOT USE WHEN` và chuẩn hóa quy ước truyền tham số (`handle` bỏ ký tự `@`, ánh xạ tên thực thể sang handle, chuẩn hóa `topic="news"`, `timeframe`, `search_type`) → Sửa được các case `R01`, `R04`, tăng độ chính xác lên **`90.0%` (18/20 cases)** (`runs/v2_B_base_openrouter_20261110T114657532378.json`).

### 1.2. Thiết kế & Cài đặt Tool mới `github_search`
- Viết đặc tả kỹ thuật tại `starter_v0/tools/github_search/TOOL.md` (xác định rõ mục đích, tham số đầu vào `query`, `sort`, `max_results`, cấu trúc đầu ra và các trường hợp biên).
- Cài đặt thực thi tại `starter_v0/tools/github_search/tool.py`:
  - Gọi trực tiếp GitHub REST Search API (`https://api.github.com/search/repositories`).
  - Chuẩn hóa kết quả trả về (`title`, `url`, `source="github.com"`, `summary`, `stars`, `forks`, `language`, `updated_at`, `topics`) tương thích với chuỗi xử lý phía sau (`filter`, `summarize`, `save`, `send`).
  - Cài đặt cơ chế fallback offline an toàn khi mất mạng hoặc chạm ngưỡng rate-limit.
- Xây dựng **10 kịch bản kiểm thử** (5 single-turn `G01`–`G05` + 5 multi-turn `GM01`–`GM05`) cho `github_search` trong `starter_v0/data/eval_group.json`.

### 1.3. Hoàn thành Unit Test Challenge (`tests/test_tools_todo.py`)
- Viết mới toàn bộ **18 unit tests** trong `starter_v0/tests/test_tools_todo.py` (thay thế hoàn toàn các hàm `pytest.skip` ban đầu):
  - 14 unit tests kiểm thử các tool có sẵn (`extract`, `filter`, `summarize`, `translate`, `save`, `send`, `clarify`, `web_search`, `hn_search`, `feed`, `x_monitor`).
  - 4 unit tests kiểm thử chuyên biệt cho `github_search` (truy vấn hợp lệ, truy vấn rỗng, fallback khi `sort` không hợp lệ, giới hạn `max_results`).

### 1.4. Nâng cấp Giao diện Web Demo (`app.py`) & Xuất Transcript
- Cải tiến `starter_v0/app.py` (Streamlit UI) với 3 chức năng:
  1. **💬 Live Chat:** Cho phép chọn trực tiếp phiên bản `v0`, `v1`, `v2`, `v3` trên thanh công cụ để trải nghiệm và lưu log hội thoại.
  2. **⚖️ So sánh trực tiếp (`v0` vs `v1` vs `v2` vs `v3`):** Chạy cùng một câu hỏi song song trên nhiều phiên bản để đối chiếu trực quan sự khác biệt về `tool_calls` và câu trả lời.
  3. **📊 Bảng điểm Eval:** Đọc trực tiếp `artifacts/version_log.csv` và `runs/*.json` để hiển thị tiến trình cải thiện điểm số.
- Chạy demo và xuất file log hội thoại thực tế tại `starter_v0/transcripts/v3_openrouter_20261110T120636173354.transcript.json`.

---

## 2. Đối chiếu kết quả & Merge code với nhánh của đồng đội

- Khi đối chiếu kết quả giữa các thành viên trong nhóm, nhánh của đồng đội đạt kết quả `v1`/`v2` tối ưu hơn trên provider OpenAI (`100%`) và đã xây dựng thêm tool `deduplicate` (`tools/deduplicate/`, `tests/test_deduplicate.py` cùng 10 test cases cho `deduplicate`).
- Tiến hành `pull/merge` code từ nhánh đồng đội về để kế thừa bộ cấu hình tối ưu đó làm nền tảng phát triển tiếp phiên bản `v3` / `v3.1`.

---

## 3. Phần thực hiện sau khi Merge (Hoàn thiện `v3` & `v3.1` đạt 100%)

### 3.1. Giải quyết xung đột (Merge Conflict) & Hợp nhất 2 Tool mới
- Tích hợp đồng thời cả 2 tool mới (`github_search` và `deduplicate`) vào `starter_v0/tools/__init__.py` và khai báo đầy đủ 12 tools trong `starter_v0/artifacts/tools.yaml`.
- Hợp nhất bộ dữ liệu đánh giá nhóm `starter_v0/data/eval_group.json` gồm **20 kịch bản** (10 kịch bản `github_search` + 10 kịch bản `deduplicate`, chia đều 10 single-turn và 10 multi-turn).
- Chạy kiểm tra lại toàn bộ unit test của cả nhóm (`pytest starter_v0/tests`): đạt **`117 passed, 0 failed, 0 skipped`**.

### 3.2. Tinh chỉnh Prompt & Chạy đánh giá `v3` → `v3.1`
- **Bản `v3`:**
  - Cập nhật `artifacts/system_prompt.md` để định tuyến chính xác cho cả `github_search` và `deduplicate`, đồng thời bổ sung quy tắc bỏ tool cũ khi người dùng đổi nguồn ở hội thoại nhiều lượt (sửa thành công case `M06_switch_tool`).
  - Kết quả `v3`: Đạt **`95.0%` (19/20)** trên `eval_base.json` (`runs/v3_B_base_openrouter_20261110T140454147383.json`) và **`100%` (20/20)** trên `eval_group.json` (`runs/v3_B_group_openrouter_20261110T140646989399.json`).
- **Bản `v3.1` (Sửa triệt để `R12_confirm_before_send`):**
  - Phân tích lỗi duy nhất còn sót ở `v3` (`R12_confirm_before_send`: khi người dùng nói *"Đăng bản tin này lên Telegram giúp mình"* mà chưa kèm nội dung, model gọi `clarify` với `response_type="text"` thay vì `"yes_no"`).
  - Bổ sung quy tắc bắt buộc `clarify(response_type="yes_no")` trước mọi yêu cầu gửi tin nhắn bất kể đã có nội dung hay chưa.
  - Kết quả `v3.1`: Đạt tuyệt đối **`100%` (20/20)** trên cả `eval_base.json` (`runs/v3.1_B_base_openrouter_20261110T141507526145.json`) và **`100%` (20/20)** trên `eval_group.json` (`runs/v3.1_B_group_openrouter_20261110T141714443104.json`).
- Cập nhật đầy đủ lịch sử các phiên bản, mã băm (`prompt_hash`, `tools_hash`), giả thuyết và đường dẫn file run vào `starter_v0/artifacts/version_log.csv`.

---

### DinhThiHuong-2A202603569

*(Thành viên tự điền phần việc và đóng góp cụ thể của mình tại đây)*

---

### NguyenDieuVy-2A202603381

*(Thành viên tự điền phần việc và đóng góp cụ thể của mình tại đây)*

---

### ManhLinh - 2A202603539

*(Thành viên tự điền MSSV, phần việc và đóng góp cụ thể của mình tại đây)*

