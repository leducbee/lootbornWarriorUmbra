import pyautogui
import time
import logging
import sys

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Region hien tai dang su dung
PORTAL_REGION = (40, 300, 400, 450)  # (left, top, width, height)

def verify_corners():
    left, top, width, height = PORTAL_REGION
    right = left + width
    bottom = top + height

    corners = [
        ("Top-Left", (left, top)),
        ("Top-Right", (right, top)),
        ("Bottom-Right", (right, bottom)),
        ("Bottom-Left", (left, bottom))
    ]

    logging.info(f"Bat dau kiem tra vung: {PORTAL_REGION}")
    logging.info("Chuot se di chuyen den 4 goc cua hinh chu nhat nay.")
    
    # Cho 2 giay de nguoi dung chuan bi
    time.sleep(2)

    for name, pos in corners:
        logging.info(f"Moving to {name}: {pos}")
        pyautogui.moveTo(pos[0], pos[1], duration=0.5)
        time.sleep(1)

    logging.info("Kiem tra ket thuc.")

if __name__ == "__main__":
    try:
        verify_corners()
    except KeyboardInterrupt:
        logging.info("Dung lai boi nguoi dung.")
