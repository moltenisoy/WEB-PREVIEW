import keyboard
from PIL import Image
import pystray
import threading
import os

class TriggerManager:
    def __init__(self, config_manager, show_window_callback):
        self.config_manager = config_manager
        self.show_window_callback = show_window_callback
        self.tray_icon = None

    def setup_hotkey(self):
        try:
            config = self.config_manager.load()
            keyboard.unhook_all()
            hotkey = config.get("hotkey", "ctrl+shift+h")
            if hotkey:
                keyboard.add_hotkey(hotkey, self.show_window_callback)
        except:
            pass

    def setup_tray(self):
        try:
            image = Image.new('RGB', (64, 64), color=(40, 40, 40))
            menu = pystray.Menu(
                pystray.MenuItem("Show Dashboard", self.show_window_callback),
                pystray.MenuItem("Exit", self.exit_app)
            )
            self.tray_icon = pystray.Icon("DashboardApp", image, "History Dashboard", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except:
            pass

    def start(self):
        try:
            self.setup_hotkey()
            self.setup_tray()
        except:
            pass

    def exit_app(self, icon, item):
        try:
            icon.stop()
            os._exit(0)
        except:
            pass