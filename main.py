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
INTERVALS = {
    "5 seconds (Debug)": 5,
    "1 minute": 60,
    "5 minutes": 300,
    "10 minutes": 600,
    "30 minutes": 1800
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
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def set_interval(icon, item):
    global current_interval
    current_interval = INTERVALS[item.text]
    save_config()
    print(f"Interval changed to {item.text}")

def is_interval_checked(item):
    return current_interval == INTERVALS[item.text]

def create_image():
    """Generate a simple icon for the system tray"""
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
                print("Leigod is ON. Proceeding to pause...")
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

def on_quit(icon, item):
    """Callback to handle quitting the app."""
    global running
    running = False
    icon.stop()

def setup_tray():
    """Setup and run the system tray icon."""
    
    interval_items = []
    for label in INTERVALS.keys():
        interval_items.append(pystray.MenuItem(label, set_interval, checked=is_interval_checked, radio=True))
        
    icon = pystray.Icon("LeigodAutoPause")
    icon.menu = pystray.Menu(
        pystray.MenuItem("Check Interval", pystray.Menu(*interval_items)),
        pystray.MenuItem("Quit", on_quit)
    )
    icon.icon = create_image()
    icon.title = "Leigod Auto Pause"
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
