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

# Danh sach cac Region hien tai dang su dung
PORTAL_REGIONS = [
    # (123, 343, 75, 26),   # left text
    # (277, 343, 69, 27),   # right text
    # (146, 394, 29, 29),   # left icon
    # (297, 394, 30, 26),   # righ icon
    # (76, 729, 36, 33),    # back
    # (188, 387, 90, 30),   # fail
    # (176, 722, 112, 20),  # challenge
    # (174, 339, 120, 26),  # win
    # (310, 619, 49, 33),   # x3_click
    # (85, 540, 58, 21),    # tach
    # (273, 487, 66, 24),   # all
    # (321, 537, 60, 26),   # confirm tach
    # (243, 511, 93, 34), # confirm
    # testing
    (40, 300, 400, 450)
]

def verify_corners(regions):
    if not isinstance(regions, list):
        regions = [regions]

    logging.info(f"Bat dau kiem tra {len(regions)} vung.")
    logging.info("Chuot se di chuyen den 4 goc cua tung hinh chu nhat.")
    
    # Cho 2 giay de nguoi dung chuan bi
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
        # Input dau vao la 1 list cua array/tuple
        verify_corners(PORTAL_REGIONS)
    except KeyboardInterrupt:
        logging.info("Dung lai boi nguoi dung.")
