import logging
import sys
import time
import os
import threading
import json
from search_util import find_all_assets, get_screen_scale, set_hud, click_at
from hud_util import HUD
from PIL import ImageGrab, Image
from pynput import keyboard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
IS_MAC = sys.platform == "darwin"
HOTKEY_STR = "<cmd>+v" if IS_MAC else "<ctrl>+v"
def save_clipboard_image(scanning_dir):
    try:
        img = ImageGrab.grabclipboard()
        if img:
            if isinstance(img, list):
                if len(img) > 0:
                    img = Image.open(img[0])
            _, scale = get_screen_scale()
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
def scan_logic(hud, base_path=None):
    set_hud(hud)
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
    scanning_dir = os.path.join(base_path, "src", "assets", "scanning")
    config_path = os.path.join(base_path, "config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    scan_region = config.get("scan_region")
    recalibrate = False
    if scan_region:
        print(f"--- SCAN REGION FOUND: {scan_region} ---")
        choice = input("Scanning region coordinates identified. Do you want to scan again? (y/n): ").strip().lower()
        if choice == 'y':
            recalibrate = True
            scan_region = None
    if not scan_region or recalibrate:
        logging.info("Scan region not found. Starting calibration...")
        calib_event = threading.Event()
        points = []
        def on_calib_done(pts):
            nonlocal points
            points = pts
            calib_event.set()
        hud.request_calibration(on_calib_done)
        calib_event.wait()
        time.sleep(0.5)
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x = min(xs)
        y = min(ys)
        w = max(xs) - x
        h = max(ys) - y
        scan_region = (x, y, w, h)
        config["scan_region"] = scan_region
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        logging.info(f"Calibration done. Scan region saved: {scan_region}")
    if scan_region:
        logging.info(f"📍 Displaying SCAN_AREA HUD: {scan_region}")
        hud.update_regions([("SCAN_AREA", scan_region)], padding=5)
    assets_paths = {}
    for name, filename in ASSETS_MAPPING.items():
        assets_paths[name] = os.path.join(scanning_dir, filename)
    logging.info(f"Scanner logic started with region {scan_region}. Waiting for assets in '{scanning_dir}'...")
    while True:
        scan_targets = {name: path for name, path in assets_paths.items() if os.path.exists(path)}
        found_on_screen = []
        if scan_targets:
            results = find_all_assets(scan_targets, list(scan_targets.keys()), confidence=0.7, signature=False, region=scan_region)
            if results:
                names = [name for name, loc in results]
                logging.info(f"-> Detected: {', '.join(names)}")
                has_challenge = any(name == "challenge" for name, loc in results)
                if has_challenge:
                    logging.info("Challenge detected!")
            for name, loc in results:
                found_on_screen.append((name, loc))
        render_items = [("SCAN_AREA", scan_region)]
        for name, loc in found_on_screen:
            render_items.append((name, loc))
        hud.update_regions(render_items, padding=5)
        time.sleep(2) 
if __name__ == "__main__":
    hud = HUD()
    base_path = os.path.dirname(os.path.abspath(__file__))
    scanning_dir = os.path.join(base_path, "src", "assets", "scanning")
    os.makedirs(scanning_dir, exist_ok=True)
    listener_thread = threading.Thread(target=start_clipboard_listener, args=(scanning_dir,), daemon=True)
    listener_thread.start()
    scanner_thread = threading.Thread(target=scan_logic, args=(hud, base_path), daemon=True)
    scanner_thread.start()
    try:
        hud.start()
    except KeyboardInterrupt:
        logging.info("Scanner stopped by user.")
