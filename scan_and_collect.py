import logging
import sys
import time
import os
import threading
from search_util import find_all_assets, get_screen_scale
from hud_util import HUD
from PIL import ImageGrab, Image
from pynput import keyboard

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Phím chức năng theo OS
IS_MAC = sys.platform == "darwin"
HOTKEY_STR = "<cmd>+v" if IS_MAC else "<ctrl>+v"

def save_clipboard_image(scanning_dir):
    try:
        img = ImageGrab.grabclipboard()
        if img:
            # Nếu là list (trên một số hệ thống khi copy file)
            if isinstance(img, list):
                if len(img) > 0:
                    img = Image.open(img[0])
            
            # Lấy tỷ lệ scale của màn hình
            _, scale = get_screen_scale()
            
            # Nếu tỷ lệ scale > 1 (ví dụ Retina 2.0), chúng ta cần resize ảnh về tỷ lệ logical
            # vì logic find_image sẽ tự động scale lên theo tỷ lệ hệ thống khi quét.
            if scale > 1.0:
                new_size = (int(img.width / scale), int(img.height / scale))
                logging.info(f"📏 Resizing clipboard image from {img.width}x{img.height} to {new_size[0]}x{new_size[1]} (Scale: {scale})")
                img = img.resize(new_size, Image.LANCZOS)
            
            save_path = os.path.join(scanning_dir, "image.png")
            img.save(save_path, "PNG")
            logging.info(f"🎨 Clipboard image saved to: {save_path}")
        else:
            logging.warning("📋 No image found in clipboard.")
    except Exception as e:
        logging.error(f"❌ Error saving clipboard image: {e}")

def start_clipboard_listener(scanning_dir):
    logging.info(f"Hotkeys enabled: {HOTKEY_STR} to save clipboard as img.png")
    
    def on_activate():
        save_clipboard_image(scanning_dir)

    with keyboard.GlobalHotKeys({
        HOTKEY_STR: on_activate
    }) as h:
        h.join()

# Danh sách Assets mục tiêu (Dựa trên debug_testing_dynamic.py)
# Bạn có thể thêm bớt các asset vào dict này
ASSETS_MAPPING = {
    "challenge": "challenge.png",
    "back_fighting": "back.png",
    "back_challenge": "back.png",
    "back_umbra": "back.png",
    "confirm": "confirm.png",
    "failed": "failed.png",
    "win": "win.png",
    "x3_click": "x3_click.png",
    "to_umbra": "to_umbra.png",
    "tach": "tach.png",
    "tach_all": "tach_all.png",
    "tach_confirm": "tach_confirm.png",
    "lvl3_ruongNguyen_1": "text_lvl3_ruongNguyen_1.png",
    "lvl3_ruongNguyen_2": "text_lvl3_ruongNguyen_2.png",
    "lvl1_boLacQuaiVat_1": "text_lvl1_boLacQuaiVat_1.png",
    "lvl1_boLacQuaiVat_2": "text_lvl1_boLacQuaiVat_2.png",
    "lvl1_suoiSinhMenh": "text_lvl1_suoiSinhMenh.png",
    "lvl1_suoiTinhThan_1": "text_lvl1_suoiTinhThan_1.png",
    "lvl1_suoiTinhThan_2": "text_lvl1_suoiTinhThan_2.png",
    "lvl1_teDanCoDai_1": "text_lvl1_teDanCoDai_1.png",
    "lvl1_teDanCoDai_2": "text_lvl1_teDanCoDai_2.png",
    "lvl2_hangOQuaiVat_1": "text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "text_lvl2_hangOQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_1": "text_lvl3_toChinhQuaiVat_1.png",
    "lvl3_toChinhQuaiVat_2": "text_lvl3_toChinhQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_3": "text_lvl3_toChinhQuaiVat_3.png",
    "lvl3_toChinhQuaiVat_4": "text_lvl3_toChinhQuaiVat_4.png",
    "lvl5_banDoChuaRo": "text_lvl5_banDoChuaRo.png"
}

def optimize_portal_region(current_loc, new_loc):
    """
    Tối ưu hóa vùng portal bằng cách mở rộng bounding box bao phủ cả vùng cũ và mới.
    Nếu vùng mới đã nằm trọn trong vùng cũ, không cần thay đổi.
    """
    if not current_loc:
        return new_loc
    
    x1, y1, w1, h1 = current_loc
    x2, y2, w2, h2 = new_loc
    
    # Kiểm tra xem new_loc đã nằm trong current_loc chưa
    # (x2 >= x1) và (y2 >= y1) và (x2+w2 <= x1+w1) và (y2+h2 <= y1+h1)
    if x2 >= x1 and y2 >= y1 and (x2 + w2) <= (x1 + w1) and (y2 + h2) <= (y1 + h1):
        return current_loc

    # Nếu không nằm trong, thực hiện mở rộng vùng (Extend)
    new_x = min(x1, x2)
    new_y = min(y1, y2)
    new_w = max(x1 + w1, x2 + w2) - new_x
    new_h = max(y1 + h1, y2 + h2) - new_y
    
    return (new_x, new_y, new_w, new_h)

