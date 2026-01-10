import pyautogui
import os
import time
import logging
from PIL import Image

# Global default confidence for image searching
DEFAULT_CONFIDENCE = 0.7

_logged_scale_info = False

def get_screen_scale(region=None):
    """
    Tính toán tỷ lệ giữa pixel thực tế (physical) và tọa độ logical.
    Hỗ trợ macOS Retina và Windows DPI Scaling.
    """
    global _logged_scale_info
    screen_width, screen_height = pyautogui.size()
    s = pyautogui.screenshot(region=region)
    # Scale = (Số pixel thực tế) / (Kích thước logical)
    scale = s.width / (region[2] if region else screen_width)
    
    # Thêm log theo yêu cầu, chỉ log lần đầu tiên
    if not _logged_scale_info:
        logging.info(f"Screen size (Logical): {screen_width}x{screen_height}")
        logging.info(f"Screenshot size (Physical): {s.width}x{s.height}")
        logging.info(f"Scale value: {scale}")
        _logged_scale_info = True
    
    return s, scale

def find_image(image_path, timeout=5, confidence=DEFAULT_CONFIDENCE, region=None):
    """
    Checks if image appears on screen.
    Tự động xử lý tỷ lệ màn hình (Retina/DPI Scaling).
    
    Returns:
        tuple: (x, y) logical coordinates if found, None if not found.
    """
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
                    logic_x = int((location.left + location.width / 2) / scale)
                    logic_y = int((location.top + location.height / 2) / scale)
                    # Khong can cong them region[0] vi pyautogui.locateOnScreen tra ve toa do man hinh thuc
                    result = (logic_x, logic_y)
                    break
            except Exception:
                pass
            time.sleep(0.5)
    finally:
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
            
    return result

def find_multiple_assets(assets_dict, priority_list, confidence=DEFAULT_CONFIDENCE, region=None):
    """
    Quét danh sách assets trên cùng một ảnh chụp màn hình để đảm bảo ưu tiên đúng.
    Hỗ trợ Retina/Windows DPI Scaling.
    """
    s, scale = get_screen_scale(region)
    
    for key in priority_list:
        image_path = assets_dict.get(key)
        if not image_path or not os.path.exists(image_path):
            continue
            
        temp_retina = f"temp_batch_{key}_{int(time.time()*1000)}.png"
        try:
            with Image.open(image_path) as img:
                scaled_size = (int(img.width * scale), int(img.height * scale))
                img.resize(scaled_size, Image.LANCZOS).save(temp_retina)
            
            # Sử dụng ảnh vừa chụp để tìm
            location = pyautogui.locate(temp_retina, s, confidence=confidence)
            if location:
                # Chuyen toa do tu screenshot ve toa do man hinh logical
                offset_x = region[0] if region else 0
                offset_y = region[1] if region else 0
                logic_x = int((location.left + location.width / 2) / scale + offset_x)
                logic_y = int((location.top + location.height / 2) / scale + offset_y)
                return key, (logic_x, logic_y)
        except Exception as e:
            logging.debug(f"Error finding {key}: {e}")
        finally:
            if os.path.exists(temp_retina):
                os.remove(temp_retina)
    return None, None

def find_all_assets(assets_dict, priority_list, confidence=DEFAULT_CONFIDENCE, region=None):
    """
    Tìm tất cả các assets trong priority_list đang xuất hiện trên màn hình.
    Trả về danh sách tuple (tên_asset, location) với location là (left, top, width, height) trong hệ tọa độ màn hình logical.
    Hỗ trợ Retina/Windows DPI Scaling.
    """
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
                # location ở đây là tương đối so với screenshot 's'
                # Cần chuyển về tọa độ màn hình logical (chia cho scale)
                offset_x = region[0] if region else 0
                offset_y = region[1] if region else 0
                real_left = int(location.left / scale + offset_x)
                real_top = int(location.top / scale + offset_y)
                real_width = int(location.width / scale)
                real_height = int(location.height / scale)
                real_location = (real_left, real_top, real_width, real_height)
                found_assets.append((key, real_location))
        except Exception as e:
            logging.debug(f"Error finding {key}: {e}")
        finally:
            if os.path.exists(temp_retina):
                os.remove(temp_retina)
    return found_assets

def click_at(x, y, double=True):
    if double:
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.click(x, y)

def wait_and_click(image_path, timeout=10, confidence=DEFAULT_CONFIDENCE, double=True, region=None):
    """
    Waits for image to appear on screen and performs a click.
    Hỗ trợ Retina/Windows DPI Scaling.
    
    Args:
        image_path (str): Path to the template image.
        timeout (int): Maximum wait time (seconds). Default is 10s.
        confidence (float): Search accuracy. Default is 0.7.
        region (tuple): (left, top, width, height) to search in.
    
    Returns:
        bool: True if found and clicked, False if timed out.
    """
    if not os.path.exists(image_path):
        logging.error(f"File {image_path} not found")
        return False

    start_time = time.time()
    
    # Get screen info for Retina/Windows DPI Scaling
    s, scale = get_screen_scale(region)
    
    # Prepare image
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
                    # Convert coordinates to logic for clicking
                    logic_x = int((location.left + location.width / 2) / scale)
                    logic_y = int((location.top + location.height / 2) / scale)
                    click_at(logic_x, logic_y, double=double)
                    return True
            except Exception:
                pass
            time.sleep(0.5)
    finally:
        if os.path.exists(temp_retina):
            os.remove(temp_retina)
            
    return False
