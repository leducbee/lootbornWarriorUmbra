import sys
import threading
import logging
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QFont


class HUDSignals(QObject):
    update_data = pyqtSignal(list)


class QtHUD(QWidget):
    def __init__(self):
        # We need a QApplication instance before creating any QWidget
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

        super().__init__()

        self.regions = []
        self.signals = HUDSignals()
        self.signals.update_data.connect(self._set_regions)

        # Configure window: Frameless, Transparent, Stay on top, Click-through
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Specific macOS optimizations to stay on top
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # Full screen
        screen = self.app.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())

        self.show()

    def _set_regions(self, regions):
        # logging.info(f"HUD: Updating {len(regions)} regions")
        self.regions = regions
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        if not self.regions:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Font chữ
        font = QFont("Helvetica", 12, QFont.Bold)
        painter.setFont(font)

        for name, rect in self.regions:
            x, y, w, h = rect
            
            # Chọn màu sắc dựa trên tên vùng
            if "left_portal_text" in name or "right_portal_text" in name:
                pen = QPen(QColor(0, 255, 0)) # Màu xanh lá cây cho portal
            else:
                pen = QPen(QColor(255, 0, 0)) # Màu đỏ cho các vùng khác
            
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Vẽ hình chữ nhật
            painter.drawRect(x, y, w, h)
            
            # Vẽ text ngay phía trên box
            painter.drawText(x, y - 5, name)

    def update_regions(self, regions):
        """
        Thread-safe method to update regions.
        regions: [("Name", (x, y, w, h)), ...]
        """
        self.signals.update_data.emit(regions)


def start_hud_app(hud_container):
    """Function to run the Qt Event Loop"""
    hud_container['instance'] = QtHUD()
    sys.exit(hud_container['app_ref'].exec_())


class HUDManager:
    """Helper class to manage HUD. On macOS, this MUST be initialized on the main thread."""

    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

        self.hud = QtHUD()

    def start_main_loop(self):
        """Runs the Qt event loop. This blocks the main thread."""
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
