from pynput import mouse
import logging
import sys

# Cấu hình logging để in ra console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def on_click(x, y, button, pressed):
    """
    Hàm callback được gọi mỗi khi có sự kiện click chuột.
    """
    if pressed and button == mouse.Button.left:
        logging.info(f"Đã click chuột trái tại vị trí: ({int(x)}, {int(y)})")

def run_logger():
    logging.info("Đang lắng nghe sự kiện click chuột... (Nhấn Ctrl+C để dừng)")
    # Khởi tạo listener để lắng nghe sự kiện chuột
    with mouse.Listener(on_click=on_click) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            logging.info("Đã dừng logger.")

if __name__ == "__main__":
    run_logger()
