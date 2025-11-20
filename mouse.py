import pyautogui
import time

def track_mouse(interval=0.5):
    print("Tracking mouse position... Press CTRL+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Mouse is at: ({x}, {y})")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Tracking stopped.")

# Run:
track_mouse()

# Home: (1094, 356)
# A1 (1095, 402)
# J10 (1633, 940)
