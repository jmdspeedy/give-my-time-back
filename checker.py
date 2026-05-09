import win32gui
import win32con
import win32ui
import time
import ctypes
from PIL import Image

# Force DPI awareness
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

import psutil

def is_process_running(process_name):
    if not process_name: return False
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def get_leigod_hwnd():
    hwnds = []
    def enum_cb(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "雷神" in title:
            results.append(hwnd)
    win32gui.EnumWindows(enum_cb, hwnds)
    return hwnds[0] if hwnds else None

def is_leigod_running():
    """
    Checks if Leigod is boosting by briefly un-minimizing it in the background,
    capturing its color buffer, and re-minimizing it.
    """
    hwnd = get_leigod_hwnd()
    if not hwnd:
        return False
        
    was_minimized = win32gui.IsIconic(hwnd)
    
    if was_minimized:
        # Restore it without taking focus (it stays behind your current window)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        time.sleep(0.2) # Give Windows DWM a split second to render the buffer
        
    # Get window dimensions
    placement = win32gui.GetWindowPlacement(hwnd)
    rect = placement[4] 
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    
    # Capture the window's pixels directly (even if it's hidden behind other windows)
    hdc = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hdc)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # PW_RENDERFULLCONTENT = 2. Works on Windows 8.1+ for hardware accelerated apps
    ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    
    # Cleanup GDI objects
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hdc)
    
    if was_minimized:
        # Re-minimize it immediately
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        
    # Now check the color of the Pause button area
    # Pause button is top-right. Let's sample a pixel.
    import pauser
    # Coordinate of the button
    btn_x = width + pauser.PAUSE_BTN_OFFSET_X
    btn_y = pauser.PAUSE_BTN_OFFSET_Y
    
    # Safely get pixel color
    try:
        r, g, b = img.getpixel((btn_x, btn_y))
        
        # When boosting, the button is RED. (R > 150, G < 100, B < 100)
        # When paused, the button is WHITE. (R > 200, G > 200, B > 200)
        is_red = r > 150 and g < 100 and b < 100
        
        return is_red
    except IndexError:
        print("Pixel check out of bounds!")
        return False

def check_status():
    if is_leigod_running():
        print("STATUS: Leigod is ON (Boosting - Red Button Detected)")
    else:
        print("STATUS: Leigod is OFF (Paused - White Button Detected)")

if __name__ == "__main__":
    check_status()
