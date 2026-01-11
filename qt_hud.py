import sys
import threading
import logging
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
class HUDSignals(QObject):
    update_data = pyqtSignal(list)
    request_calibration = pyqtSignal(object) 
class ClickOverlay(QWidget):
    def __init__(self, signals, callback=None):
        super().__init__()
        self.signals = signals
        self.callback = callback
        logging.info(f"ClickOverlay initialized. Callback provided: {callback is not None}")
        self.points = []
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False) 
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())
        self.label_text = "Click to define 4 corners of the scanning area (Top-Left, Top-Right, Bottom-Right, Bottom-Left)"
        self.show()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Helvetica", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.label_text}\nPoints: {len(self.points)}/4")
        painter.setPen(QPen(Qt.red, 3))
        for point_tuple in self.points:
            # point_tuple đã là logical coordinate
            point = QPoint(point_tuple[0], point_tuple[1])
            painter.drawEllipse(point, 5, 5)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # PyQt5 event.pos() trả về tọa độ logical.
            # Chúng ta cần đảm bảo lưu tọa độ logical để đồng nhất với pyautogui.
            x = event.pos().x()
            y = event.pos().y()
            logging.info(f"Click recorded at logical: ({x}, {y})")
            self.points.append((x, y))
            self.update()
            if len(self.points) == 4:
                logging.info(f"Calibration points collected: {self.points}")
                if self.callback:
                    try:
                        logging.info("Calling calibration callback...")
                        self.callback(self.points)
                        logging.info("Calibration callback executed successfully.")
                    except Exception as e:
                        logging.error(f"Error in calibration callback: {e}")
                self.hide()
                self.close()
class QtHUD(QWidget):
    def __init__(self, signals):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        super().__init__()
        self.signals = signals
        self.regions = []
        self.overlay = None
        self.signals.update_data.connect(self._set_regions)
        self.signals.request_calibration.connect(self._show_calibration)
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Specific macOS optimizations to stay on top
        # self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        # Full screen
        screen = self.app.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())
        # Ensure it's not hidden initially
        self.show()
        self.raise_()
    def _set_regions(self, regions):
        # logging.info(f"HUD: Received {len(regions)} regions to render.")
        self.regions = regions
        self.update()  # Trigger repaint
    def _show_calibration(self, callback):
        logging.info("Showing Calibration Overlay...")
        if self.overlay:
            self.overlay.close()
        self.overlay = ClickOverlay(self.signals, callback)
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()
    def paintEvent(self, event):
        # logging.info(f"QtHUD paintEvent triggered. Regions: {len(self.regions)}")
        if not self.regions:
            # logging.info("QtHUD paintEvent: No regions to draw.")
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Trên macOS High-DPI, Qt tự động xử lý vẽ tọa độ logical.
        # Chúng ta chỉ vẽ các rect dựa trên tọa độ logical đã nhận.
        # Font chữ
        font = QFont("Helvetica", 12, QFont.Bold)
        painter.setFont(font)
        for name, rect in self.regions:
            x, y, w, h = rect
            # Chọn màu sắc và text dựa trên tên vùng
            if name == "SCAN_AREA":
                pen = QPen(QColor(0, 255, 0)) # Màu Green (Xanh lá cây)
                display_text = "Scanning region coordinates"
            else:
                pen = QPen(QColor(255, 0, 255)) # Màu Magenta (Hồng tím)
                display_text = name
            pen.setWidth(2)
            painter.setPen(pen)
            # Vẽ hình chữ nhật (Tọa độ logical)
            painter.drawRect(x, y, w, h)
            # Vẽ text ngay phía trên box
            painter.drawText(x, y - 5, display_text)
    def update_regions(self, regions):
        self.signals.update_data.emit(regions)
    def start_calibration(self, callback):
        self.signals.request_calibration.emit(callback)
def start_hud_app(hud_container):
    signals = HUDSignals()
    hud_container['instance'] = QtHUD(signals)
    sys.exit(hud_container['app_ref'].exec_())
class HUDManager:
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        self.signals = HUDSignals()
        self.hud = QtHUD(self.signals)
    def start_calibration(self, callback):
        self.hud.start_calibration(callback)
    def start_main_loop(self):
        return self.app.exec_()
    def update_regions(self, regions):
        if self.hud:
            self.hud.update_regions(regions)
if __name__ == "__main__":
    # Test block
    print("Testing QtHUD... (Requires PyQt5)")
    import time
    # On macOS, we can't run HUD in a thread if we want it to be the main GUI
    # So we do the opposite: Run logic in a thread, and HUD in main thread
    manager = HUDManager()
    def background_logic():
        time.sleep(1)  # Wait for HUD to show
        try:
            for i in range(100):
                test_data = [
                    (f"Qt Target {i}", (100 + i * 5, 100 + i * 2, 200, 100)),
                    ("Static Area", (500, 500, 150, 50))
                ]
                manager.update_regions(test_data)
                time.sleep(0.05)
        except Exception as e:
            print(f"Logic error: {e}")
        print("Logic finished. You can close the window or Ctrl+C.")
    logic_thread = threading.Thread(target=background_logic, daemon=True)
    logic_thread.start()
    sys.exit(manager.start_main_loop())
