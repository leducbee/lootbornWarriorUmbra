import pyautogui
import os
import time
from PIL import Image

def capture_region(x, y, width, height, save_path="src/assets/pyautogui_screenshot.png", resize_to_logic=False):
    """
    Captures a screen region and saves it to the specified path.
    
    Args:
        x (int): Top-left X coordinate.
        y (int): Top-left Y coordinate.
        width (int): Region width.
        height (int): Region height.
        save_path (str): Path to save the image file.
        resize_to_logic (bool): If True, resizes to logical dimensions (Mac Retina standard).
                               If False, keeps physical dimensions (Retina).
    """
    # Ensure directory exists
    directory = os.path.dirname(save_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Use pyautogui to capture the specified region
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # Retina handling: If captured size differs from requested logical size
    if screenshot.width != width or screenshot.height != height:
        if resize_to_logic:
            screenshot = screenshot.resize((width, height), Image.LANCZOS)

    # Save image
    screenshot.save(save_path)
    return save_path

def capture_between_two_points(save_path="src/assets/pyautogui_screenshot.png", delay1=3, delay2=3):
    """
    Waits for delay1 seconds to get mouse position 1, then waits for delay2 seconds 
    to get mouse position 2 to determine the capture region.
    """
    print("Starting to capture position 1...")
    for i in range(delay1, 0, -1):
        time.sleep(1)
    
    x1, y1 = pyautogui.position()
    print(f"Position 1: x={x1}, y={y1}")
    
    print("Starting to capture position 2...")
    for i in range(delay2, 0, -1):
        time.sleep(1)
    
    x2, y2 = pyautogui.position()
    print(f"Position 2: x={x2}, y={y2}")
    
    # Calculate top-left coordinates (x, y) and dimensions (width, height)
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    
    if width == 0 or height == 0:
        return None

    return capture_region(left, top, width, height, save_path)

if __name__ == "__main__":
    # Example: Capture region defined by 2 mouse positions
    try:
        path = capture_between_two_points()
        if path:
            print(f"Please check the file at: {os.path.abspath(path)}")
    except Exception as e:
        print(f"❌ An error occurred while capturing: {e}")
