import pywinauto
import traceback
import win32gui

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
    print(f"Found hwnd: {hwnd}")
    try:
        app = pywinauto.Application(backend="uia").connect(handle=hwnd)
        window = app.window(handle=hwnd)
        
        # Look for the pause or resume text in the tree
        # We don't want to print the whole tree, just check if we can find specific elements
        texts = []
        for elem in window.descendants():
            if elem.window_text():
                texts.append(elem.window_text())
                
        print(f"Found {len(texts)} text elements.")
        print(texts[:20]) # Print first 20
    except Exception as e:
        traceback.print_exc()
else:
    print("Not found")
