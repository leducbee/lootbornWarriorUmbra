import sys
import logging
import threading

def run_scan_and_collect():
    logging.info("Starting Scan & Collect...")
    from scan_and_collect import scan_logic
    from hud_util import HUD
    
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

def run_auto_script():
    logging.info("Starting Auto Script Application...")
    from auto_script_application import AutoScriptApplication
    
    app = AutoScriptApplication()
    app.run()

def main():
    # Cấu hình Logging cơ bản để thấy output
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
