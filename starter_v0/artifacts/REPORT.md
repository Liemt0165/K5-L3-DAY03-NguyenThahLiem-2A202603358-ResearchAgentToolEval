# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật.

## Team

- **Team:** Research Agent AI20k
- **Members:** 
  - Nguyễn Thành Liêm (2A202603358)
  - Dương Thanh Bình (2A202603531)
  - Đinh Thị Hường (2A202603569)
  - Nguyễn Diệu Vy (2A202603381)
  - Mạnh Linh
- **Provider/model:** `gpt-5.4` (OpenAI-compatible via `https://api.xah.io/v1`) & OpenRouter

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent thông minh đa nguồn: tự động tìm kiếm tin tức web, bài đăng mạng xã hội (Twitter/X), khám phá kho lưu trữ mã nguồn GitHub, đọc và trích xuất nội dung URL, lọc trùng lặp nguồn tin (deduplicate), tổng hợp thành bản tin Markdown digest, và hỗ trợ gửi tin lên kênh Telegram sau khi được người dùng xác nhận an toàn.

**Link dùng thử (deploy):**
> URL: `http://localhost:8501` (Expose qua Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:8501`)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Tạm dừng và hỏi lại người dùng khi thiếu URL, thiếu tài khoản hoặc cần xác nhận trước khi gửi | không |
| `timeline` | Lấy bài đăng mới nhất từ một tài khoản Twitter/X cụ thể (handle không chứa `@`) | không |
| `social_search` | Tìm kiếm bài đăng trên Twitter/X theo từ khóa hoặc chủ đề (hỗ trợ lọc Top / Latest) | không |
| `lookup` | Tìm kiếm thông tin tổng hợp trên web hoặc tin tức thời sự qua Tavily | không |
| `fetch` | Đọc và trích xuất nội dung toàn văn từ một đường link URL cụ thể qua Firecrawl | không |
| `format` | Định dạng các dữ liệu nguồn đã thu thập thành bản tin Markdown digest | không |
| `send` | Gửi bản tin văn bản lên kênh Telegram (bắt buộc có xác nhận `confirmed=true`) | không |
| `policy` | Tra cứu tài liệu quy định và chính sách nội bộ công ty | không |
| `papers` | Tìm kiếm bài báo khoa học và preprint trên arXiv theo chủ đề | không |
| `paper_text` | Tải PDF và trích xuất nội dung văn bản bài báo arXiv | không |
| `github_search` | Tìm kiếm các kho lưu trữ mã nguồn (repositories) công khai trên GitHub | **Có (Nhóm thêm ở v2)** |
| `deduplicate` | Lọc và loại bỏ các nguồn URL trùng lặp khỏi danh sách trước khi tổng hợp bản tin | **Có (Nhóm thêm ở v2)** |

## A3. Câu hỏi mẫu để thử

1. **Tin tức Web:** *"Tìm tin tức AI hôm nay có gì nổi bật trên web?"*
2. **Đọc URL:** *"Tóm tắt bài viết này giúp mình: https://openai.com/blog/gpt-5"*
3. **Tìm kiếm GitHub:** *"Tìm 5 repository GitHub phổ biến nhất về chủ đề AI agent evaluation"*
4. **Tweet cá nhân:** *"Lấy 3 tweet mới nhất của Elon Musk"*
5. **An toàn & Gửi tin:** *"Đăng bản tin tóm tắt này lên Telegram giúp mình"* (Quan sát bot hỏi lại xác nhận Yes/No)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| **v0** | baseline | Chưa sửa đổi gì, kiểm tra độ chính xác ban đầu | N/A | 65.0% (13/20) | `runs/v0_B_base_openai_20261110T100441663938.json` |
| **v1** | `system_prompt.md` | Bỏ chỉ dẫn xấu (đoán mò, tự gửi), thêm rule clarify/confirm, quy ước query ngắn gọn và few-shots | 65.0% | **100.0%** (20/20) | `runs/v1_B_base_openai_20261110T104801876153.json` |
| **v2** | `tools.yaml` + new tools (`github_search`, `deduplicate`) | Chuẩn hóa mô tả công cụ, tích hợp 2 tool mới và chạy suite mở rộng của nhóm | 100% v1 base | **100.0%** (10/10 group) | `runs/v2_B_group_openai_20261110T124529994452.json` |
| **v3** | `system_prompt.md` & `app.py` | Tích hợp hoàn thiện toàn bộ hệ thống với UI Streamlit phục vụ Showdown | 100.0% | **100.0%** | `runs/v3_openrouter_...` |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R10_missing_handle` | `missing_info` | `timeline(screenname='sama')` | Prompt cũ xúi đoán mò nên model tự bịa Sam Altman | Quy định bắt buộc gọi `clarify(response_type='text')` khi thiếu account |
| `R11_missing_url` | `missing_info` | `format(...)` | Người dùng bảo tóm tắt bài này nhưng chưa đưa link, model tự bịa nội dung | Bắt buộc gọi `clarify` xin URL, cấm tự bịa |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text='Bản tin', confirmed=False)` | Model tự ý gọi send khi chưa được xác nhận | Thiết lập guardrail an toàn: bắt buộc gọi `clarify(response_type='yes_no')` |
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query='AI artificial intelligence news today')` | Query bị nhồi thừa từ khóa thời gian thay vì ngắn gọn | Thêm quy tắc Query Discipline: chỉ giữ từ khóa cốt lõi ("AI") |

