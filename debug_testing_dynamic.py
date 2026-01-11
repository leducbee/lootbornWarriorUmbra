import logging
import sys
import time
import os
import json
import threading
import pyautogui
from search_util import find_all_assets
from hud_util import HUD
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
CONFIG_FILE = "found_coordinate_scanning.txt" 
ASSETS = {
    "challenge": "src/assets/backup/challenge.png",
    "back_fighting": "src/assets/backup/back.png",
    "back_challenge": "src/assets/backup/back.png",
    "back_umbra": "src/assets/backup/back.png",
    "confirm": "src/assets/backup/confirm.png",
    "failed": "src/assets/backup/failed.png",
    "win": "src/assets/backup/win.png",
    "x3_click": "src/assets/backup/x3_click.png",
    "to_umbra": "src/assets/backup/to_umbra.png",
    "tach": "src/assets/backup/tach.png",
    "tach_all": "src/assets/backup/tach_all.png",
    "tach_confirm": "src/assets/backup/tach_confirm.png",
    "lvl3_ruongNguyen_1": "src/assets/backup/text_lvl3_ruongNguyen_1.png",
    "lvl3_ruongNguyen_2": "src/assets/backup/text_lvl3_ruongNguyen_2.png",
    "lvl1_boLacQuaiVat_1": "src/assets/backup/text_lvl1_boLacQuaiVat_1.png",
    "lvl1_boLacQuaiVat_2": "src/assets/backup/text_lvl1_boLacQuaiVat_2.png",
    "lvl1_suoiSinhMenh": "src/assets/backup/text_lvl1_suoiSinhMenh.png",
    "lvl1_suoiTinhThan_1": "src/assets/backup/text_lvl1_suoiTinhThan_1.png",
    "lvl1_suoiTinhThan_2": "src/assets/backup/text_lvl1_suoiTinhThan_2.png",
    "lvl1_teDanCoDai_1": "src/assets/backup/text_lvl1_teDanCoDai_1.png",
    "lvl1_teDanCoDai_2": "src/assets/backup/text_lvl1_teDanCoDai_2.png",
    "lvl2_hangOQuaiVat_1": "src/assets/backup/text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "src/assets/backup/text_lvl2_hangOQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_1": "src/assets/backup/text_lvl3_toChinhQuaiVat_1.png",
    "lvl3_toChinhQuaiVat_2": "src/assets/backup/text_lvl3_toChinhQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_3": "src/assets/backup/text_lvl3_toChinhQuaiVat_3.png",
    "lvl3_toChinhQuaiVat_4": "src/assets/backup/text_lvl3_toChinhQuaiVat_4.png",
    "lvl5_banDoChuaRo": "src/assets/backup/text_lvl5_banDoChuaRo.png"
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
    "lvl2_hangOQuaiVat_1",
    "lvl2_hangOQuaiVat_2",
    "lvl3_toChinhQuaiVat_1",
    "lvl3_toChinhQuaiVat_2",
    "lvl3_toChinhQuaiVat_3",
    "lvl3_toChinhQuaiVat_4",
    "lvl5_banDoChuaRo",
    "win",
    "failed",
    "challenge",
    "back_fighting",
    "back_challenge",
    "back_umbra",
    "confirm",
    "x3_click",
    "to_umbra",
    "tach",
    "tach_all",
    "tach_confirm",
]
known_regions = []
def load_regions():
    regions = []
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    name, coords_str = line.split(":", 1)
                    coords = tuple(map(int, coords_str.strip().strip("()").split(",")))
                    if not name.startswith("lvl"):
                        regions.append((name.strip(), coords))
            regions.sort(key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(PRIORITY_LIST))
            logging.info(f"Loaded {len(regions)} regions from {CONFIG_FILE}")
        except Exception as e:
            logging.error(f"Error loading {CONFIG_FILE}: {e}")
    return regions
def save_regions(regions):
    try:
        sorted_regions = sorted(regions, key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(
            PRIORITY_LIST))
        with open(CONFIG_FILE, "w") as f:
            for name, coords in sorted_regions:
                f.write(f"{name}: {coords}\n")
    except Exception as e:
        logging.error(f"Error saving {CONFIG_FILE}: {e}")
def run_debug_dynamic():
    logging.info("Starting debug_testing_dynamic...")
    global known_regions
    known_regions = load_regions()
    hud = HUD()
    # Logic quét đưa vào thread
    def scan_loop():
        # 3. Limited scan region
        limited_region = (40, 300, 400, 460)
        # limited_region = None
        current_detected_map = {}  # Dùng dict để lưu trữ theo tên asset hoặc vị trí để tránh duplicate
        def check_and_filter(results):
            if not results:
                return []
            return results
        try:
            while True:
                # 1. Quét 1 lần duy nhất cho tất cả ASSETS trên vùng LIMITED (vùng làm việc chính)
                # "quet 1 lan het luon access, thay j thi ve len"
                all_results = find_all_assets(ASSETS, PRIORITY_LIST, confidence=0.7, region=limited_region)
                all_results = check_and_filter(all_results)
                # Kiểm tra xem có asset "challenge" không
                has_challenge = any(res[0] == "challenge" for res in all_results)
                if has_challenge:
                    logging.info("Challenge detected! Clearing HUD and scanning again...")
                    current_detected_map.clear()
                    # Quét lại lần nữa theo yêu cầu: "xong scan again + ve lai"
                    all_results = find_all_assets(ASSETS, PRIORITY_LIST, confidence=0.7, region=limited_region)
                    all_results = check_and_filter(all_results)
                    if not all_results:
                        logging.info("Nothing found in the re-scan after challenge.")
                if all_results:
                    # Thêm tất cả vào HUD
                    for asset_name, loc in all_results:
                        current_detected_map[asset_name] = (asset_name, loc)
                        # Cập nhật known_regions cho non-lvl assets
                        found_idx = -1
                        for idx, (kn_name, kn_loc) in enumerate(known_regions):
                            if kn_name == asset_name:
                                found_idx = idx
                                break
                        if found_idx == -1:
                            known_regions.append((asset_name, loc))
                            logging.info(f"New asset found: {asset_name}")
                            known_regions.sort(
                                key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(
                                    PRIORITY_LIST))
                            save_regions(known_regions)
                        elif known_regions[found_idx][1] != loc:
                            known_regions[found_idx] = (asset_name, loc)
                            save_regions(known_regions)
                else:
                    all_results = []
                # Cập nhật HUD: Vẽ tất cả các item đang có trong map
                current_detected = list(current_detected_map.values())
                hud.update_regions(current_detected, padding=5)
                if not all_results:
                    logging.info("Nothing detected in this scan.")
                time.sleep(4)
        except Exception as e:
            logging.error(f"Scan loop error: {e}")
    scan_thread = threading.Thread(target=scan_loop, daemon=True)
    scan_thread.start()
    try:
        hud.start()
    except KeyboardInterrupt:
        logging.info("Debug stopped by user.")
        hud.stop()
if __name__ == "__main__":
    run_debug_dynamic()
