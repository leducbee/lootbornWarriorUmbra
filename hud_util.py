import threading
import time
import logging
import sys
from qt_hud import HUDManager

class HUD:
    """
    HUD class wrapper sử dụng PyQt5.
    Lưu ý quan trọng trên macOS: 
    1. Bạn phải khởi tạo đối tượng HUD này trên MAIN THREAD.
    2. Sau khi khởi tạo và chạy logic (trong thread khác), bạn phải gọi hud.start() 
       ở cuối main thread để chạy vòng lặp hiển thị của Qt.
    """
    def __init__(self):
        self.manager = None
        try:
            self.manager = HUDManager()
            logging.info("HUD initialized using PyQt5 (Real-time Overlay).")
        except Exception as e:
            logging.error(f"Failed to initialize PyQt5 HUD: {e}")

    def update_regions(self, regions, padding=0):
        """
        Cập nhật các vùng vẽ trên HUD với padding.
        regions: [("Name", (x, y, w, h)), ...]
        """
        if self.manager:
            padded_regions = []
            for name, rect in regions:
                x, y, w, h = rect
                # Áp dụng padding: mở rộng đều ra 4 phía
                padded_rect = (
                    x - padding,
                    y - padding,
                    w + (padding * 2),
                    h + (padding * 2)
                )
                padded_regions.append((name, padded_rect))
            
            self.manager.update_regions(padded_regions)

    def start(self):
        """
        Bắt đầu vòng lặp sự kiện của Qt. 
        Hàm này sẽ chặn (block) thread hiện tại (nên gọi ở main thread).
        """
        if self.manager:
            logging.info("Starting HUD main loop...")
            return self.manager.start_main_loop()
        return None

    def stop(self):
        """Dừng HUD (thường bằng cách đóng ứng dụng)"""
        # Với Qt, việc dừng thường được quản lý bởi việc đóng cửa sổ hoặc thoát app
        pass

if __name__ == "__main__":
    # Test HUD mới tích hợp
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    hud = HUD()
    
    def background_logic():
        time.sleep(1)
        logging.info("Updating dummy regions...")
        for i in range(50):
            dummy_regions = [
                (f"Test_{i}", (100 + i*5, 100 + i*2, 200, 50)),
                ("Center", (500, 400, 100, 100))
            ]
            hud.update_regions(dummy_regions)
            time.sleep(0.1)
        logging.info("Logic finished.")

    # Chạy logic trong thread riêng
    logic_thread = threading.Thread(target=background_logic, daemon=True)
    logic_thread.start()
    
    # Chạy HUD trên main thread
    hud.start()
