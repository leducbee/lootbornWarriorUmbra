import asyncio
import json
import logging
import os
import sys
import time
from enum import Enum

from pynput import keyboard
from telegram import Bot

from capture_util import capture_region
from search_util import click_at, find_multiple_assets, find_all_assets
from telegram_notifier import send_telegram_message, send_telegram_photo

# Telegram Config
CONFIG_FILE = "config.json"

def load_telegram_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                token = config.get("telegram_token", "")
                chat_id = str(config.get("telegram_chat_id", ""))
                
                # Check for placeholders
                if token in ["", "xx", "your_token_here"] or chat_id in ["", "yy", "your_chat_id_here"]:
                    return "", ""
                return token, chat_id
        except Exception as e:
            logging.error(f"Error loading {CONFIG_FILE} for Telegram: {e}")
    return "", ""

TELEGRAM_TOKEN, TELEGRAM_CHAT_ID = load_telegram_config()

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

ASSETS = {} # Will be populated based on assets_dir from config

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
    def __init__(self, base_path=None):
        if base_path is None:
            if getattr(sys, 'frozen', False):
                self.base_path = os.path.dirname(sys.executable)
            else:
                self.base_path = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_path = base_path

        self.config_file = os.path.join(self.base_path, "config.json")
        self.coords_file = os.path.join(self.base_path, "initial_coordinates.txt")

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
        token, chat_id = self.load_telegram_config_from_file()
        if token and chat_id:
            try:
                logging.info("Initializing Telegram bot and clearing old updates...")
                bot = Bot(token=token)
                loop = asyncio.new_event_loop()
                updates = loop.run_until_complete(self._get_latest_update_id(bot))
                loop.close()
                if updates:
                    self.last_update_id = updates[-1].update_id
                    logging.info(f"Telegram initialized. Ignoring updates before ID: {self.last_update_id}")
            except Exception as e:
                logging.error(f"Failed to initialize Telegram updates: {e}")
        else:
            logging.info("Telegram configuration missing or placeholder detected. Telegram notifications disabled.")

    def load_telegram_config_from_file(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    token = config.get("telegram_token", "")
                    chat_id = str(config.get("telegram_chat_id", ""))
                    
                    # Check for placeholders
                    if token in ["", "xx", "your_token_here"] or chat_id in ["", "yy", "your_chat_id_here"]:
                        return "", ""
                    return token, chat_id
            except Exception as e:
                logging.error(f"Error loading {self.config_file} for Telegram: {e}")
        return "", ""

    def load_config(self):
        """
        Load configuration from config.json
        """
        if not os.path.exists(self.config_file):
            logging.warning(f"File {self.config_file} not found. Using default values")
            self._update_assets_paths(os.path.join(self.base_path, "src/assets/working/"))
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                self.max_run = config_data.get("max_run", 0)
                assets_dir_relative = config_data.get("assets_dir", "src/assets/working/")
                
                # Nếu assets_dir là tương đối, nối nó với base_path
                if not os.path.isabs(assets_dir_relative):
                    assets_dir = os.path.join(self.base_path, assets_dir_relative)
                else:
                    assets_dir = assets_dir_relative
                
                self._update_assets_paths(assets_dir)
            logging.info(f"Loaded config: MAX_RUN = {self.max_run}, ASSETS_DIR = {assets_dir}")
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self._update_assets_paths(os.path.join(self.base_path, "src/assets/working/"))

    def _update_assets_paths(self, assets_dir):
        """
        Update the global ASSETS dictionary with the given directory
        """
        global ASSETS
        ASSETS.clear()
        for key, filename in ASSETS_MAPPING.items():
            ASSETS[key] = os.path.join(assets_dir, filename)

    def save_config(self):
        """
        Save configuration to config.json
        """
        try:
            config_data = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            
            config_data["max_run"] = self.max_run
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            logging.info(f"Saved config: MAX_RUN = {self.max_run}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def load_initial_coordinates(self):
        """
        Load initial coordinates from initial_coordinates.txt
        Format: name: (x, y, w, h)
        """
        if not os.path.exists(self.coords_file):
            logging.error(f"File {self.coords_file} not found.")
            return

        try:
            with open(self.coords_file, "r", encoding="utf-8") as f:
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
            logging.info(f"Loaded regions from {self.coords_file}: {list(self.regions.keys())}")
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
                    logging.info("MAX_RUN reached 0. Application will stop after this run.")
                
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

        if self.max_run <= 0:
            logging.info("Stopping application as planned after finishing the run.")
            self.running = False
            return

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
