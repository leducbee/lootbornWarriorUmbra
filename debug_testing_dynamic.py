import logging
import sys
import time
import os
import json
import threading
import pyautogui
from search_util import find_all_assets
from hud_util import HUD

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

CONFIG_FILE = "initial_coordinates.txt"
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

# 2. Known regions loaded from file
known_regions = []
# Portal regions for lvl_xx assets
portal_regions = {
    "left_portal_text": None,  # (x, y, w, h)
    "right_portal_text": None
}


def load_regions():
    """Tải danh sách các vùng từ file config."""
    regions = []
    global portal_regions
    portal_regions = {"left_portal_text": None, "right_portal_text": None}

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    name, coords_str = line.split(":", 1)
                    coords = tuple(map(int, coords_str.strip().strip("()").split(",")))

                    if name in portal_regions:
                        portal_regions[name] = coords
                    elif not name.startswith("lvl"):
                        regions.append((name.strip(), coords))

            # Sắp xếp theo PRIORITY_LIST cho các vùng non-lvl
            regions.sort(key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(PRIORITY_LIST))

            logging.info(f"Loaded {len(regions)} non-lvl regions and portals from {CONFIG_FILE}")
        except Exception as e:
            logging.error(f"Error loading {CONFIG_FILE}: {e}")
    return regions


def save_regions(regions):
    """Lưu các vùng non-lvl và portal regions vào file config."""
    try:
        # Sắp xếp các vùng non-lvl
        sorted_regions = sorted(regions, key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(
            PRIORITY_LIST))
        with open(CONFIG_FILE, "w") as f:
            # Lưu portal regions trước
            for name, coords in portal_regions.items():
                if coords:
                    f.write(f"{name}: {coords}\n")
            # Lưu các vùng khác
            for name, coords in sorted_regions:
                f.write(f"{name}: {coords}\n")
    except Exception as e:
        logging.error(f"Error saving {CONFIG_FILE}: {e}")


def optimize_portal_region(portal_name, new_location):
    """Cập nhật và tối ưu hóa vùng portal dựa trên asset lvl tìm thấy."""
    global portal_regions
    if portal_regions[portal_name] is None:
        portal_regions[portal_name] = new_location
        return True

    # Logic tối ưu: mở rộng vùng portal để luôn bao phủ cả vùng cũ và vị trí mới (Bounding Box)
    curr = portal_regions[portal_name]

    x1, y1, w1, h1 = curr
    x2, y2, w2, h2 = new_location

    new_x = min(x1, x2)
    new_y = min(y1, y2)
    new_w = max(x1 + w1, x2 + w2) - new_x
    new_h = max(y1 + h1, y2 + h2) - new_y

    new_rect = (new_x, new_y, new_w, new_h)

    if new_rect != curr:
        portal_regions[portal_name] = new_rect
        return True
    return False


def filter_optimal_regions(results):
    """
    Lọc các vùng trùng lặp hoặc bị bao hàm cho các asset lvl_xx.
    Giữ lại vùng lớn nhất đại diện cho mỗi vị trí logic.
    """
    if not results:
        return []

    def is_contained(r1, r2):
        # r1: (x, y, w, h)
        # Kiểm tra xem r1 có bị bao hàm bởi r2 không (hoặc gần như trùng khớp)
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return x1 >= x2 - 5 and y1 >= y2 - 5 and (x1 + w1) <= (x2 + w2) + 5 and (y1 + h1) <= (y2 + h2) + 5

    def get_area(r):
        return r[2] * r[3]

    def get_base_name(name):
        if name.startswith("lvl"):
            # Ví dụ: lvl3_toChinhQuaiVat_1 -> lvl3_toChinhQuaiVat
            parts = name.split("_")
            if len(parts) > 2:
                return "_".join(parts[:-1])
        return name

    # Phân loại: lvl_xx và các loại khác
    lvl_results = [res for res in results if res[0].startswith("lvl")]
    other_results = [res for res in results if not res[0].startswith("lvl")]

    if not lvl_results:
        return results

    optimized_lvl = []

    # Nhóm theo base_name
    groups = {}
    for name, loc in lvl_results:
        base = get_base_name(name)
        if base not in groups:
            groups[base] = []
        groups[base].append((name, loc))

    for base, items in groups.items():
        # Trong mỗi nhóm, ta muốn lọc ra các vị trí khác nhau
        # Ví dụ: nếu có nhiều cái ở cùng 1 chỗ (trùng lặp/bao hàm), chỉ lấy cái to nhất

        # Sắp xếp theo diện tích giảm dần để ưu tiên cái to nhất
        items.sort(key=lambda x: get_area(x[1]), reverse=True)

        group_kept = []
        for name, loc in items:
            is_redundant = False
            for k_name, k_loc in group_kept:
                # Nếu loc bị bao hàm bởi k_loc (cái to hơn đã giữ), thì loc là dư thừa
                if is_contained(loc, k_loc):
                    is_redundant = True
                    break
            if not is_redundant:
                group_kept.append((name, loc))

        optimized_lvl.extend(group_kept)

    return optimized_lvl + other_results


