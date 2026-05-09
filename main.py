import pystray
from PIL import Image, ImageDraw
import threading
import time
import os
import signal
import json
from pauser import pause_leigod
import checker
from logger import log
from i18n import t, set_lang, get_lang

CONFIG_FILE = "config.json"

INTERVAL_MAP = {
    5: "5_sec",
    60: "1_min",
    300: "5_min",
    600: "10_min",
    1800: "30_min"
}

# Global flag to control the background thread
running = True
current_interval = 300  # Default

def load_config():
    global current_interval
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            current_interval = config.get("check_interval_seconds", 300)
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
        config["language"] = get_lang()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        log.error(f"Error saving config: {e}")



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
        set_lang(lang)
        save_config()
        log.info(f"Language changed to {lang}")
        # Need to rebuild menu for dynamic strings to update
        icon.title = t("title")
        icon.menu = build_menu()
        icon.update_menu()
    return inner

def is_lang_checked(lang):
    return lambda item: get_lang() == lang

def on_quit(icon, item):
    """Callback to handle quitting the app."""
    global running
    running = False
    icon.stop()

import sys
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_image():
    """Load the custom icon or generate a simple fallback icon"""
    icon_path = resource_path("icon.png")
    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path)
        except Exception as e:
            log.error(f"Failed to load icon.png: {e}")
            
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
        log.info(t("log_checking", current_interval=current_interval))
        
        try:
            if not checker.is_leigod_running():
                log.info(t("log_already_paused"))
            else:
                log.info(t("log_leigod_on"))
                try:
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        monitored_games = json.load(f).get("monitored_games", [])
                except Exception:
                    monitored_games = []
                
                game_running = False
                for game in monitored_games:
                    if checker.is_process_running(game):
                        log.info(t("log_game_detected", game=game))
                        game_running = True
                        break
                        
                if not game_running:
                    pause_leigod()
        except Exception as e:
            log.error(f"[Error] Failed to check Leigod: {e}")
        
        # We loop in 1-second intervals so we can exit quickly if the app is quit,
        # or immediately trigger if the interval is reduced by the user.
        elapsed = 0
        while elapsed < current_interval and running:
            time.sleep(1)
            elapsed += 1

def open_log(icon, item):
    log_file = resource_path("give_my_time_back.log")
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
    os.startfile(log_file)

def build_menu():
    interval_items = []
    for interval, key in INTERVAL_MAP.items():
        interval_items.append(pystray.MenuItem(lambda item, k=key: t(k), set_interval_by_value(interval), checked=is_interval_checked(interval), radio=True))
        
    lang_items = []
    lang_items.append(pystray.MenuItem("English", set_language("English"), checked=is_lang_checked("English"), radio=True))
    lang_items.append(pystray.MenuItem("中文", set_language("中文"), checked=is_lang_checked("中文"), radio=True))

    return pystray.Menu(
        pystray.MenuItem(lambda item: t("check_interval"), pystray.Menu(*interval_items)),
        pystray.MenuItem(lambda item: t("language"), pystray.Menu(*lang_items)),
        pystray.MenuItem(lambda item: t("check_log"), open_log),
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
