import pyautogui
import time
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
PORTAL_REGIONS = [
    (40, 300, 400, 450)
]
def verify_corners(regions):
    if not isinstance(regions, list):
        regions = [regions]
    logging.info(f"Bat dau kiem tra {len(regions)} vung.")
    logging.info("Chuot se di chuyen den 4 goc cua tung hinh chu nhat.")
    time.sleep(2)
    for i, region in enumerate(regions):
        left, top, width, height = region
        right = left + width
        bottom = top + height
        corners = [
            ("Top-Left", (left, top)),
            ("Top-Right", (right, top)),
            ("Bottom-Right", (right, bottom)),
            ("Bottom-Left", (left, bottom))
        ]
        logging.info(f"--- Kiem tra Region {i+1}: {region} ---")
        for name, pos in corners:
            logging.info(f"Moving to {name}: {pos}")
            pyautogui.moveTo(pos[0], pos[1], duration=0.5)
            time.sleep(0.5)
    logging.info("Kiem tra tat ca cac vung ket thuc.")
if __name__ == "__main__":
    try:
        verify_corners(PORTAL_REGIONS)
    except KeyboardInterrupt:
        logging.info("Dung lai boi nguoi dung.")
