# NHẬT KÝ TIẾN ĐỘ & THAY ĐỔI DỰ ÁN (PROJECT PROGRESS & CHANGELOG)

- **Dự án:** Research Agent Tool Evaluation (Day 03 Lab v2)
- **Tác giả / Nhánh:** `ntl`
- **Model sử dụng:** `gpt-5.4` (OpenAI-compatible via `https://api.xah.io/v1`)
- **Ngày cập nhật:** 10/11/2026

---

## 1. Cấu hình môi trường & Provider Adapters

- **Biến môi trường (`.env`):**
  - Cấu hình provider tương thích OpenAI: `OPENAI_BASE_URL=https://api.xah.io/v1`, `OPENAI_MODEL=gpt-5.4` và API key tương ứng.
  - Cấu hình API keys cho các research tools: `TAVILY_API_KEY` (Web Search) và `FIRECRAWL_API_KEY` (Web Scraper).
  - Đảm bảo an toàn bảo mật: File `.env` được đưa vào `.gitignore`, không bao giờ commit lên GitHub.
- **Cập nhật mã nguồn Adapters:**
  - `starter_v0/providers/openai_provider.py`: Hỗ trợ tự động đọc `OPENAI_BASE_URL` và `OPENAI_MODEL` từ biến môi trường nếu không truyền tham số.
  - `starter_v0/providers/openrouter_provider.py`: Hỗ trợ đọc `OPENROUTER_MODEL` từ biến môi trường.
- **Kiểm thử kết nối (Preflight Test):**
  - Chạy `starter_v0/scripts/preflight_provider.py --provider openai` kiểm tra khả năng gọi tool:
  - Kết quả: Thành công (`tool=timeline`, `args={'screenname': 'sama', 'limit': 1}`).

---

## 2. Baseline `v0` (Chạy đánh giá ban đầu với mã nguồn gốc)

- **Mục tiêu:** Đo lường độ chính xác ban đầu của Agent khi dùng `system_prompt.md` và `tools.yaml` nguyên bản của starter code.
- **Lệnh thực thi:**
  ```bash
  starter_v0\.venv\Scripts\python.exe starter_v0\run_eval.py --provider openai --version v0 --suite base --eval-cases starter_v0\data\eval_base.json
  ```
- **File log kết quả:** `starter_v0/runs/v0_B_base_openai_20261110T100441663938.json`
- **Kết quả đánh giá:**
  - **Case Accuracy:** 13/20 cases PASS (**65.0%**)
  - **Tool Routing Accuracy:** 85.0%
  - **Argument Accuracy:** 65.0%
  - **Multiturn Accuracy:** 66.67%
- **Phân tích 7 cases bị FAIL:**
  1. `R10_missing_handle` (Thiếu handle Twitter): Prompt cũ xúi đoán mò nên model tự chọn `sama` gọi `timeline`. Mong đợi: gọi `clarify`.
  2. `R11_missing_url` (Thiếu link URL bài viết): Prompt cũ bảo đoán mò nên model gọi `format` bịa nội dung. Mong đợi: gọi `clarify`.
  3. `R12_confirm_before_send` (Gửi tin Telegram): Prompt cũ xúi gửi ngay không chờ nên model gọi thẳng `send`. Mong đợi: gọi `clarify(response_type='yes_no')`.
  4. `R03_web_news_routing`, `R13_parallel_web_and_tweets`, `M02_carryover_timeframe`, `M06_switch_tool`: Tham số `query` bị nhồi thừa các từ khóa thời gian như `"AI artificial intelligence news today"` hay `"robotics news today"` thay vì chỉ chứa từ khóa cốt lõi (`"AI"`, `"robotics"`).

---

## 3. Tối ưu hóa Phiên bản `v1` (Prompt Engineering)

