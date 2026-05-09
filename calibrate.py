import pauser
import pyautogui
import time
import win32gui
import ctypes

# Force DPI awareness to match pauser.py
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

def calibrate():
    print("Finding Leigod window...")
    hwnd = pauser.get_leigod_hwnd()
    
    if not hwnd:
        print("Leigod window not found. Make sure it's open!")
        return

    # Briefly restore it if minimized so user can visually verify
    if win32gui.IsIconic(hwnd) or not win32gui.IsWindowVisible(hwnd):
        win32gui.ShowWindow(hwnd, 4)
        time.sleep(0.5)

    # Use exact same math as pauser.py
    placement = win32gui.GetWindowPlacement(hwnd)
    normal_rect = placement[4] 
    width = normal_rect[2] - normal_rect[0]
    height = normal_rect[3] - normal_rect[1]

    # Calculate relative coordinates
    rel_x = (width // 2) + pauser.CANCEL_BTN_OFFSET_X
    rel_y = (height // 2) + pauser.CANCEL_BTN_OFFSET_Y

    # Calculate absolute coordinates for physical mouse
    cancel_x = normal_rect[0] + rel_x
    cancel_y = normal_rect[1] + rel_y

    print(f"Window physical dimensions: {width}x{height}")
    print(f"Target absolute coordinates: ({cancel_x}, {cancel_y})")
    
    print("Moving physical mouse to visual location...")
    pyautogui.moveTo(cancel_x, cancel_y, duration=0.5)
    
    print(f"Testing PURE background click at relative ({rel_x}, {rel_y})...")
    pauser.background_click(hwnd, rel_x, rel_y)
    
    print("\nDid the click register on the Cancel button?")

if __name__ == "__main__":
    calibrate()
