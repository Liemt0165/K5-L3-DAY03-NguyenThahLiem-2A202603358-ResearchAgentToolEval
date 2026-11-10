> Lịch sử local trước khi kéo NTL; không phải baseline đang dùng cho v2. Baseline NTL xem V1_ANALYSIS.md và V2_BASELINE_SOURCE.md.

# Baseline v0

Provider: OpenAI / gpt-4o-mini. Chạy API thật trên 20 case base, không sửa prompt/tool starter.

| Metric | Kết quả |
|---|---:|
| Case accuracy | 14/20 (70%) |
| Tool routing accuracy | 75% |
| Argument accuracy | 70% |
| Multi-turn accuracy | 100% (6/6) |
| Provider errors | 0 |

## Các lỗi thực tế

| Case | Quan sát | Hướng sửa cho vòng sau (chưa thực hiện) |
|---|---|---|
| R08 | Gọi send cho câu hỏi tích phân | Giới hạn phạm vi research; câu ngoài phạm vi không gọi tool |
| R10 | Tự đoán screenname=sama | Thiếu tài khoản phải gọi clarify |
| R11 | Tự đoán URL https://example.com/article | Thiếu URL phải gọi clarify |
| R12 | Gọi send ngay, chưa hỏi xác nhận | Hỏi xác nhận nội dung trước khi gửi |
| R13 | lookup query='AI news', thiếu topic; kỳ vọng query='AI', topic='news' | Quy ước query giữ chủ đề, thời sự đặt trong topic/timeframe |
| R14 | Gọi send cho yêu cầu viết Fibonacci | Không dùng send để trả lời câu hỏi thông thường |

R13 có cả lookup và social_search: lỗi nằm ở arguments, không phải thiếu công cụ.
Tên failure_type của dataset chỉ là loại lỗi mục tiêu; cần đọc actual_tool_calls và observed_mismatch để kết luận.

## Giới hạn bằng chứng

Chỉ có OPENAI_API_KEY. TAVILY_API_KEY, FIRECRAWL_API_KEY và RAPIDAPI_KEY chưa được cấu hình;
tool tương ứng đã được gọi thật nhưng trả lỗi thiếu key. Điểm eval đo routing/arguments,
không chứng minh lấy dữ liệu hoặc câu trả lời cuối hoạt động đúng. send không gửi vì chưa xác nhận và chưa cấu hình Telegram.
Case no_tool chỉ kiểm tra không gọi tool, không kiểm tra chất lượng câu từ chối.
Multi-turn eval đưa lịch sử có sẵn vào prompt; không phải hội thoại end-to-end thực tế.

Log thật nằm trong runs/v0_B_base_openai_20261110T095029642910.json.
Snapshot prompt/tool nằm trong artifacts/versions/v0/; hashes ghi trong artifacts/version_log.csv.

## Chạy UI trên Windows

Từ thư mục starter_v0:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Mở http://localhost:8501. UI giữ nguyên baseline v0, có xem tool call và tải transcript JSON.
Bổ sung key tool trong .env rồi khởi động lại UI để lấy dữ liệu bên ngoài.

## Kiểm tra UI đã thực hiện

- Streamlit AppTest: giao diện ban đầu không có exception; ô chat hoạt động.
- Một lượt OpenAI thật: hỏi quy định trích dẫn nội bộ, gọi policy với policy_area=source_citation, hiển thị câu trả lời và lưu transcript.
- Nút tạo cuộc trò chuyện mới xóa lịch sử hiển thị, giữ transcript cũ trên đĩa.
- Bằng chứng: transcripts/v0_ui_20261110T095701_25ad4ce6.transcript.json.
- Offline suite: 62 passed, 17 skipped (các stub starter giữ nguyên).
- Hash prompt/tool hiện tại khớp log v0. Chưa thực hiện tối ưu v1–v3.
- Chưa kiểm tra trực quan bằng screenshot; UI dùng layout và controls mặc định của Streamlit.
