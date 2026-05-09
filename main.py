import pystray
from PIL import Image, ImageDraw
import threading
import time
import os
import signal
import json
from pauser import pause_leigod
import checker

CONFIG_FILE = "config.json"

INTERVAL_MAP = {
    5: "5_sec",
    60: "1_min",
    300: "5_min",
    600: "10_min",
    1800: "30_min"
}

TRANSLATIONS = {
    "English": {
        "check_interval": "Check Interval",
        "language": "Language",
        "quit": "Quit",
        "5_sec": "5 seconds (Debug)",
        "1_min": "1 minute",
        "5_min": "5 minutes",
        "10_min": "10 minutes",
        "30_min": "30 minutes",
        "title": "Give my time back"
    },
    "中文": {
        "check_interval": "检查间隔",
        "language": "语言 / Language",
        "quit": "退出",
        "5_sec": "5 秒 (调试)",
        "1_min": "1 分钟",
        "5_min": "5 分钟",
        "10_min": "10 分钟",
        "30_min": "30 分钟",
        "title": "还我时长"
    }
}

def t(key):
    return TRANSLATIONS.get(current_lang, TRANSLATIONS["English"]).get(key, key)

# Global flag to control the background thread
running = True
current_interval = 300  # Default
current_lang = "English"  # Default

def load_config():
    global current_interval, current_lang
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            current_interval = config.get("check_interval_seconds", 300)
            current_lang = config.get("language", "English")
    except Exception:
        pass

def save_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        config["check_interval_seconds"] = current_interval
        config["language"] = current_lang
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")



def is_interval_checked(interval):
    return lambda item: current_interval == interval

def set_interval_by_value(interval):
    def inner(icon, item):
        global current_interval
        current_interval = interval
        save_config()
        print(f"Interval changed to {interval} seconds")
    return inner

def set_language(lang):
    def inner(icon, item):
        global current_lang
        current_lang = lang
        save_config()
        print(f"Language changed to {lang}")
        # Need to rebuild menu for dynamic strings to update
        icon.title = t("title")
        icon.menu = build_menu()
        icon.update_menu()
    return inner

def is_lang_checked(lang):
    return lambda item: current_lang == lang

def on_quit(icon, item):
    """Callback to handle quitting the app."""
    global running
    running = False
    icon.stop()

def create_image():
    """Load the custom icon or generate a simple fallback icon"""
    if os.path.exists("icon.png"):
        try:
            return Image.open("icon.png")
        except Exception as e:
            print(f"Failed to load icon.png: {e}")
            
    width = 64
    height = 64
    color1 = "black"
    color2 = "red"
    
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def monitor_loop():
    """Background thread loop that checks Leigod."""
    while running:
        print(f"\nRunning scheduled check... (Current interval: {current_interval}s)")
        
        try:
            if not checker.is_leigod_running():
                print("Leigod is ALREADY PAUSED. Doing nothing.")
            else:
                print("Leigod is ON. Checking for active games...")
                try:
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        monitored_games = json.load(f).get("monitored_games", [])
                except Exception:
                    monitored_games = []
                
                game_running = False
                for game in monitored_games:
                    if checker.is_process_running(game):
                        print(f"Game detected: {game}. Will NOT pause.")
                        game_running = True
                        break
                        
                if not game_running:
                    pause_leigod()
        except Exception as e:
            print(f"[Error] Failed to check Leigod: {e}")
        
        # We loop in 1-second intervals so we can exit quickly if the app is quit,
        # or immediately trigger if the interval is reduced by the user.
        elapsed = 0
        while elapsed < current_interval and running:
            time.sleep(1)
            elapsed += 1

def build_menu():
    interval_items = []
    for interval, key in INTERVAL_MAP.items():
        # Lambda for text to ensure dynamic translation, although here we rebuild menu anyway
        interval_items.append(pystray.MenuItem(lambda item, k=key: t(k), set_interval_by_value(interval), checked=is_interval_checked(interval), radio=True))
        
    lang_items = []
    lang_items.append(pystray.MenuItem("English", set_language("English"), checked=is_lang_checked("English"), radio=True))
    lang_items.append(pystray.MenuItem("中文", set_language("中文"), checked=is_lang_checked("中文"), radio=True))

    return pystray.Menu(
        pystray.MenuItem(lambda item: t("check_interval"), pystray.Menu(*interval_items)),
        pystray.MenuItem(lambda item: t("language"), pystray.Menu(*lang_items)),
        pystray.MenuItem(lambda item: t("quit"), on_quit)
    )

def setup_tray():
    """Setup and run the system tray icon."""
    icon = pystray.Icon("LeigodAutoPause")
    icon.menu = build_menu()
    icon.icon = create_image()
    icon.title = t("title")
    icon.run()

def signal_handler(sig, frame):
    print('\nCtrl+C detected! Exiting immediately...')
    os._exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    load_config()
    print("Starting Leigod Auto Pause...")
    print("-> To quit: Press Ctrl+C here, or right-click the red/black icon in the Windows system tray (bottom right).")
    # Start the monitoring thread
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Run the system tray icon (this blocks the main thread)
    setup_tray()
