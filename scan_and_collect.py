import logging
import sys
import time
import os
import threading
from search_util import find_all_assets
from hud_util import HUD

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Danh sách Assets mục tiêu (Dựa trên debug_testing_dynamic.py)
# Bạn có thể thêm bớt các asset vào dict này
ASSETS_PATHS = {
    "challenge": "src/assets/scanning/challenge.png",
    "back_fighting": "src/assets/scanning/back.png",
    "back_challenge": "src/assets/scanning/back.png",
    "back_umbra": "src/assets/scanning/back.png",
    "confirm": "src/assets/scanning/confirm.png",
    "failed": "src/assets/scanning/failed.png",
    "win": "src/assets/scanning/win.png",
    "x3_click": "src/assets/scanning/x3_click.png",
    "to_umbra": "src/assets/scanning/to_umbra.png",
    "tach": "src/assets/scanning/tach.png",
    "tach_all": "src/assets/scanning/tach_all.png",
    "tach_confirm": "src/assets/scanning/tach_confirm.png",
    "lvl3_ruongNguyen_1": "src/assets/scanning/text_lvl3_ruongNguyen_1.png",
    "lvl3_ruongNguyen_2": "src/assets/scanning/text_lvl3_ruongNguyen_2.png",
    "lvl1_boLacQuaiVat_1": "src/assets/scanning/text_lvl1_boLacQuaiVat_1.png",
    "lvl1_boLacQuaiVat_2": "src/assets/scanning/text_lvl1_boLacQuaiVat_2.png",
    "lvl1_suoiSinhMenh": "src/assets/scanning/text_lvl1_suoiSinhMenh.png",
    "lvl1_suoiTinhThan_1": "src/assets/scanning/text_lvl1_suoiTinhThan_1.png",
    "lvl1_suoiTinhThan_2": "src/assets/scanning/text_lvl1_suoiTinhThan_2.png",
    "lvl1_teDanCoDai_1": "src/assets/scanning/text_lvl1_teDanCoDai_1.png",
    "lvl1_teDanCoDai_2": "src/assets/scanning/text_lvl1_teDanCoDai_2.png",
    "lvl2_hangOQuaiVat_1": "src/assets/scanning/text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "src/assets/scanning/text_lvl2_hangOQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_1": "src/assets/scanning/text_lvl3_toChinhQuaiVat_1.png",
    "lvl3_toChinhQuaiVat_2": "src/assets/scanning/text_lvl3_toChinhQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_3": "src/assets/scanning/text_lvl3_toChinhQuaiVat_3.png",
    "lvl3_toChinhQuaiVat_4": "src/assets/scanning/text_lvl3_toChinhQuaiVat_4.png",
    "lvl5_banDoChuaRo": "src/assets/scanning/text_lvl5_banDoChuaRo.png"
}

