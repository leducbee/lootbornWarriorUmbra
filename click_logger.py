from pynput import mouse
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        logging.info(f"Đã click chuột trái tại vị trí: ({int(x)}, {int(y)})")
def run_logger():
    logging.info("Đang lắng nghe sự kiện click chuột... (Nhấn Ctrl+C để dừng)")
    with mouse.Listener(on_click=on_click) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            logging.info("Đã dừng logger.")
if __name__ == "__main__":
    run_logger()
