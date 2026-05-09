import time
import json
import win32gui
import win32api
import win32con
import ctypes
import checker
import win32gui
import win32api
import win32con
import ctypes

# Force DPI awareness so window dimensions match physical screen pixels
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

CONFIG_FILE = "config.json"

# --- CONFIGURATION FOR CLICK COORDINATES ---
# "暂停时长" (Pause) button location (Relative to Top-Right corner)
PAUSE_BTN_OFFSET_X = -260  # Pixels from the right edge (Changed from -280 to move RIGHT)
PAUSE_BTN_OFFSET_Y = 25    # Pixels from the top edge

# "取消" (Cancel) button location (Relative to the Center of the window)
CANCEL_BTN_OFFSET_X = 210  # Pixels to the right of the exact center
CANCEL_BTN_OFFSET_Y = -190 # Pixels below the exact center

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config in pauser: {e}")
        return {}

def background_click(hwnd, x, y):
    """Sends a mouse click to a window in the background."""
    lparam = win32api.MAKELONG(int(x), int(y))
    # CEF buttons often require a hover event before they accept clicks
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

def get_leigod_hwnd():
    hwnds = []
    def enum_cb(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "雷神" in title:
            results.append(hwnd)
    win32gui.EnumWindows(enum_cb, hwnds)
    return hwnds[0] if hwnds else None

def check_and_pause_leigod():
    config = load_config()
    monitored_games = config.get("monitored_games", [])

    print(f"Checking if Leigod tunnel is active...")
    if not checker.is_leigod_running():
        print("Leigod is ALREADY PAUSED. Skipping.")
        return

    print("Leigod is RUNNING. Checking for active games...")
    for game in monitored_games:
        if checker.is_process_running(game):
            print(f"Game detected: {game}. Will NOT pause.")
            return
            
    print("No active games detected! Proceeding to pause Leigod via background click...")
    
    hwnd = get_leigod_hwnd()
    if not hwnd:
        print("Could not find the Leigod window!")
        return
        
    # Get the un-minimized (normal) dimensions of the window using GetWindowPlacement
    # placement[4] is the (left, top, right, bottom) of the restored window
    placement = win32gui.GetWindowPlacement(hwnd)
    normal_rect = placement[4] 
    width = normal_rect[2] - normal_rect[0]
    height = normal_rect[3] - normal_rect[1]
    
    print(f"Window logic dimensions: {width}x{height} (Minimized: {win32gui.IsIconic(hwnd)})")

    # 1. Click the Pause button
    pause_x = width + PAUSE_BTN_OFFSET_X
    pause_y = PAUSE_BTN_OFFSET_Y
    print(f"Sending background click to Pause button at ({pause_x}, {pause_y})...")
    background_click(hwnd, pause_x, pause_y)

    time.sleep(2.5)

    # 2. Click the Cancel button
    cancel_x = (width // 2) + CANCEL_BTN_OFFSET_X
    cancel_y = (height // 2) + CANCEL_BTN_OFFSET_Y
    print(f"Sending background click to Cancel button at ({cancel_x}, {cancel_y})...")
    background_click(hwnd, cancel_x, cancel_y)
    
    print("Pause sequence complete.")

if __name__ == "__main__":
    check_and_pause_leigod()