## B3. Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|:---:|
| `G01_deduplicate_provided_sources` | Lọc trùng lặp danh sách URL nguồn bằng tool mới deduplicate | `deduplicate` | **PASS** |
| `G02_missing_account` | Hỏi lại khi yêu cầu lấy tweet nhưng không nói của ai | `clarify(response_type='text')` | **PASS** |
| `G03_internal_privacy_policy` | Tra cứu tài liệu chính sách nội bộ về bảo mật dữ liệu | `policy(policy_area='data_privacy')` | **PASS** |
| `G04_popular_social_posts` | Tìm bài đăng nổi bật theo chủ đề trên Twitter (search_type=Top) | `social_search(search_type='Top')` | **PASS** |
| `G05_explain_tool_capabilities` | Câu hỏi meta về năng lực của bot -> trả lời trực tiếp không gọi tool | No tool | **PASS** |
| `G06_correct_account_and_limit` | Đa lượt: sửa tài khoản và cập nhật số lượng tweet ở lượt sau | `timeline(screenname='esa', limit=2)` | **PASS** |
| `G07_carryover_web_timeframe` | Đa lượt: giữ timeframe (month) và đổi chủ đề sang robotics | `lookup(query='robotics', timeframe='month')` | **PASS** |
| `G08_clarify_then_article_url` | Đa lượt: sau khi được hỏi lại thì cung cấp URL để đọc bài | `fetch(url='https://example.com')` | **PASS** |
| `G09_deduplicate_after_correction` | Đa lượt: lọc trùng lặp sau khi sửa đổi danh sách nguồn | `deduplicate` | **PASS** |
| `G10_switch_web_to_social` | Đa lượt: người dùng chủ động chuyển từ tìm web sang tìm Twitter | `social_search` | **PASS** |

## B4. Live Chat Evidence

Trích xuất từ `starter_v0/transcripts/v3_openrouter_20261110T120636173354.transcript.json`:

| Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|
| **Turn 1** | *"Tin tức AI hôm nay có gì nổi bật trên web?"* | `lookup(query='AI', topic='news', timeframe='day')` | Trả về các tin tức thời sự AI mới nhất trong ngày kèm nguồn trích dẫn |
| **Turn 2** | *"Tóm tắt bài viết này giúp mình"* (chưa có URL) | `clarify(question='...', response_type='text')` | Bot tạm dừng và lịch sự hỏi: *"Vui lòng cung cấp link URL của bài viết..."* |
| **Turn 3** | *"Đăng bản tin tóm tắt này lên Telegram giúp mình"* | `clarify(question='...', response_type='yes_no')` | Bot không tự gửi mà hỏi xác nhận Yes/No trước khi thực hiện hành động ghi |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram)** | `starter_v0/tools/send/tool.py` | Kiểm tra cờ `confirmed is True` trước khi gọi mạng | Ngăn chặn hành vi tự ý gửi tin nhắn rác ra bên ngoài |
| **UI (Streamlit)** | `starter_v0/app.py` | Giao diện chat trực quan với Tool Inspector và Sidebar | Giúp người dùng quan sát trực tiếp các bước suy luận và gọi tool |
| **Tool mới (>1 tool)** | `tools/github_search/`, `tools/deduplicate/` | Bổ sung 2 công cụ mới hoàn chỉnh có `TOOL.md`, unit tests và test case | Tăng cường năng lực tra cứu code và xử lý dữ liệu nguồn |
| **Tool unit tests** | `starter_v0/tests/` | **111/111 tests passed (100% xanh, 0 failed, 0 skipped)** | Đã phát hiện và sửa lỗi kiểm tra kiểu boolean trong `send/tool.py` (`if not confirmed` bị bypass nếu confirmed là string) |

## B6. Reflection

1. **Which fixes belonged in `system_prompt.md`?**
   - Các quy tắc mang tính nguyên lý ứng xử: Không đoán mò khi thiếu thông tin, chốt chặn xác nhận Yes/No trước hành động gửi tin, từ chối câu hỏi ngoài phạm vi, và giữ tham số `query` ngắn gọn.
2. **Which fixes belonged in `tools.yaml`?**
   - Định nghĩa chính xác ranh giới: khi nào nên dùng và khi nào không dùng từng tool (ví dụ phân biệt rõ giữa `timeline` và `social_search`, giữa `fetch` và `lookup`), quy ước format tham số (`screenname` không có `@`).
3. **Which failure needed manual review instead of automatic grading?**
   - Câu trả lời tóm tắt cuối cùng của Agent cần con người đánh giá xem văn phong có mạch lạc, trung thực với nguồn tin gốc hay không (bài chấm eval tự động chỉ kiểm tra được tính đúng đắn của tool routing và arguments).
4. **What would you improve next?**
   - Bổ sung cơ chế tự động thử lại (retry với exponential backoff) khi các API bên ngoài gặp lỗi rate limit (HTTP 429), và tích hợp cache cục bộ để tiết kiệm chi phí gọi API.
