import sys
import logging
import threading
import os

# Xác định đường dẫn gốc của ứng dụng
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file executable
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # Nếu đang chạy script .py bình thường
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def run_scan_and_collect():
    logging.info(f"Starting Scan & Collect (Base: {BASE_PATH})...")
    from scan_and_collect import scan_logic, start_clipboard_listener
    from hud_util import HUD
    
    # Khởi tạo HUD (Cần chạy trên main thread cho macOS/PyQt5)
    hud = HUD()
    
    # Thư mục scanning để lưu ảnh clipboard
    scanning_dir = os.path.join(BASE_PATH, "src", "assets", "scanning")
    os.makedirs(scanning_dir, exist_ok=True)

    # Chạy listener bàn phím trong thread riêng
    listener_thread = threading.Thread(target=start_clipboard_listener, args=(scanning_dir,), daemon=True)
    listener_thread.start()
    
    # Chạy vòng lặp quét trong một thread riêng để không block UI của HUD
    scanner_thread = threading.Thread(target=scan_logic, args=(hud, BASE_PATH), daemon=True)
    scanner_thread.start()
    
    try:
        # Bắt đầu hiển thị HUD
        hud.start()
    except KeyboardInterrupt:
        logging.info("Scanner stopped by user.")

def run_auto_script():
    logging.info(f"Starting Auto Script Application (Base: {BASE_PATH})...")
    from auto_script_application import AutoScriptApplication
    
    app = AutoScriptApplication(base_path=BASE_PATH)
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