def scan_logic(hud, base_path=None):
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Cấu hình đường dẫn
    scanning_dir = os.path.join(base_path, "src", "assets", "scanning")
    coord_file = os.path.join(base_path, "found_coordinate_scanning.txt")
    
    # Xây dựng ASSETS_PATHS dựa trên base_path
    assets_paths = {}
    for name, filename in ASSETS_MAPPING.items():
        assets_paths[name] = os.path.join(scanning_dir, filename)

    logging.info(f"Scanner logic started. Waiting for assets in '{scanning_dir}'...")
    
    stored_coordinates = {}
    portal_regions = {"left_portal_text": None, "right_portal_text": None}

    while True:
        existing_assets = {}
        missing_assets = []
        
        # 1. Đọc dữ liệu cũ đang có trong file để kiểm tra xem đã có tọa độ chưa
        if os.path.exists(coord_file):
            try:
                with open(coord_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if ":" in line:
                            name, coords_str = line.split(":", 1)
                            name = name.strip()
                            coords_str = coords_str.strip()
                            
                            # Cập nhật stored_coordinates (trừ các item lvl)
                            if not name.startswith("lvl"):
                                stored_coordinates[name] = coords_str
                                
                            # Phục hồi portal_regions từ file
                            if name in portal_regions:
                                try:
                                    # Chuyển string "(x, y, w, h)" về tuple
                                    val = tuple(map(int, coords_str.strip("() ").split(",")))
                                    portal_regions[name] = val
                                except:
                                    pass
            except Exception as e:
                logging.error(f"Error reading coordinate file: {e}")

        # 2. Kiểm tra sự tồn tại của file vật lý VÀ tọa độ trong file txt
        for name, path in assets_paths.items():
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
        scan_targets = {name: path for name, path in assets_paths.items() if os.path.exists(path)}
        
        found_on_screen = []
        
        if scan_targets:
            # Tắt HUD trước khi quét để tránh ảnh hưởng đến việc nhận diện hình ảnh
            hud.update_regions([], padding=0)
            
            results = find_all_assets(scan_targets, list(scan_targets.keys()), confidence=0.7)
            if results:
                names = [name for name, loc in results]
                logging.info(f"-> Detected: {', '.join(names)}")
                
                # Logic phát hiện "challenge" để clear HUD
                has_challenge = any(name == "challenge" for name, loc in results)
                if has_challenge:
                    logging.info("Challenge detected! Clearing current portal regions for recalibration...")
                    portal_regions = {"left_portal_text": None, "right_portal_text": None}

            for name, loc in results:
                found_on_screen.append((name, loc))
                
                # Logic xác định portal dựa trên tọa độ X của các asset level
                if name.startswith("lvl"):
                    p_name = "left_portal_text" if loc[0] < 220 else "right_portal_text"
                    # Tối ưu hóa vùng portal (Bounding Box mở rộng)
                    portal_regions[p_name] = optimize_portal_region(portal_regions[p_name], loc)

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
                with open(coord_file, "w") as f:
                    for name, loc_str in stored_coordinates.items():
                        f.write(f"{name}: {loc_str}\n")
                logging.info(f"Updated and merged coordinates to {coord_file}")
        except Exception as e:
            logging.error(f"Error updating coordinate file: {e}")
        
        if not found_on_screen and not missing_assets:
            logging.info("All files present, but nothing detected on screen.")
            
        time.sleep(2) # Lặp lại sau 2 giây

if __name__ == "__main__":
    # Khởi tạo HUD (Cần chạy trên main thread cho macOS/PyQt5)
    hud = HUD()
    
    # Xác định scanning_dir để truyền vào listener
    base_path = os.path.dirname(os.path.abspath(__file__))
    scanning_dir = os.path.join(base_path, "src", "assets", "scanning")
    os.makedirs(scanning_dir, exist_ok=True)

    # Chạy listener bàn phím trong thread riêng
    listener_thread = threading.Thread(target=start_clipboard_listener, args=(scanning_dir,), daemon=True)
    listener_thread.start()
    
    # Chạy vòng lặp quét trong một thread riêng để không block UI của HUD
    scanner_thread = threading.Thread(target=scan_logic, args=(hud, base_path), daemon=True)
    scanner_thread.start()
    
    try:
        # Bắt đầu hiển thị HUD
        hud.start()
    except KeyboardInterrupt:
        logging.info("Scanner stopped by user.")
