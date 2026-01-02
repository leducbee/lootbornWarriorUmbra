import logging
import sys
import time
import pyautogui
from search_util import find_all_assets

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

ASSETS = {
    "challenge": "src/assets/challenge.png",
    "back": "src/assets/back.png",
    "confirm": "src/assets/confirm.png",
    "failed": "src/assets/failed.png",
    "win": "src/assets/win.png",
    "x3_click": "src/assets/x3_click.png",
    "lvl3_ruongNguyen_1": "src/assets/text_lvl3_ruongNguyen_1.png",
    "lvl3_ruongNguyen_2": "src/assets/text_lvl3_ruongNguyen_2.png",
    "lvl1_boLacQuaiVat_1": "src/assets/text_lvl1_boLacQuaiVat_1.png",
    "lvl1_boLacQuaiVat_2": "src/assets/text_lvl1_boLacQuaiVat_2.png",
    "lvl1_suoiSinhMenh": "src/assets/text_lvl1_suoiSinhMenh.png",
    "lvl1_suoiTinhThan_1": "src/assets/text_lvl1_suoiTinhThan_1.png",
    "lvl1_suoiTinhThan_2": "src/assets/text_lvl1_suoiTinhThan_2.png",
    "lvl1_teDanCoDai_1": "src/assets/text_lvl1_teDanCoDai_1.png",
    "lvl1_teDanCoDai_2": "src/assets/text_lvl1_teDanCoDai_2.png",
    "lvl2_hangOQuaiVat_0": "src/assets/text_lvl2_hangOQuaiVat_0.png",
    "lvl2_hangOQuaiVat_1": "src/assets/text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "src/assets/text_lvl2_hangOQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_0": "src/assets/text_lvl3_toChinhQuaiVat_0.png",
    "lvl3_toChinhQuaiVat_1": "src/assets/text_lvl3_toChinhQuaiVat_1.png",
    "lvl3_toChinhQuaiVat_2": "src/assets/text_lvl3_toChinhQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_3": "src/assets/text_lvl3_toChinhQuaiVat_3.png",
    "lvl3_toChinhQuaiVat_4": "src/assets/text_lvl3_toChinhQuaiVat_4.png",
    "lvl5_banDoChuaRo": "src/assets/text_lvl5_banDoChuaRo.png"
}

PRIORITY_LIST = [
    "lvl3_ruongNguyen_1",
    "lvl3_ruongNguyen_2",
    "lvl1_boLacQuaiVat_1",
    "lvl1_boLacQuaiVat_2",
    "lvl1_suoiSinhMenh",
    "lvl1_suoiTinhThan_1",
    "lvl1_suoiTinhThan_2",
    "lvl1_teDanCoDai_1",
    "lvl1_teDanCoDai_2",
    "lvl2_hangOQuaiVat_0",
    "lvl2_hangOQuaiVat_1",
    "lvl2_hangOQuaiVat_2",
    "lvl3_toChinhQuaiVat_0",
    "lvl3_toChinhQuaiVat_1",
    "lvl3_toChinhQuaiVat_2",
    "lvl3_toChinhQuaiVat_3",
    "lvl3_toChinhQuaiVat_4",
    "lvl5_banDoChuaRo",
    "win",
    "failed"
]

# Global configuration for scanning region (Terminal window)
# Format: (left, top, width, height)
PORTAL_REGION = (40, 300, 400, 450)

def run_debug():
    logging.info(f"Starting debug_testing (Search only region {PORTAL_REGION}, NO clicking)...")
    try:
        while True:
            all_found = find_all_assets(ASSETS, PRIORITY_LIST, confidence=0.7, region=PORTAL_REGION)
            if all_found:
                # Group assets by their "portal type"
                unique_portals = set()
                for asset_name in all_found:
                    base_name = asset_name
                    if "_" in asset_name:
                        parts = asset_name.split("_")
                        if parts[-1].isdigit():
                            base_name = "_".join(parts[:-1])
                    unique_portals.add(base_name)
                
                logging.info(f"Found {len(unique_portals)} portal types: {', '.join(unique_portals)} (Total resources: {len(all_found)})")
                logging.debug(f"Resources: {', '.join(all_found)}")
            elif len(all_found) > 0: # Only log if something was found (e.g. click_and_close or failed which are ignored in unique_portals)
                 logging.info(f"Found {len(all_found)} assets but 0 portal types.")
            
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Debug stopped by user.")

if __name__ == "__main__":
    run_debug()
