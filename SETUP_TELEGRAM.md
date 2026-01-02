### Hướng dẫn thiết lập Telegram Bot để nhận thông báo về điện thoại

Để nhận được thông báo từ script trên Mac về iPhone, bạn cần tạo một Telegram Bot. Đây là cách nhanh và ổn định nhất.

#### Bước 1: Tạo Bot và lấy Token
1. Mở Telegram, tìm kiếm `@BotFather`.
2. Gửi lệnh `/newbot`.
3. Làm theo hướng dẫn (đặt tên cho bot).
4. Sau khi xong, bạn sẽ nhận được một chuỗi **API Token** (ví dụ: `712345678:ABCDefGhIJK...`). Hãy lưu nó lại.

#### Bước 2: Lấy Chat ID của bạn
1. Tìm kiếm `@userinfobot` trên Telegram.
2. Nhấn `Start`.
3. Nó sẽ gửi cho bạn một dãy số `Id` (ví dụ: `123456789`). Đây là **Chat ID** của bạn.

#### Bước 3: Cấu hình vào Script
1. Mở file `telegram_notifier.py`.
2. Thay `YOUR_BOT_TOKEN` bằng Token bạn vừa nhận được.
3. Thay `YOUR_CHAT_ID` bằng dãy số ID của bạn.
4. Chạy lệnh: `python3 telegram_notifier.py` để kiểm tra.

#### Bước 4: Tích hợp vào Auto Script
Sau khi test xong, tôi sẽ cập nhật `application.py` để nó tự động dùng thông tin này gửi thông báo mỗi khi tìm thấy Rương Nguyên.
