import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import os
from logger import log_queue, LOG_FILE
from i18n import t

# Global reference to prevent multiple windows
_log_window = None

def _run_gui():
    global _log_window
    
    root = tk.Tk()
    root.title(t("check_log"))
    root.geometry("700x400")
    root.configure(bg="#1e1e1e")
    
    # Configure grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create text widget
    text_area = scrolledtext.ScrolledText(
        root, 
        wrap=tk.WORD, 
        bg="#1e1e1e", 
        fg="#d4d4d4", 
        font=("Consolas", 10),
        padx=10,
        pady=10,
        insertbackground="white" # Cursor color
    )
    text_area.grid(row=0, column=0, sticky="nsew")
    
    # Make it read-only
    text_area.configure(state='disabled')
    
    # Load history from file
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                history = f.read()
                text_area.configure(state='normal')
                text_area.insert(tk.END, history)
                text_area.configure(state='disabled')
                text_area.see(tk.END)
        except Exception:
            pass

    # Function to poll the queue for new messages
    def check_queue():
        try:
            while True:
                msg = log_queue.get_nowait()
                text_area.configure(state='normal')
                text_area.insert(tk.END, msg + "\n")
                text_area.configure(state='disabled')
                text_area.see(tk.END)
        except queue.Empty:
            pass
        finally:
            root.after(200, check_queue)

    # Start polling
    root.after(200, check_queue)
    
    # Handle window close
    def on_close():
        global _log_window
        _log_window = None
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    _log_window = root
    
    # Bring to front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()

def show_log_window():
    global _log_window
    if _log_window is not None:
        try:
            _log_window.lift()
            _log_window.attributes('-topmost', True)
            _log_window.after_idle(_log_window.attributes, '-topmost', False)
        except tk.TclError:
            # Window was destroyed somehow without clearing the reference
            _log_window = None
            threading.Thread(target=_run_gui, daemon=True).start()
    else:
        # Spawn UI in a background thread so it doesn't block pystray
        threading.Thread(target=_run_gui, daemon=True).start()

if __name__ == "__main__":
    show_log_window()
