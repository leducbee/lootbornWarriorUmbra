import threading
import time
import logging
import sys
from qt_hud import HUDManager
class HUD:
    def __init__(self):
        self.manager = None
        try:
            self.manager = HUDManager()
            logging.info("HUD initialized using PyQt5 (Real-time Overlay).")
        except Exception as e:
            logging.error(f"Failed to initialize PyQt5 HUD: {e}")
    def update_regions(self, regions, padding=0):
        if self.manager:
            padded_regions = []
            for name, rect in regions:
                x, y, w, h = rect
                padded_rect = (
                    x - padding,
                    y - padding,
                    w + (padding * 2),
                    h + (padding * 2)
                )
                padded_regions.append((name, padded_rect))
            self.manager.update_regions(padded_regions)
    def start(self):
        if self.manager:
            logging.info("Starting HUD main loop...")
            return self.manager.start_main_loop()
        return None
    def request_calibration(self, callback):
        if self.manager:
            self.manager.start_calibration(callback)
    def stop(self):
        pass
if __name__ == "__main__":
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
    logic_thread = threading.Thread(target=background_logic, daemon=True)
    logic_thread.start()
    hud.start()
