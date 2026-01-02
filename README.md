# Auto Scripts Project

This project provides a basic code base for writing automation scripts based on image recognition on the screen.

## Project Structure

- `src/core/detector.py`: Handles searching for images on the screen using `pyautogui` and `OpenCV`.
- `src/core/controller.py`: Handles mouse control operations (click, move).
- `src/assets/`: Storage for template images to be recognized.
- `main.py`: Example file demonstrating how to use the code base.

## Installation

1. Ensure you have Python 3 installed.
2. Install the necessary libraries:
   ```bash
   pip install pyautogui opencv-python numpy pillow
   ```

## Usage

1. Take a screenshot of the screen area you want the script to find and click on.
2. Save that image into the `src/assets/` directory (e.g., `button.png`).
3. Edit `main.py` to point to your image file.
4. Run the script:
   ```bash
   python main.py
   ```

## Important Notes (macOS)

- On macOS, you need to grant permissions to Terminal/IDE in **System Settings > Privacy & Security > Accessibility** and **Screen Recording** so the script can control the mouse and take screenshots.
- **Fail-Safe** feature: If the script behaves unexpectedly, quickly move the mouse to any of the 4 corners of the screen to stop the script immediately.
