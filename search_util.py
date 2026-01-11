import pyautogui
import os
import time
import logging
from PIL import Image
DEFAULT_CONFIDENCE = 0.7
_logged_scale_info = False
_hud = None
def set_hud(hud_obj):
    global _hud
    _hud = hud_obj
def get_screen_scale(region=None):
    global _logged_scale_info
    screen_width, screen_height = pyautogui.size()
    s = pyautogui.screenshot() 
    scale = s.width / screen_width
    if region:
        left, top, width, height = region
        left_p, top_p = int(left * scale), int(top * scale)
        width_p, height_p = int(width * scale), int(height * scale)
        s = s.crop((left_p, top_p, left_p + width_p, top_p + height_p))
    if not _logged_scale_info:
        logging.info(f"Screen size (Logical): {screen_width}x{screen_height}")
        logging.info(f"Full Screenshot size (Physical): {s.width if not region else int(screen_width*scale)}x{s.height if not region else int(screen_height*scale)}")
        logging.info(f"Scale value: {scale}")
        _logged_scale_info = True
    return s, scale
def find_image(image_path, timeout=5, confidence=DEFAULT_CONFIDENCE, region=None):
    if not os.path.exists(image_path):
        logging.error(f"File {image_path} not found")
        return None
    s, scale = get_screen_scale(region)
    temp_retina = f"temp_find_{int(time.time()*1000)}.png"
    try:
        with Image.open(image_path) as img:
            scaled_size = (int(img.width * scale), int(img.height * scale))
            img.resize(scaled_size, Image.LANCZOS).save(temp_retina)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
        return None
    start_time = time.time()
    result = None
    try:
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(temp_retina, confidence=confidence, region=region)
                if location:
                    logic_x = int(location.left + location.width / 2)
                    logic_y = int(location.top + location.height / 2)
                    logic_x = int(logic_x / scale)
                    logic_y = int(logic_y / scale)
                    result = (logic_x, logic_y)
                    break
            except Exception:
                pass
            time.sleep(0.5)
    finally:
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
    return result
def find_multiple_assets(assets_dict, priority_list, confidence=DEFAULT_CONFIDENCE, region=None, signature=True):
    s, scale = get_screen_scale(region)
    first_found_key = None
    first_found_pos = None
    all_found_regions = []
    for key in priority_list:
        image_path = assets_dict.get(key)
        if not image_path or not os.path.exists(image_path):
            continue
        temp_retina = f"temp_batch_{key}_{int(time.time()*1000)}.png"
        try:
            with Image.open(image_path) as img:
                scaled_size = (int(img.width * scale), int(img.height * scale))
                img.resize(scaled_size, Image.LANCZOS).save(temp_retina)
            location = pyautogui.locate(temp_retina, s, confidence=confidence)
            if location:
                offset_x = region[0] if region else 0
                offset_y = region[1] if region else 0
                logic_x = int((location.left + location.width / 2) / scale + offset_x)
                logic_y = int((location.top + location.height / 2) / scale + offset_y)
                logic_left = location.left / scale
                logic_top = location.top / scale
                logic_width = location.width / scale
                logic_height = location.height / scale
                real_left = int(logic_left + offset_x)
                real_top = int(logic_top + offset_y)
                real_width = int(logic_width)
                real_height = int(logic_height)
                logging.debug(f"Found {key} at physical ({location.left}, {location.top}), logical ({real_left}, {real_top}) with scale {scale}")
                all_found_regions.append((key, (real_left, real_top, real_width, real_height)))
                if first_found_key is None:
                    first_found_key = key
                    first_found_pos = (logic_x, logic_y)
                    if not signature:
                        break
        except Exception as e:
            logging.debug(f"Error finding {key}: {e}")
        finally:
            if os.path.exists(temp_retina):
                os.remove(temp_retina)
    if signature and _hud:
        _hud.update_regions(all_found_regions, padding=5)
    return first_found_key, first_found_pos, all_found_regions
def find_all_assets(assets_dict, priority_list, confidence=DEFAULT_CONFIDENCE, region=None, signature=True):
    s, scale = get_screen_scale(region)
    found_assets = []
    for key in priority_list:
        image_path = assets_dict.get(key)
        if not image_path or not os.path.exists(image_path):
            continue
        temp_retina = f"temp_all_{key}_{int(time.time()*1000)}.png"
        try:
            with Image.open(image_path) as img:
                scaled_size = (int(img.width * scale), int(img.height * scale))
                img.resize(scaled_size, Image.LANCZOS).save(temp_retina)
            location = pyautogui.locate(temp_retina, s, confidence=confidence)
            if location:
                offset_x = region[0] if region else 0
                offset_y = region[1] if region else 0
                logic_left = location.left / scale
                logic_top = location.top / scale
                logic_width = location.width / scale
                logic_height = location.height / scale
                real_left = int(logic_left + offset_x)
                real_top = int(logic_top + offset_y)
                real_width = int(logic_width)
                real_height = int(logic_height)
                logging.debug(f"Found {key} at physical ({location.left}, {location.top}), logical ({real_left}, {real_top}) with scale {scale}")
                real_location = (real_left, real_top, real_width, real_height)
                found_assets.append((key, real_location))
        except Exception as e:
            logging.debug(f"Error finding {key}: {e}")
        finally:
            if os.path.exists(temp_retina):
                os.remove(temp_retina)
    if signature and _hud:
        _hud.update_regions(found_assets, padding=5)
    return found_assets
def click_at(x, y, double=True):
    if double:
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.click(x, y)
def wait_and_click(image_path, timeout=10, confidence=DEFAULT_CONFIDENCE, double=True, region=None):
    if not os.path.exists(image_path):
        logging.error(f"File {image_path} not found")
        return False
    start_time = time.time()
    s, scale = get_screen_scale(region)
    temp_retina = f"temp_retina_{int(time.time())}.png"
    try:
        with Image.open(image_path) as img:
            scaled_size = (int(img.width * scale), int(img.height * scale))
            img.resize(scaled_size, Image.LANCZOS).save(temp_retina)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
        return False
    try:
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(temp_retina, confidence=confidence, region=region)
                if location:
                    logic_x = int(location.left + location.width / 2)
                    logic_y = int(location.top + location.height / 2)
                    logic_x = int(logic_x / scale)
                    logic_y = int(logic_y / scale)
                    click_at(logic_x, logic_y, double=double)
                    return True
            except Exception:
                pass
            time.sleep(0.5)
    finally:
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
    return False
