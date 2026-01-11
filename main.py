import sys
import logging
import threading
import os
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
def run_scan_and_collect():
    logging.info(f"Starting Scan & Collect (Base: {BASE_PATH})...")
    from scan_and_collect import scan_logic, start_clipboard_listener
    from hud_util import HUD
    hud = HUD()
    from search_util import set_hud
    set_hud(hud)
    scanning_dir = os.path.join(BASE_PATH, "src", "assets", "scanning")
    os.makedirs(scanning_dir, exist_ok=True)
    listener_thread = threading.Thread(target=start_clipboard_listener, args=(scanning_dir,), daemon=True)
    listener_thread.start()
    scanner_thread = threading.Thread(target=scan_logic, args=(hud, BASE_PATH), daemon=True)
    scanner_thread.start()
    try:
        hud.start()
    except KeyboardInterrupt:
        logging.info("Scanner stopped by user.")
def run_auto_script():
    logging.info(f"Starting Auto Script Application (Base: {BASE_PATH})...")
    from auto_script_application import AutoScriptApplication
    from hud_util import HUD
    from search_util import set_hud
    hud = HUD()
    set_hud(hud)
    app = AutoScriptApplication(base_path=BASE_PATH, hud=hud)
    import threading
    app_thread = threading.Thread(target=app.run, daemon=True)
    app_thread.start()
    hud.start()
def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("========================================")
    print("   AUTO SCRIPT MAIN APPLICATION")
    print("========================================")
    print("1. Run Scan & Collect (Define Assets)")
    print("2. Run Auto Script (Start Farming)")
    print("========================================")
    choice = input("Please enter your choice (1 or 2): ").strip()
    if choice == '1':
        run_scan_and_collect()
    elif choice == '2':
        run_auto_script()
    else:
        print("Invalid choice. Please run the application again.")
if __name__ == "__main__":
    main()
