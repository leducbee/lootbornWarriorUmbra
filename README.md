# AutoScript - Công cụ Tự động hóa Game

AutoScript là một ứng dụng mạnh mẽ được thiết kế để tự động hóa các thao tác trong game dựa trên nhận diện hình ảnh. Công cụ này hỗ trợ người chơi thực hiện các chuỗi hành động lặp đi lặp lại một cách thông minh, đặc biệt là trong việc săn tìm các mục tiêu cụ thể.

### 📥 Tải về (Download)
Để đảm bảo ứng dụng chạy ổn định với đầy đủ cấu hình và asset, vui lòng tải xuống file nén tương ứng với hệ điều hành của bạn:

*   **Windows:** [Tải xuống AutoScript cho Windows (.zip)](dist/AutoScript_win.zip)
*   **macOS:** [Tải xuống AutoScript cho macOS (.zip)](dist/AutoScript_mac.zip)

**Lưu ý:** Sau khi tải về, bạn hãy giải nén. Bạn phải giữ nguyên cấu trúc thư mục (bao gồm file `AutoScript`, `config.json` và thư mục `src`) để công cụ hoạt động chính xác.

---

### ✨ Tính năng chính
*   **Tự động chiến đấu (Auto Combat):** Nhận diện trạng thái trận đấu và thực hiện các thao tác tương ứng (Bắt đầu, Win, Failed).
*   **Săn rương thông minh (Treasure Hunting):** Tự động tìm kiếm và ưu tiên các cổng có rương báu (`lvl3_ruongNguyen`). Nếu không thấy rương, hệ thống sẽ tự động chọn cổng có cấp độ thấp nhất để đảm bảo an toàn. Tất cả asset được quản lý trong thư mục `src/assets/scanning/`.
*   **Tự động chuyển lộ trình:** Nếu sau 2 đợt (wave) không tìm thấy rương, hệ thống sẽ tự động Reset để bắt đầu lộ trình mới.
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

#### Bước 1: Xác định vùng quét và Thu thập Asset (Mode 1)
1.  **Xác định vùng quét (Scan Region):** Chạy lệnh `python scan_and_collect.py`. Nếu đây là lần đầu chạy, tool sẽ yêu cầu bạn xác định vùng cần quét trên màn hình (thường là vùng chứa các cổng portal). Hãy chọn 2 điểm để tạo thành khung hình chữ nhật bao quanh khu vực game. Vùng này sẽ được hiển thị bằng **khung viền màu đỏ (SCAN_AREA)** trên HUD.
2.  **Cung cấp Asset:** Sau khi đã có vùng quét đỏ, tool sẽ bắt đầu tìm kiếm các asset bên trong vùng đó. Khi tool báo thiếu asset hoặc bạn muốn thêm asset mới (ở thư mục `src/assets/scanning/`):
    *   Chụp ảnh màn hình vùng asset đó.
    *   Copy vào clipboard.
    *   Nhấn `Ctrl+V` (Windows) hoặc `Cmd+V` (macOS) để tool tự động lưu thành file `image.png` trong thư mục scanning.
    *   *Lưu ý:* Bạn cần đổi tên file `image.png` thành tên tương ứng trong `ASSETS_MAPPING` (ví dụ: `text_lvl3_ruongNguyen_1.png`) để tool nhận diện.
3.  **Kiểm tra nhận diện:** Khi asset đã có trong thư mục, tool sẽ hiển thị khung xanh kèm tên asset trên HUD nếu tìm thấy chúng trong vùng quét đỏ. Chạy tool vài lần để đảm bảo nhận diện đủ các loại cổng (portals).

#### Bước 2: Kiểm tra và Chạy Auto (Mode 2)
1.  **Chạy Auto:** Tắt công cụ quét, sau đó chạy ứng dụng chính bằng lệnh:
    ```bash
    python auto_script_application.py
    ```
    (Hoặc chạy file thực thi `AutoScript` trong thư mục đã tải). Lúc này tool sẽ chạy ở chế độ Auto hoàn toàn.

#### Bước 3: Xử lý khi gặp Rương Nguyên (Treasure)
1.  Khi gặp **Rương Nguyên**, ứng dụng sẽ tự động chọn cổng rương, gửi ảnh thông báo qua Telegram và chuyển sang trạng thái chờ kết thúc trận đấu.
2.  Sau khi lấy rương, `max_run` trong cấu hình sẽ tự động giảm đi 1. Tool sẽ tự động dừng nếu `max_run` chạm mức 0.
3.  Bạn có thể theo dõi tiến độ và số lượng rương đã tìm thấy thông qua Logs hoặc thông báo Telegram.

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