- **Phương pháp tiếp cận:** *"Fix One Thing"* — Chỉ sửa file `starter_v0/artifacts/system_prompt.md`, giữ nguyên `tools.yaml` và `eval_base.json`.
- **Nội dung cải tiến trong `system_prompt.md`:**
  - **Loại bỏ chỉ dẫn xấu:** Xóa các câu xúi đoán mò, tự ý gửi tin, và ép thực hiện 1 bước.
  - **Biên phạm vi (Scope Boundary):** Trả lời trực tiếp hoặc từ chối đối với các câu hỏi meta ("bạn là ai") hoặc ngoài phạm vi (giải toán, coding), tuyệt đối không gọi tool.
  - **Hỏi lại khi thiếu thông tin (Clarification):** Bắt buộc gọi `clarify(response_type='text')` khi người dùng không cung cấp URL hoặc không nói rõ tài khoản của ai.
  - **Xác nhận an toàn (Safety Guardrail):** Bắt buộc gọi `clarify(response_type='yes_no')` để xin xác nhận trước khi gọi tool `send`. Chỉ gọi `send` khi `confirmed=True`.
  - **Quy tắc trích xuất Query (Query Discipline):** Quy định tham số `query` của các công cụ tìm kiếm chỉ được chứa thực thể/từ khóa cốt lõi; cấm lặp lại các từ chỉ thời gian hay thể loại tin tức ("news", "today", "latest", "tin tức", "hôm nay") vì đã có `topic="news"` và `timeframe`.
  - **Chuẩn hóa Handle:** Bỏ ký tự `@` ở đầu khi gọi `timeline`.
  - **Ưu tiên ngữ cảnh mới nhất:** Trong hội thoại đa lượt, luôn ưu tiên các chỉnh sửa, cập nhật tham số ở lượt mới nhất.
  - **Bổ sung Few-shot Examples:** Thêm các ví dụ mẫu tổng quát (không hardcode dữ liệu test case) để định hình phản xạ gọi tool cho model.
- **Lệnh thực thi:**
  ```bash
  starter_v0\.venv\Scripts\python.exe starter_v0\run_eval.py --provider openai --version v1 --suite base --eval-cases starter_v0\data\eval_base.json
  ```
- **File log kết quả:** `starter_v0/runs/v1_B_base_openai_20261110T104801876153.json`
- **Kết quả đánh giá:**
  - **Case Accuracy:** 20/20 cases PASS (**100%**) 🎯
  - **Tool Routing Accuracy:** **100%**
  - **Argument Accuracy:** **100%**
  - **Multiturn Accuracy:** **100%**
  - **Số lỗi (Failures):** 0

---

## 4. Bảng theo dõi tiến độ (`artifacts/version_log.csv`)

| Version | Author | Changed Artifact | Case Accuracy | Routing Acc | Arg Acc | Ghi chú & Giả thuyết |
|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **`v0`** | team | baseline | **65.0%** (13/20) | 85.0% | 65.0% | Baseline starter code, chưa chỉnh sửa. |
| **`v1`** | team | `system_prompt.md` | **100.0%** (20/20) | **100.0%** | **100.0%** | Tối ưu prompt, bổ sung quy tắc clarify/confirm, quy ước query ngắn gọn và few-shot examples. |
| **`v2`** | team | prompt + `tools.yaml` + `github_search` | 80.0% (16/20) base | 85% routing, 80% args | `runs/v2_B_base_openrouter_20261110T121453310623.json` | Bốn lỗi tập trung ở thiếu thông tin, xác nhận send và đổi ý định ở multi-turn. |
| **`v3`** | team | `system_prompt.md` | 100.0% (20/20) base | 100% routing, 100% args, 100% multiturn | `runs/v3_B_base_openrouter_20261110T124406560221.json` | Làm rõ thứ tự hỏi lại/xác nhận và ưu tiên ý định mới nhất; group eval đang chạy. |

---

## 5. Kế hoạch các bước tiếp theo

1. **Phiên bản `v2`:** Đã thêm `github_search`, mô tả routing trong prompt/schema, 10 group eval case (5 single-turn + 5 multi-turn), và unit tests.
2. **Phiên bản `v3`:** Base eval đạt 20/20 sau khi xử lý các lỗi v2. Group eval 10 case đang chạy để đo khả năng routing và xử lý multi-turn cho GitHub search.
3. **Giao diện & Báo cáo Showdown:**
   - Dựng giao diện Web UI bằng Streamlit (`app.py`).
   - Mở đường hầm Cloudflare Tunnel (`cloudflared`) để demo trực tiếp.
   - Hoàn thành `artifacts/REPORT.md` (Phần A trước 16:30, Phần B trước khi nộp bài).
