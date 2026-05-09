import psutil
import json

CONFIG_FILE = "config.json"

def is_process_running(process_name):
    """Check if a process is currently running by its executable name."""
    if not process_name:
        return False
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def is_leigod_running():
    """Reads config and checks if the Leigod boost tunnel process is running."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        config = {}
        
    boost_process = config.get("leigod_boost_process", "networktunnel_proxy.exe")
    return is_process_running(boost_process)

def check_status():
    """Prints the current status to the console."""
    if is_leigod_running():
        print("STATUS: Leigod is ON (Boosting)")
        return True
    else:
        print("STATUS: Leigod is OFF (Paused)")
        return False

if __name__ == "__main__":
    check_status()
