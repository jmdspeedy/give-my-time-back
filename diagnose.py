import psutil
import time
import os

def monitor():
    print("Watching for process changes...")
    print("👉 Please go to Leigod and click PAUSE, then click START.")
    print("Press Ctrl+C when you are done.\n")
    
    previous = set()
    first_run = True
    
    while True:
        current = set()
        # Scan all processes
        for p in psutil.process_iter(['name', 'exe']):
            try:
                exe = p.info.get('exe', '')
                name = p.info.get('name', '')
                if exe and ('leigod' in exe.lower() or 'leishen' in exe.lower() or 'proxy' in exe.lower()):
                    current.add(name)
            except Exception:
                pass
                
        if not first_run:
            started = current - previous
            stopped = previous - current
            if started: 
                print(f"✅ Process STARTED (Boosting?): {started}")
            if stopped: 
                print(f"❌ Process STOPPED (Paused?): {stopped}")
        else:
            first_run = False
            print(f"Currently running: {current}")
            print("-" * 40)
        
        previous = current
        time.sleep(1)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\nExiting...")
