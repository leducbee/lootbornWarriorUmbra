import time
import logging
import sys
from pynput import keyboard
import pyautogui
from search_util import wait_and_click, find_image, click_at, find_multiple_assets, find_all_assets
import asyncio
from telegram_notifier import send_telegram_message, send_telegram_photo
from telegram import Bot
import os

# Telegram Config (Nên để vào file config riêng nếu có)
TELEGRAM_TOKEN = "xx" # Dien token vao day
TELEGRAM_CHAT_ID = "xx" # Dien chat id vao day

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose HTTP logs from telegram library
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

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


# Global configuration
PORTAL_REGION = (40, 300, 400, 450)  # Vung cua so Redfinger App tren man hinh 1440x900
DEFAULT_CONFIDENCE = 0.7

class AutoScriptApp:
    def __init__(self):
        self.running = True
        self.paused = False
        self.listener = None
        self.portal_count = 0
        self.found_ruong_nguyen = False
        self.ruong_nguyen_count = 0  # Biến đếm số lần hoàn thành Rương Nguyên thành công
        self.route_count = 0  # Biến đếm tổng số lần chạy (route)
        self.last_update_id = -1
        self.should_restart_route = False
        
        # Khởi tạo last_update_id để bỏ qua các lệnh cũ gửi trước khi chạy script
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                logging.info("Initializing Telegram bot and clearing old updates...")
                bot = Bot(token=TELEGRAM_TOKEN)
                # Chạy async trong init đồng bộ
                loop = asyncio.new_event_loop()
                updates = loop.run_until_complete(self._get_latest_update_id(bot))
                loop.close()
                if updates:
                    self.last_update_id = updates[-1].update_id
                    logging.info(f"Telegram initialized. Ignoring updates before ID: {self.last_update_id}")
            except Exception as e:
                logging.error(f"Failed to initialize Telegram updates: {e}")

    async def _get_latest_update_id(self, bot):
        async with bot:
            return await bot.get_updates(offset=-1, timeout=1)

    async def check_telegram_commands(self):
        """
        Kiểm tra tin nhắn từ Telegram để điều khiển ứng dụng.
        'stop' -> Tạm dừng (paused = True)
        'again' -> Tiếp tục (paused = False)
        """
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            return

        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            async with bot:
                updates = await bot.get_updates(offset=self.last_update_id + 1, timeout=1)
                for update in updates:
                    self.last_update_id = update.update_id
                    if update.message and str(update.message.chat_id) == TELEGRAM_CHAT_ID:
                        text = update.message.text.lower().strip()
                        logging.info(f"Received Telegram command: '{text}' (ID: {update.update_id})")
                        if text == "stop":
                            if not self.paused:
                                self.paused = True
                                logging.info(f"Pausing application due to command ID: {update.update_id}")
                                await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🛑 Application đã tạm dừng theo lệnh của bạn.")
                        elif text == "again":
                            if self.paused:
                                self.paused = False
                                self.should_restart_route = True
                                logging.info(f"Restarting route due to command ID: {update.update_id}")
                                await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "▶️ Application đang khởi động lại route mới...")
                            else:
                                self.should_restart_route = True
                                logging.info(f"Forcing new route due to 'again' command (ID: {update.update_id})")
                                await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🔄 Đang ép buộc bắt đầu lại route mới...")
                        elif text == "exit":
                            self.running = False
                            self.paused = False # Break pause loop if any
                            logging.info(f"Stopping application due to 'exit' command (ID: {update.update_id})")
                            await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🔌 Application đang đóng hoàn toàn theo lệnh của bạn.")
                        elif text == "capture":
                            logging.info(f"Capturing screen due to command ID: {update.update_id}")
                            try:
                                screenshot_path = f"manual_capture_{update.update_id}.png"
                                img = pyautogui.screenshot()
                                img.save(screenshot_path)
                                if os.path.exists(screenshot_path):
                                    await send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, screenshot_path, caption=f"📸 Screenshot manual (ID: {update.update_id})")
                                    os.remove(screenshot_path)
                                else:
                                    await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "❌ Lỗi: Không thể lưu ảnh chụp màn hình.")
                            except Exception as e:
                                logging.error(f"Error during manual capture: {e}")
                                await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"❌ Lỗi khi capture: {e}")
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra lệnh Telegram: {e}")

    def on_press(self, key):
        if key == keyboard.Key.esc:
            logging.info("ESC key pressed. Stopping application...")
            self.running = False
            if self.listener:
                self.listener.stop()
            return False

    def wait_for_end_of_route(self, is_ruong_nguyen=False):
        """
        Chờ đợi Portal mới xuất hiện HOẶC kết quả Boss (Thắng/Thua).
        Trả về True nếu thấy 2 portal (tiếp tục wave), False nếu đã kết thúc route.
        """
        logging.info("Waiting for next portals or Boss result...")
        start_time = time.time()
        win_detected = False
        
        while time.time() - start_time < 60: # Chờ tối đa 60s cho Boss fight
            # 0. Kiểm tra lệnh từ Telegram
            asyncio.run(self.check_telegram_commands())
            if self.paused or not self.running or self.should_restart_route:
                return False

            # 1. Kiểm tra chiến thắng
            if not win_detected:
                if find_image(ASSETS["win"], timeout=1):
                    logging.info("Boss defeated! Win detected.")
                    win_detected = True
                    if is_ruong_nguyen:
                        self.ruong_nguyen_count += 1
                        logging.info(f"Ruong Nguyen completed! Total: {self.ruong_nguyen_count}")
            
            # 2. Nếu đã thấy win, tìm và click x3_click
            if win_detected:
                logging.info("Searching for x3_click button...")
                if wait_and_click(ASSETS["x3_click"], timeout=10, confidence=DEFAULT_CONFIDENCE):
                    logging.info("Clicked x3_click!")
                    time.sleep(1)
                    return False
                else:
                    logging.warning("Win was detected but x3_click not found. Retrying win detection or waiting...")
                    # Co the win.png van con do, hoac x3_click chua hien. Loop tiep.
                    win_detected = False # Reset de check lai win hoac tiep tuc doi
            
            # 3. Kiểm tra thất bại (quet toan man hinh)
            if find_image(ASSETS["failed"], timeout=1):
                logging.info("Route failed! Clicking 'Failed'...")
                wait_and_click(ASSETS["failed"], timeout=5)
                return False

            # 4. Kiểm tra xem có 2 portal mới chưa (quet o vung hardcode)
            all_found = find_all_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE, region=PORTAL_REGION)
            
            unique_portals = set()
            for asset_name in all_found:
                if asset_name in ["win", "failed"]:
                    continue
                base_name = asset_name
                if "_" in asset_name:
                    parts = asset_name.split("_")
                    if parts[-1].isdigit():
                        base_name = "_".join(parts[:-1])
                unique_portals.add(base_name)

            if len(unique_portals) >= 2:
                return True
            
            if not self.running:
                break
            time.sleep(1)
        return False

    def process_action(self):
        """
        Main auto route logic.
        """
        self.portal_count = 0
        self.targeted_ruong_nguyen = False

        # 1. Click challenge
        challenge_fail_count = 0
        while self.running:
            # 0. Kiểm tra lệnh từ Telegram
            asyncio.run(self.check_telegram_commands())
            if self.paused:
                time.sleep(1)
                continue
            
            if self.should_restart_route:
                self.should_restart_route = False # Reset flag when at the start of route

            if wait_and_click(ASSETS["challenge"], timeout=10, confidence=DEFAULT_CONFIDENCE):
                challenge_fail_count = 0 # Reset count when found
                break
            
            challenge_fail_count += 1
            logging.warning(f"Challenge button not found. Retrying... (Attempt {challenge_fail_count})")
            
            if challenge_fail_count == 10:
                logging.info("Challenge button not found 10 times. Sending notification...")
                if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                    msg = "⚠️ Warning: Challenge button not found after 10 attempts. Please check the game status."
                    try:
                        screenshot_path = "challenge_not_found.png"
                        img = pyautogui.screenshot()
                        img.save(screenshot_path)
                        if os.path.exists(screenshot_path):
                            asyncio.run(send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, screenshot_path, caption=msg))
                            os.remove(screenshot_path)
                        else:
                            asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg))
                    except Exception as e:
                        logging.error(f"Failed to send 'challenge not found' notification: {e}")
            
            time.sleep(10)

        if not self.running or self.paused:
            return

        time.sleep(2) # Đợi game chuyển cảnh vào trong route

        while self.running:
            # 2. Wait for any target to appear (monster killed) - scan portal region
            target = None

            start_wait = time.time()
            while time.time() - start_wait < 30:  # Wait up to 30s for wave completion
                # 0. Kiểm tra lệnh từ Telegram
                asyncio.run(self.check_telegram_commands())
                if self.paused or not self.running or self.should_restart_route:
                    return

                name, pos = find_multiple_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE, region=PORTAL_REGION)
                if name:
                    # Nếu tìm thấy win hoặc failed ngay tại đây, nghĩa là route đã kết thúc
                    # Bo x3_click ra khoi day de chi trigger khi thay win
                    if name in ["win", "failed"]:
                        # Tránh bắt nhầm asset cũ ngay khi vừa start route (Wave 0)
                        if self.portal_count == 0 and (time.time() - start_wait < 5):
                            logging.info(f"Ignored potential stale end-of-route asset: {name}")
                            time.sleep(1)
                            continue
                            
                        logging.info(f"Detected end-of-route asset during target wait: {name}")
                        if not self.wait_for_end_of_route(is_ruong_nguyen=self.targeted_ruong_nguyen):
                            return
                        break # Trở lại vòng lặp chính

                    # double check 2nd time to avoid missing
                    name, pos = find_multiple_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE, region=PORTAL_REGION)
                    if not name or name in ["win", "failed"]:
                        continue # Re-scan
                    target = (name, pos)
                    break

                if not self.running:
                    break
                time.sleep(1)

            if not target:
                logging.warning("No target found after waiting for wave completion. Returning to challenge...")
                return

            self.portal_count += 1
            name, pos = target
            all_found = find_all_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE, region=PORTAL_REGION)
            
            # Group assets by their "portal type" to count actual distinct portals
            # Logic: remove the suffix _1, _2, _3 to get the base type
            unique_portals = set()
            for asset_name in all_found:
                if asset_name in ["win", "failed"]:
                    continue
                # Loai bo phan _1, _2, _3 o cuoi neu co
                base_name = asset_name
                if "_" in asset_name:
                    parts = asset_name.split("_")
                    if parts[-1].isdigit():
                        base_name = "_".join(parts[:-1])
                unique_portals.add(base_name)

            # Phải tìm thấy đủ 2 cổng khác nhau thì mới xử lý
            if len(unique_portals) < 2:
                if len(unique_portals) > 1:
                    logging.info(f"Wave {self.portal_count} - Found only {len(unique_portals)} portal types: {', '.join(unique_portals)} (From: {', '.join(all_found)}). Waiting for both portals...")
                self.portal_count -= 1
                time.sleep(1)
                continue
            
            # Uu tien ruongNguyen o bat ky wave nao
            if name.startswith("lvl3_ruongNguyen"):
                logging.info(f"Wave {self.portal_count} - Targeting RUONG NGUYEN: {name} (Found: {', '.join(all_found)}) - JACKPOT!!")
                self.targeted_ruong_nguyen = True
                
                # Gui thong bao Telegram (Async)
                if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                    msg = f"Treasure found at run {self.route_count}"
                    try:
                        # Capture man hinh
                        screenshot_path = "treasure_screenshot.png"
                        img = pyautogui.screenshot()
                        img.save(screenshot_path)
                        
                        if os.path.exists(screenshot_path):
                            # Chờ một chút để đảm bảo file đã được ghi hoàn toàn (đề phòng)
                            time.sleep(0.5)
                            # Vi application dang chay dong bo, ta dung cach nay de ko block thread chinh
                            asyncio.run(send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, screenshot_path, caption=msg))
                        else:
                            logging.error(f"Failed to create screenshot at {screenshot_path}")
                            asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg + " (Screenshot failed)"))
                        
                        # Xoa file sau khi gui
                        if os.path.exists(screenshot_path):
                            os.remove(screenshot_path)
                    except Exception as e:
                        logging.error(f"Failed to send Telegram notification: {e}")
                        # Backup: gui tin nhan text neu anh loi
                        asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg + f" (Error: {e})"))

                click_at(pos[0], pos[1])
                # Sau khi click Ruong Nguyen, chờ xem có portal tiếp hay kết thúc luôn
                if not self.wait_for_end_of_route(is_ruong_nguyen=True):
                    return # Kết thúc route
                continue # Nếu có portal mới thì loop tiếp
            
            if self.portal_count == 1:
                logging.info(f"Wave 1 - Clicking: {name} (Found: {', '.join(all_found)})")
                click_at(pos[0], pos[1])
                if not self.wait_for_end_of_route(is_ruong_nguyen=False):
                    return
                continue

            # Logic Wave 2+ (khong phai ruongNguyen)
            if self.portal_count >= 2:
                if self.targeted_ruong_nguyen:
                    logging.info(f"Wave {self.portal_count} - Ruong Nguyen already targeted, proceeding with: {name} (Found: {', '.join(all_found)})")
                    click_at(pos[0], pos[1])
                    if not self.wait_for_end_of_route(is_ruong_nguyen=True): # Giữ is_ruong_nguyen=True để đếm
                        return
                    continue

                if self.portal_count == 2:
                    logging.info(f"Wave 2 - Backing... (Found: {', '.join(all_found)}, No Ruong Nguyen)")
                    if wait_and_click(ASSETS["back"], timeout=5):
                        if wait_and_click(ASSETS["confirm"], timeout=5):
                            wait_and_click(ASSETS["failed"], timeout=10)
                    return

            # Fail-safe cho truong hop khong phai Ruong Nguyen ma portal_count > 2
            if self.portal_count >= 2 and not self.targeted_ruong_nguyen:
                return

    def run(self):
        # Start listening for ESC key in a separate thread
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        try:
            while self.running:
                # 0. Kiểm tra lệnh từ Telegram
                asyncio.run(self.check_telegram_commands())
                
                if self.paused:
                    logging.info("Application is paused. Waiting for 'again' command...")
                    while self.paused and self.running:
                        asyncio.run(self.check_telegram_commands())
                        time.sleep(2)
                    if not self.running:
                        break
                
                self.route_count += 1
                logging.info(f"--- Starting route #{self.route_count} ({self.ruong_nguyen_count} found) ---")
                self.process_action()

                # Wait briefly before next route check
                for _ in range(2):
                    if not self.running or self.paused:
                        break
                    time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Application stopped by Ctrl+C.")
        finally:
            self.running = False
            if self.listener:
                self.listener.stop()
            logging.info(f"Summary: Total routes run: {self.route_count}, Ruong Nguyen successfully finished {self.ruong_nguyen_count} times.")
            logging.info("AutoScripts application finished.")


if __name__ == "__main__":
    app = AutoScriptApp()
    app.run()