def scan_logic(hud):
    logging.info("Scanner logic started. Waiting for assets in 'src/assets/scanning/'...")
    
    while True:
        existing_assets = {}
        missing_assets = []
        
        # 1. Đọc dữ liệu cũ đang có trong file để kiểm tra xem đã có tọa độ chưa
        stored_coordinates = {}
        if os.path.exists("found_coordinate_scanning.txt"):
            try:
                with open("found_coordinate_scanning.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if ":" in line:
                            name, coords = line.split(":", 1)
                            name = name.strip()
                            # Loại bỏ các item lvl cũ nếu lỡ có trong file
                            if not name.startswith("lvl"):
                                stored_coordinates[name] = coords.strip()
            except Exception as e:
                logging.error(f"Error reading coordinate file: {e}")

        # 2. Kiểm tra sự tồn tại của file vật lý VÀ tọa độ trong file txt
        for name, path in ASSETS_PATHS.items():
            file_exists = os.path.exists(path)
            
            # Đối với các asset lvl, ta coi như coord_exists luôn True nếu file vật lý tồn tại
            # vì chúng ta không lưu chúng vào txt mà dùng portal thay thế.
            if name.startswith("lvl"):
                coord_exists = True 
            else:
                coord_exists = name in stored_coordinates
            
            if file_exists:
                if coord_exists:
                    existing_assets[name] = path
                else:
                    # File có nhưng chưa có tọa độ trong txt -> Vẫn báo missing để user biết cần tìm UI
                    missing_assets.append(f"{name}(no_coord)")
            else:
                missing_assets.append(name)
        
        # 3. In báo cáo trạng thái ra Console
        if missing_assets:
            logging.warning(f"MISSING assets (file or coord): {', '.join(missing_assets)}")
        
        # 4. Quét màn hình cho những assets đang có file (luôn quét những cái có file để update tọa độ)
        # Ở bước này ta quét tất cả những gì CÓ FILE để lấp đầy file txt
        scan_targets = {name: path for name, path in ASSETS_PATHS.items() if os.path.exists(path)}
        
        found_on_screen = []
        portal_regions = {"left_portal_text": None, "right_portal_text": None}
        
        if scan_targets:
            # Tắt HUD trước khi quét để tránh ảnh hưởng đến việc nhận diện hình ảnh
            hud.update_regions([], padding=0)
            
            results = find_all_assets(scan_targets, list(scan_targets.keys()), confidence=0.7)
            if results:
                names = [name for name, loc in results]
                logging.info(f"-> Detected: {', '.join(names)}")
                
            for name, loc in results:
                found_on_screen.append((name, loc))
                
                # Logic xác định portal dựa trên tọa độ X của các asset level
                if name.startswith("lvl"):
                    p_name = "left_portal_text" if loc[0] < 220 else "right_portal_text"
                    # Cập nhật hoặc tối ưu hóa vùng portal (Bounding Box đơn giản hoặc lấy vị trí mới nhất)
                    portal_regions[p_name] = loc

        # 4. Cập nhật HUD (Vẽ khung lên màn hình)
        # Hợp nhất found_on_screen với portal_regions để render
        render_items = list(found_on_screen)
        for p_name, p_loc in portal_regions.items():
            if p_loc:
                # Kiểm tra xem portal này đã có trong list chưa (tránh vẽ đè nếu trùng tên)
                if not any(item[0] == p_name for item in render_items):
                    render_items.append((p_name, p_loc))

        if render_items:
            hud.update_regions(render_items, padding=5)
        else:
            hud.update_regions([], padding=5)

        # 5. Lưu vào file found_coordinate_scanning.txt (Cập nhật cuốn chiếu)
        try:
            # Cập nhật với những item mới tìm thấy (bao gồm cả portal)
            if render_items:
                for name, loc in render_items:
                    # Không lưu các asset bắt đầu bằng "lvl" vào file txt vì đã có portal đại diện
                    if not name.startswith("lvl"):
                        stored_coordinates[name] = str(loc)
                
                # Ghi lại toàn bộ vào file
                with open("found_coordinate_scanning.txt", "w") as f:
                    for name, loc_str in stored_coordinates.items():
                        f.write(f"{name}: {loc_str}\n")
                logging.info(f"Updated and merged coordinates to found_coordinate_scanning.txt")
        except Exception as e:
            logging.error(f"Error updating coordinate file: {e}")
        
        if not found_on_screen and not missing_assets:
            logging.info("All files present, but nothing detected on screen.")
            
        time.sleep(2) # Lặp lại sau 2 giây

if __name__ == "__main__":
    # Khởi tạo HUD (Cần chạy trên main thread cho macOS/PyQt5)
    hud = HUD()
    
    # Chạy vòng lặp quét trong một thread riêng để không block UI của HUD
    scanner_thread = threading.Thread(target=scan_logic, args=(hud,), daemon=True)
    scanner_thread.start()
    
    try:
        # Bắt đầu hiển thị HUD
        hud.start()
    except KeyboardInterrupt:
        logging.info("Scanner stopped by user.")
