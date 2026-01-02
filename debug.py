from search_util import wait_and_click

if __name__ == "__main__":
    target = "src/assets/pyautogui_screenshot.png"
    if not wait_and_click("src/assets/img.png"):
        print("Not found")
