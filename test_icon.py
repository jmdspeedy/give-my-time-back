import win32gui
import win32con
import win32ui
from PIL import Image

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
    # Try to get the icon
    hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_SMALL, 0)
    if not hicon:
        hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICONSM)
    
    print(f"Icon handle: {hicon}")
else:
    print("Not found")
