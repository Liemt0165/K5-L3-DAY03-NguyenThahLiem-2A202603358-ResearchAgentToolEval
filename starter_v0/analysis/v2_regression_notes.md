# Bug unit test tìm được trong v2

send_telegram trước đây dùng `if not confirmed`: chuỗi không rỗng "false" hoặc
"true" và số 1 đều vượt qua guard. Với env thật có thể dẫn tới gửi dù model
truyền sai kiểu boolean. Test giả lập cho thấy chúng đi vào nhánh hành động.

Sửa thành `confirmed is not True`: chỉ boolean True qua guard. Năm trường hợp
sai kiểu được giữ thành regression test; có set token/chat ID giả và assert
không có request nào. Happy path True vẫn kiểm tra POST qua fake_http.
Tất cả kiểm tra offline, không có tin Telegram thật được gửi.

Eval bổ sung blocked_tools={send}: tool call vẫn được chấm theo args, nhưng
không thực thi gửi kể cả khi model trả confirmed=True. Test fake provider xác
nhận callback gửi không được chạy và event vẫn được lưu execution_disabled.