def run_debug_dynamic():
    logging.info("Starting debug_testing_dynamic with Portal Logic and HUD...")

    global known_regions, portal_regions
    known_regions = load_regions()

    hud = HUD()

    # Logic quét đưa vào thread
    def scan_loop():
        # 3. Limited scan region
        # limited_region = (40, 300, 400, 460)
        limited_region = None

        current_detected_map = {}  # Dùng dict để lưu trữ theo tên asset hoặc vị trí để tránh duplicate

        def check_and_filter(results):
            """Hỗ trợ kiểm tra 2 portal và gọi lọc nếu thỏa mãn."""
            if not results:
                return []

            lvl_res = [res for res in results if res[0].startswith("lvl")]

            # Kiểm tra xem có ít nhất 1 cái bên trái (<220) và ít nhất 1 cái bên phải (>=220) không.
            has_left = any(r[1][0] < 220 for r in lvl_res)
            has_right = any(r[1][0] >= 220 for r in lvl_res)

            if has_left and has_right:
                logging.info("Detected 2 unique portals (left & right). Filtering regions...")
                return filter_optimal_regions(results)

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
                    # Tách riêng lvl_assets để xử lý logic left/right portal
                    lvl_findings = [res for res in all_results if res[0].startswith("lvl")]
                    non_lvl_findings = [res for res in all_results if not res[0].startswith("lvl")]

                    if lvl_findings:
                        # Kiểm tra xem có đủ 2 portal không để thực hiện update portal_regions
                        has_left = any(res[1][0] < 220 for res in lvl_findings)
                        has_right = any(res[1][0] >= 220 for res in lvl_findings)

                        if has_left and has_right:
                            # Phân loại và cập nhật portal_regions
                            for asset_name, loc in lvl_findings:
                                p_name = "left_portal_text" if loc[0] < 220 else "right_portal_text"
                                current_detected_map[f"{p_name}_{asset_name}"] = (asset_name, loc)
                                if optimize_portal_region(p_name, loc):
                                    save_regions(known_regions)
                        else:
                            # Nếu không đủ 2 portal, chỉ thêm vào HUD mà không update portal_regions (theo yêu cầu)
                            for asset_name, loc in lvl_findings:
                                p_name = "left_portal_text" if loc[0] < 220 else "right_portal_text"
                                current_detected_map[f"{p_name}_{asset_name}"] = (asset_name, loc)

                    # Xử lý các asset không phải lvl
                    for asset_name, loc in non_lvl_findings:
                        current_detected_map[asset_name] = (asset_name, loc)

                        # Cập nhật known_regions cho non-lvl assets
                        found_idx = -1
                        for idx, (kn_name, kn_loc) in enumerate(known_regions):
                            if kn_name == asset_name:
                                found_idx = idx
                                break

                        if found_idx == -1:
                            known_regions.append((asset_name, loc))
                            logging.info(f"New non-lvl asset found: {asset_name}")
                            known_regions.sort(
                                key=lambda x: PRIORITY_LIST.index(x[0]) if x[0] in PRIORITY_LIST else len(
                                    PRIORITY_LIST))
                            save_regions(known_regions)
                        elif known_regions[found_idx][1] != loc:
                            known_regions[found_idx] = (asset_name, loc)
                            save_regions(known_regions)
                else:
                    lvl_findings = []
                    non_lvl_findings = []

                # 2. Quét bổ sung tại các Portal Regions đã biết (để đảm bảo không bỏ sót khi chúng nằm ngoài limited_region nếu có)
                # Tuy nhiên, theo yêu cầu "quet 1 lan", ta tập trung vào kết quả của all_results.
                # Nếu người dùng muốn tối ưu tốc độ, việc quét portal riêng biệt vẫn tốt, 
                # nhưng ở đây ta tuân thủ "quet 1 lan".

                # Cập nhật HUD: Vẽ tất cả các item đang có trong map + 2 portal regions mặc định
                current_detected = list(current_detected_map.values())

                # Luôn thêm 2 portal regions vào HUD để hiển thị vùng xanh lá cây
                for p_name in ["left_portal_text", "right_portal_text"]:
                    if portal_regions[p_name]:
                        # Tránh duplicate nếu nó đã có trong current_detected_map với tên chính xác đó
                        exists = False
                        for name, _ in current_detected:
                            if name == p_name:
                                exists = True
                                break
                        if not exists:
                            current_detected.append((p_name, portal_regions[p_name]))

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
