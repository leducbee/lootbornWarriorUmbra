import asyncio
import logging
import os
import sys
import time

from enum import Enum, auto
from pynput import keyboard
from telegram import Bot

from search_util import wait_and_click, click_at, find_multiple_assets, find_all_assets
from telegram_notifier import send_telegram_message, send_telegram_photo
from capture_util import capture_region

# Telegram Config
TELEGRAM_TOKEN = "xx"
TELEGRAM_CHAT_ID = "yy"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

ASSETS = {
    "challenge": "src/assets/working/challenge.png",
    "back_fighting": "src/assets/working/back.png",
    "back_challenge": "src/assets/working/back.png",
    "back_umbra": "src/assets/working/back.png",
    "confirm": "src/assets/working/confirm.png",
    "failed": "src/assets/working/failed.png",
    "win": "src/assets/working/win.png",
    "x3_click": "src/assets/working/x3_click.png",
    "to_umbra": "src/assets/working/to_umbra.png",
    "tach": "src/assets/working/tach.png",
    "tach_all": "src/assets/working/tach_all.png",
    "tach_confirm": "src/assets/working/tach_confirm.png",
    "lvl3_ruongNguyen_1": "src/assets/working/text_lvl3_ruongNguyen_1.png",
    "lvl3_ruongNguyen_2": "src/assets/working/text_lvl3_ruongNguyen_2.png",
    "lvl1_boLacQuaiVat_1": "src/assets/working/text_lvl1_boLacQuaiVat_1.png",
    "lvl1_boLacQuaiVat_2": "src/assets/working/text_lvl1_boLacQuaiVat_2.png",
    "lvl1_suoiSinhMenh": "src/assets/working/text_lvl1_suoiSinhMenh.png",
    "lvl1_suoiTinhThan_1": "src/assets/working/text_lvl1_suoiTinhThan_1.png",
    "lvl1_suoiTinhThan_2": "src/assets/working/text_lvl1_suoiTinhThan_2.png",
    "lvl1_teDanCoDai_1": "src/assets/working/text_lvl1_teDanCoDai_1.png",
    "lvl1_teDanCoDai_2": "src/assets/working/text_lvl1_teDanCoDai_2.png",
    "lvl2_hangOQuaiVat_1": "src/assets/working/text_lvl2_hangOQuaiVat_1.png",
    "lvl2_hangOQuaiVat_2": "src/assets/working/text_lvl2_hangOQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_1": "src/assets/working/text_lvl3_toChinhQuaiVat_1.png",
    "lvl3_toChinhQuaiVat_2": "src/assets/working/text_lvl3_toChinhQuaiVat_2.png",
    "lvl3_toChinhQuaiVat_3": "src/assets/working/text_lvl3_toChinhQuaiVat_3.png",
    "lvl3_toChinhQuaiVat_4": "src/assets/working/text_lvl3_toChinhQuaiVat_4.png",
    "lvl5_banDoChuaRo": "src/assets/working/text_lvl5_banDoChuaRo.png"
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


class FlowStatus(Enum):
    FIGHTING = "fighting"
    AWAIT_FIGHTING_DONE = "await_fighting_done"
    FIGHTING_DONE = "fighting_done"
    FIGHT = "fight"
    NONE = "none"
    REFINE = "refine"
    DONE = "done"
    UNKNOWN = "unknown"
    RESET = "reset"


class ScanResult:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos


FLOW_REGIONS = {
    FlowStatus.FIGHTING: ["to_umbra", "challenge", "left_portal_text", "right_portal_text", "win", "failed"],
    FlowStatus.AWAIT_FIGHTING_DONE: ["left_portal_text", "right_portal_text", "win", "failed"],
    FlowStatus.DONE: ["failed", "x3_click"],
    FlowStatus.RESET: ["back_fighting", "failed", "confirm"],
    FlowStatus.REFINE: ["tach", "tach_all", "tach_confirm", "back_umbra"]
}

DEFAULT_CONFIDENCE = 0.7


def determine_flow(scan_results):
    if "win" in scan_results or "failed" in scan_results:
        return FlowStatus.DONE
    if "challenge" in scan_results:
        return FlowStatus.FIGHTING
    if "left_portal_text" in scan_results or "right_portal_text" in scan_results:
        return FlowStatus.FIGHTING
    return FlowStatus.UNKNOWN


def click_scan_result(scan_results, key):
    res = scan_results.get(key)
    if res:
        click_at(res.pos[0], res.pos[1])
        return True
    return False


class AutoScriptApplication:
    def __init__(self):
        self.running = True
        self.paused = False
        self.listener = None
        self.last_update_id = -1
        self.route_count = 0
        self.ruong_nguyen_count = 0
        self.found_treasure = False
        self.portal_count = 0
        self.current_flow = FlowStatus.NONE
        self.regions = {}
        self.load_initial_coordinates()
        self.sleep_time = 3
        self.unscreen_count = 0
        self.max_run = 0
        self.load_config()

        # Init Telegram
        self.initialize_telegram()

    def initialize_telegram(self):
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                logging.info("Initializing Telegram bot and clearing old updates...")
                bot = Bot(token=TELEGRAM_TOKEN)
                loop = asyncio.new_event_loop()
                updates = loop.run_until_complete(self._get_latest_update_id(bot))
                loop.close()
                if updates:
                    self.last_update_id = updates[-1].update_id
                    logging.info(f"Telegram initialized. Ignoring updates before ID: {self.last_update_id}")
            except Exception as e:
                logging.error(f"Failed to initialize Telegram updates: {e}")

    def load_config(self):
        """
        Load configuration from auto_script_config.txt
        """
        file_path = "auto_script_config.txt"
        if not os.path.exists(file_path):
            logging.warning(f"File {file_path} not found. Using default MAX_RUN=0")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    if key.strip() == "MAX_RUN":
                        self.max_run = int(value.strip())
            logging.info(f"Loaded config: MAX_RUN = {self.max_run}")
        except Exception as e:
            logging.error(f"Error loading config: {e}")

    def save_config(self):
        """
        Save configuration to auto_script_config.txt
        """
        file_path = "auto_script_config.txt"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"MAX_RUN = {self.max_run}\n")
            logging.info(f"Saved config: MAX_RUN = {self.max_run}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def load_initial_coordinates(self):
        """
        Load initial coordinates from initial_coordinates.txt
        Format: name: (x, y, w, h)
        """
        file_path = "initial_coordinates.txt"
        if not os.path.exists(file_path):
            logging.error(f"File {file_path} not found.")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue

                    name, coords_str = line.split(":", 1)
                    name = name.strip()
                    # Remove brackets and split by comma
                    coords_str = coords_str.strip().strip("() ")
                    if coords_str:
                        coords = tuple(map(int, coords_str.split(",")))
                        self.regions[name] = coords
            logging.info(f"Loaded regions from {file_path}: {list(self.regions.keys())}")
        except Exception as e:
            logging.error(f"Error loading initial coordinates: {e}")

    async def _get_latest_update_id(self, bot):
        async with bot:
            return await bot.get_updates(offset=-1, timeout=1)

    async def check_telegram_commands(self):
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
                        if text == "exit":
                            self.running = False
                            self.paused = False
                            logging.info(f"Stopping application due to 'exit' command (ID: {update.update_id})")
                            await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🔌 Thoát")
                        elif text == "capture":
                            logging.info(f"Capturing screen due to command ID: {update.update_id}")
                            try:
                                import pyautogui
                                screenshot_path = f"manual_capture_{update.update_id}.png"
                                img = pyautogui.screenshot()
                                img.save(screenshot_path)
                                if os.path.exists(screenshot_path):
                                    await send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, screenshot_path,
                                                              caption=f"📸 Screenshot manual (ID: {update.update_id})")
                                    os.remove(screenshot_path)
                                else:
                                    await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
                                                                "❌ Lỗi: Không thể lưu ảnh chụp màn hình.")
                            except Exception as e:
                                logging.error(f"Error during manual capture: {e}")
                                await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"❌ Lỗi khi capture: {e}")
        except Exception as e:
            logging.error(f"Telegram command error: {e}")

    def on_press(self, key):
        if key == keyboard.Key.esc:
            logging.info("ESC pressed. Stopping...")
            self.running = False
            return False

    def scan_all_regions(self, flow=FlowStatus.NONE):
        results = {}
        target_regions = FLOW_REGIONS.get(flow)

        if target_regions is None:
            regions_to_scan = list(self.regions.keys())
        else:
            regions_to_scan = [r for r in target_regions if r in self.regions]

        for region_name in regions_to_scan:
            region_coords = self.regions[region_name]
            name, pos = find_multiple_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE, region=region_coords)
            if name:
                results[region_name] = ScanResult(name, pos)

        # if results:
        #     logging.info(f"Scan results: {list(results.keys())}")
        return results

    def handle_fighting(self, scan_results):
        self.sleep_time = 3

        if "win" in scan_results:
            x3_res = self.scan_all_regions(FlowStatus.DONE).get("x3_click")
            if x3_res:
                click_at(x3_res.pos[0], x3_res.pos[1])
                self.current_flow = FlowStatus.DONE
            return

        if "failed" in scan_results:
            if click_scan_result(scan_results, "failed"):
                self.current_flow = FlowStatus.DONE
            return

        if "to_umbra" in scan_results:
            if click_scan_result(scan_results, "to_umbra"):
                self.sleep_time = 2
                self.current_flow = FlowStatus.REFINE
            return

        if "challenge" in scan_results:
            click_scan_result(scan_results, "challenge")
            self.route_count += 1
            self.portal_count = 0  # Reset wave count when starting new route
            logging.info(f"Route #{self.route_count} started. ({self.ruong_nguyen_count} found)")
            return

        res_l = scan_results.get("left_portal_text")
        res_r = scan_results.get("right_portal_text")

        all_found = []
        if "left_portal_text" in self.regions:
            all_found_l = find_all_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE,
                                          region=self.regions["left_portal_text"])
            all_found.extend(all_found_l)
        if "right_portal_text" in self.regions:
            all_found_r = find_all_assets(ASSETS, PRIORITY_LIST, confidence=DEFAULT_CONFIDENCE,
                                          region=self.regions["right_portal_text"])
            all_found.extend(all_found_r)

        unique_portals = set()
        for asset_name, _ in all_found:
            base_name = asset_name
            if "_" in asset_name and asset_name.split("_")[-1].isdigit():
                base_name = "_".join(asset_name.split("_")[:-1])
            unique_portals.add(base_name)

        if len(unique_portals) < 2:
            return

        target = None
        if res_l and res_r:
            idx_l = PRIORITY_LIST.index(res_l.name) if res_l.name in PRIORITY_LIST else 999
            idx_r = PRIORITY_LIST.index(res_r.name) if res_r.name in PRIORITY_LIST else 999
            target = res_l if idx_l <= idx_r else res_r
        elif res_l:
            target = res_l
        elif res_r:
            target = res_r

        if target:
            name = target.name
            pos = target.pos
            self.portal_count += 1

            if name.startswith("lvl3_ruongNguyen"):
                logging.info(f"Wave {self.portal_count} - Targeting: {name}")
                self.ruong_nguyen_count += 1
                self.found_treasure = True
                self.current_flow = FlowStatus.AWAIT_FIGHTING_DONE

                msg = f"💎 Treasure found! (run {self.route_count})"
                import pyautogui
                sw, sh = pyautogui.size()
                photo_path = f"src/assets/working/treasure.png"
                capture_region(0, 0, sw, sh, save_path=photo_path)

                asyncio.run(send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, photo_path, caption=msg))

                # Xóa ảnh sau khi gửi để tránh đầy bộ nhớ
                if os.path.exists(photo_path):
                    os.remove(photo_path)

                logging.info(f"{msg})")
                self.max_run -= 1
                self.save_config()
                if self.max_run <= 0:
                    logging.info("MAX_RUN reached 0. Stopping application...")
                    self.running = False
                
                click_at(pos[0], pos[1])  # Click portal chứa rương
                time.sleep(2)
                return

            if self.portal_count >= 2 and not self.found_treasure:
                logging.info(f"Wave {self.portal_count} - Backing... (No Ruong Nguyen found)")
                self.current_flow = FlowStatus.RESET
                self.sleep_time = 1
                return

            logging.info(f"Wave {self.portal_count} - Targeting: {name}")
            click_at(pos[0], pos[1])

    def handle_reset(self, scan_results):
        if "failed" in scan_results:
            self.current_flow = FlowStatus.NONE
            click_scan_result(scan_results, "failed")
            return
        if "confirm" in scan_results:
            click_scan_result(scan_results, "confirm")
            return
        if "back_fighting" in scan_results:
            click_scan_result(scan_results, "back_fighting")
            return

    def handle_refine(self):
        tach = self.scan_all_regions(FlowStatus.REFINE).get("tach")
        if tach:
            click_at(tach.pos[0], tach.pos[1], False)
            time.sleep(1)
            scan_result = self.scan_all_regions(FlowStatus.REFINE)
            check = scan_result.get("tach_all")
            if check:
                click_at(check.pos[0], check.pos[1], False)
                time.sleep(1)
                confirm = scan_result.get("tach_confirm")
                if confirm:
                    click_at(confirm.pos[0], confirm.pos[1], False)
                    time.sleep(1)
                    back_umbra = scan_result.get("back_umbra")
                    if back_umbra:
                        click_at(back_umbra.pos[0], back_umbra.pos[1])
                        time.sleep(0.5)

            self.current_flow = FlowStatus.DONE

    def handle_done(self, scan_results):
        self.current_flow = FlowStatus.NONE
        self.found_treasure = False  # Reset flag
        self.portal_count = 0  # Reset wave count
        for key in ("x3_click", "failed"):
            if key in scan_results:
                click_scan_result(scan_results, key)
                self.sleep_time = 1
                return

    def run(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        logging.info("AutoScriptApplication started.")
        try:
            while self.running:
                asyncio.run(self.check_telegram_commands())
                if self.paused:
                    self.sleep_time = 3
                    continue

                time.sleep(self.sleep_time)

                if self.current_flow in [FlowStatus.NONE, FlowStatus.UNKNOWN]:
                    scan_results = self.scan_all_regions(FlowStatus.NONE)
                    self.current_flow = determine_flow(scan_results)

                # 2. Xử lý theo flow
                if self.current_flow == FlowStatus.FIGHTING:
                    self.unscreen_count = 0
                    scan_results = self.scan_all_regions(FlowStatus.FIGHTING)
                    self.handle_fighting(scan_results)
                elif self.current_flow == FlowStatus.AWAIT_FIGHTING_DONE:
                    self.unscreen_count = 0
                    scan_results = self.scan_all_regions(FlowStatus.AWAIT_FIGHTING_DONE)
                    self.handle_fighting(scan_results)
                elif self.current_flow == FlowStatus.RESET:
                    self.unscreen_count = 0
                    scan_results = self.scan_all_regions(FlowStatus.RESET)
                    self.handle_reset(scan_results)
                elif self.current_flow == FlowStatus.REFINE:
                    self.unscreen_count = 0
                    self.handle_refine()
                elif self.current_flow == FlowStatus.DONE:
                    self.unscreen_count = 0
                    scan_results = self.scan_all_regions(FlowStatus.DONE)
                    self.handle_done(scan_results)
                else:
                    self.unscreen_count += 1
                    logging.info(f"Flow {self.current_flow.value} - Waiting for recognizable screen... ({self.unscreen_count}/20)")
                    
                    if self.unscreen_count >= 12: # 2 minutes
                        logging.warning("Unrecognizable screen detected 20 times! Sending notification...")
                        msg = "⚠️ Cảnh báo: Không nhận diện được màn hình game (20 lần liên tiếp)."
                        import pyautogui
                        sw, sh = pyautogui.size()
                        photo_path = "unscreen_alert.png"
                        capture_region(0, 0, sw, sh, save_path=photo_path)
                        asyncio.run(send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, photo_path, caption=msg))
                        if os.path.exists(photo_path):
                            os.remove(photo_path)
                        self.unscreen_count = 0 # Reset sau khi báo

                    self.current_flow = FlowStatus.NONE
                    self.sleep_time = 10


        except KeyboardInterrupt:
            logging.info("Stopped by user.")
        finally:
            self.running = False
            if self.listener:
                self.listener.stop()
            logging.info("Finished.")


if __name__ == "__main__":
    app = AutoScriptApplication()
    app.run()
