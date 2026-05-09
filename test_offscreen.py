import win32gui
import win32con
import time
from PIL import ImageGrab

def get_leigod_hwnd():
    hwnds = []
    def enum_cb(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "雷神" in title:
            results.append(hwnd)
    win32gui.EnumWindows(enum_cb, hwnds)
    return hwnds[0] if hwnds else None

hwnd = get_leigod_hwnd()
if hwnd:
    print(f"Testing off-screen rendering on HWND: {hwnd}")
    
    # 1. Save current placement
    placement = win32gui.GetWindowPlacement(hwnd)
    original_rect = placement[4]
    
    print(f"Original Rect: {original_rect}")
    
    # 2. Move window off-screen (-10000, -10000) but keep width/height
    width = original_rect[2] - original_rect[0]
    height = original_rect[3] - original_rect[1]
    win32gui.SetWindowPos(hwnd, 0, -10000, -10000, width, height, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
    
    # 3. Restore it (without activating) so DWM renders it
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
    time.sleep(0.1) # Wait for DWM to render
    
    # 4. Check if it's rendered by reading a pixel using PrintWindow?
    # Actually, if it's off-screen, PrintWindow still works!
    import ctypes
    from ctypes import wintypes
    
    hdc = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hdc)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # PW_RENDERFULLCONTENT = 2
    ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    
    img.save("offscreen_test.png")
    print("Saved offscreen_test.png!")
    
    # 5. Hide/Minimize it again
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    
    # 6. Restore original position (but keep it minimized)
    win32gui.SetWindowPos(hwnd, 0, original_rect[0], original_rect[1], width, height, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
    
else:
    print("Leigod not found")
