import threading
import os
import customtkinter as ctk
from PIL import Image, ImageDraw
from storage import load_config, get_config
from triggers import TriggerManager


class BrowseDashApp:
    def __init__(self):
        self._root = None
        self._main_window = None
        self._config_window = None
        self._tray_thread = None
        self._tray_icon = None
        self._trigger_manager = None

    def run(self):
        try:
            load_config()
            self._root = ctk.CTk()
            self._root.withdraw()
            self._root.title("BrowseDash Root")
            self._trigger_manager = TriggerManager(self._show_main_safe)
            self._trigger_manager.setup(get_config().trigger)
            self._start_tray()
            self._root.after(300, self._show_main)
            self._root.mainloop()
        except Exception:
            pass

    def _show_main_safe(self):
        try:
            if self._root:
                self._root.after(0, self._show_main)
        except Exception:
            pass

    def _show_main(self):
        try:
            if self._main_window is None or not self._main_window.winfo_exists():
                from ui_main import MainWindow
                self._main_window = MainWindow(
                    self._root,
                    open_config_callback=self._show_config,
                )
            else:
                self._main_window.show()
        except Exception:
            pass

    def _show_config(self):
        try:
            if self._config_window is None or not self._config_window.winfo_exists():
                from ui_config import ConfigWindow
                self._config_window = ConfigWindow(
                    self._root,
                    on_save_callback=self._on_config_saved,
                )
            else:
                self._config_window.lift()
                self._config_window.focus_force()
        except Exception:
            pass

    def _on_config_saved(self):
        try:
            config = get_config()
            if self._main_window and self._main_window.winfo_exists():
                self._main_window.refresh_config()
            if self._trigger_manager:
                self._trigger_manager.update_config(config.trigger)
        except Exception:
            pass

    def _create_tray_icon_image(self):
        try:
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill="#3B82F6")
            draw.rounded_rectangle([10, 10, 30, 28], radius=4, fill="#FFFFFF")
            draw.rounded_rectangle([34, 10, 54, 28], radius=4, fill="#93C5FD")
            draw.rounded_rectangle([10, 32, 30, 50], radius=4, fill="#93C5FD")
            draw.rounded_rectangle([34, 32, 54, 50], radius=4, fill="#FFFFFF")
            return img
        except Exception:
            img = Image.new("RGBA", (64, 64), "#3B82F6")
            return img

    def _start_tray(self):
        try:
            import pystray
            icon_image = self._create_tray_icon_image()
            menu = pystray.Menu(
                pystray.MenuItem("Abrir BrowseDash", self._tray_show, default=True),
                pystray.MenuItem("Configuraci\u00f3n", self._tray_config),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", self._tray_quit),
            )
            self._tray_icon = pystray.Icon("BrowseDash", icon_image, "BrowseDash", menu)
            self._tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
            self._tray_thread.start()
        except Exception:
            pass

    def _tray_show(self, icon=None, item=None):
        try:
            self._show_main_safe()
        except Exception:
            pass

    def _tray_config(self, icon=None, item=None):
        try:
            if self._root:
                self._root.after(0, self._show_config)
        except Exception:
            pass

    def _tray_quit(self, icon=None, item=None):
        try:
            if self._trigger_manager:
                self._trigger_manager.stop_all()
            if self._tray_icon:
                self._tray_icon.stop()
            if self._root:
                self._root.after(0, self._root.destroy)
        except Exception:
            os._exit(0)