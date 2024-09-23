import pyautogui
import time

print("Move your mouse to the desired location, and press Ctrl+C to stop.")

try:
    while True:
        # Get current mouse position
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})", end="\r")  # \r to overwrite in the same line
        time.sleep(0.1)  # Sleep for a short duration to reduce CPU usage
except KeyboardInterrupt:
    print("\nProgram stopped by user.")
