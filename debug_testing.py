import logging
import sys
import time

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
    "lvl2_hangOQuaiVat_1": "src/assets/text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "src/assets/text_lvl2_hangOQuaiVat_2.png",
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
    "back",
    "confirm",
    "x3_click"
]

# Global configuration for scanning regions
# Format: list of (left, top, width, height)
PORTAL_REGIONS = [
    (123, 343, 75, 26),  # left text
    (277, 343, 69, 27),  # right text
    (146, 394, 29, 29),  # left icon
    (290, 396, 23, 26),  # righ icon
    (76, 729, 36, 33),  # back
    (188, 387, 90, 30),  # fail
    (176, 722, 112, 20),  # challenge
    (174, 339, 120, 26),  # win
    (310, 619, 49, 33),  # x3_click
    (85, 540, 58, 21),  # tach
    (273, 487, 66, 24),  # all
    (321, 537, 60, 26),  # confirm tach
    (243, 511, 93, 34),  # confirm
]


def run_debug():
    logging.info(f"Starting debug_testing (Search {len(PORTAL_REGIONS)} regions, NO clicking)...")
    try:
        while True:
            all_results = []
            for i, region in enumerate(PORTAL_REGIONS):
                all_found_raw = find_all_assets(ASSETS, PRIORITY_LIST, confidence=0.7, region=region)
                all_found = [name for name, loc in all_found_raw]
                logging.info(f"Region {i + 1}: Found {len(all_found)} assets.")
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

                    all_results.append({
                        "index": i + 1,
                        "region": region,
                        "portals": list(unique_portals),
                        "count": len(all_found)
                    })

            if all_results:
                logging.info(f"--- Scan results ({len(all_results)} regions with findings) ---")
                for res in all_results:
                    logging.info(
                        f"Region {res['index']} {res['region']}: Found {len(res['portals'])} portal types: {', '.join(res['portals'])} (Total: {res['count']})")

            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Debug stopped by user.")


if __name__ == "__main__":
    run_debug()
