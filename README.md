# AutoScript - Công cụ Tự động hóa Game

AutoScript là một ứng dụng mạnh mẽ được thiết kế để tự động hóa các thao tác trong game dựa trên nhận diện hình ảnh. Công cụ này hỗ trợ người chơi thực hiện các chuỗi hành động lặp đi lặp lại một cách thông minh, đặc biệt là trong việc săn tìm các mục tiêu cụ thể.

### 📥 Tải về (Download)
Để đảm bảo ứng dụng chạy ổn định với đầy đủ cấu hình và asset, vui lòng tải xuống file nén tương ứng với hệ điều hành của bạn:

*   **Windows:** [Tải xuống AutoScript cho Windows (.zip)](dist/AutoScript_win.zip)
*   **macOS:** [Tải xuống AutoScript cho macOS (.zip)](dist/AutoScript_mac.zip)

**Lưu ý:** Sau khi tải về, bạn hãy giải nén. Bạn phải giữ nguyên cấu trúc thư mục (bao gồm file `AutoScript`, `config.json`, `initial_coordinates.txt` và thư mục `src`) để công cụ hoạt động chính xác.

---

### ✨ Tính năng chính
*   **Tự động chiến đấu (Auto Combat):** Nhận diện trạng thái trận đấu và thực hiện các thao tác tương ứng (Bắt đầu, Win, Failed).
*   **Săn rương thông minh (Treasure Hunting):** Tự động tìm kiếm và ưu tiên các cổng có rương báu (`lvl3_ruongNguyen`).
*   **Hệ thống thông báo Telegram:** 
    *   Gửi thông báo và ảnh chụp màn hình khi tìm thấy rương.
    *   Cảnh báo khi không nhận diện được màn hình game trong thời gian dài.
    *   Điều khiển từ xa (ví dụ: lệnh `exit` để dừng tool, `capture` để xem màn hình hiện tại).
*   **Tự động dọn dẹp (Auto Refine):** Tự động thực hiện thao tác tách đồ (`tach`) để giải phóng không gian.
*   **Hỗ trợ đa nền tảng:** Chạy tốt trên cả Windows và macOS.

---

### 🚀 Hướng dẫn cài đặt

#### 1. Yêu cầu hệ thống
*   Python 3.10 trở lên (nếu chạy từ mã nguồn).
*   Cấp quyền **Accessibility** và **Screen Recording** (đối với người dùng macOS).

#### 2. Cài đặt thư viện (nếu chạy từ source)
```bash
pip install -r requirements.txt
# Hoặc cài đặt lẻ:
pip install pyautogui opencv-python numpy pillow pynput python-telegram-bot
```

#### 3. Cấu hình
*   Chỉnh sửa file `config.json` để thiết lập `telegram_token`, `telegram_chat_id` và `scan_region`.

---

### 🛠 Cách sử dụng

Để tool hoạt động hiệu quả nhất, bạn nên thực hiện theo các bước sau:

#### Bước 1: Thu thập Asset và Tọa độ (Mode 1)
1.  **Chạy quét tọa độ:** Chạy lệnh `python scan_and_collect.py`. 
2.  **Cung cấp Asset:** Khi tool báo thiếu asset (ở thư mục `src/assets/scanning/`), bạn hãy chụp ảnh màn hình vùng đó, copy vào clipboard và nhấn `Ctrl+V` (Windows) hoặc `Cmd+V` (macOS) để tool tự động lưu và nhận diện.
3.  **Optimize vùng quét:** Chạy tool vài lần, để nhân vật đi qua cả cổng bên trái (left) và bên phải (right) giúp tool cover hết các trường hợp và tối ưu hóa vùng scan.

#### Bước 2: Kiểm tra và Chạy Auto (Mode 2)
1.  **Kiểm tra dữ liệu:** Mở file `found_coordinate_scanning.txt` kiểm tra xem đã đủ thông tin tọa độ các nút và portal chưa.
2.  **Chạy Auto:** Tắt công cụ quét, sau đó chạy ứng dụng chính bằng lệnh:
    ```bash
    python auto_script_application.py
    ```
    (Hoặc chạy file thực thi `AutoScript` trong thư mục đã tải). Lúc này tool sẽ chạy ở chế độ Auto hoàn toàn.

#### Bước 3: Xử lý khi gặp Rương Nguyên (Treasure)
1.  Khi gặp **Rương Nguyên**, ứng dụng sẽ tự động dừng lại để đảm bảo an toàn. 
2.  Lúc này, bạn cần tắt tool, cung cấp asset rương (nếu chưa có) bằng cách quay lại **Bước 1** (chạy `scan_and_collect.py`).
3.  Sau khi đã cập nhật đủ asset, quay lại chạy Auto.

---

### 📺 Video hướng dẫn
*   **Link tham khảo:** [Đang cập nhật video YouTube]

---

### ⌨️ Phím tắt & Điều khiển
*   **Dừng khẩn cấp:** 
    *   Nhấn phím `ESC` để thoát.
    *   **Fail-Safe:** Di chuyển chuột nhanh vào một trong 4 góc màn hình để dừng ngay lập tức.
*   **Điều khiển qua Telegram:** Chat trực tiếp với bot đã cấu hình (lệnh `exit` để dừng, `capture` để xem màn hình).

---

### ⚠️ Lưu ý quan trọng
*   Đảm bảo cửa sổ game luôn hiển thị và không bị che khuất.
*   Độ phân giải màn hình và tỷ lệ scale cần được giữ nguyên so với lúc lấy mẫu hình ảnh.
*   Nên chạy tool ở chế độ cửa sổ để dễ dàng quản lý.

Happy Auto Run! 🚀
