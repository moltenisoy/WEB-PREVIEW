from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from config import load_config, save_config
from services_history import read_recent_sites
from storage import save_sites
from ui_main import MainWindow
from ui_settings import SettingsWindow
from triggers import TriggerManager


class AppController:
    def __init__(self, app: QApplication):
        self.app = app
        self.cfg = load_config()
        self.main = MainWindow()
        self.settings = SettingsWindow(self.cfg)
        self.settings.saved.connect(self.on_settings_saved)
        self.main.openSettingsRequested.connect(self.open_settings)

        self.tray = QSystemTrayIcon(QIcon())
        self.menu = QMenu()
        act_open = QAction("Abrir")
        act_open.triggered.connect(self.toggle_main)
        act_settings = QAction("Configuración")
        act_settings.triggered.connect(self.open_settings)
        act_exit = QAction("Salir")
        act_exit.triggered.connect(self.app.quit)
        self.menu.addAction(act_open)
        self.menu.addAction(act_settings)
        self.menu.addSeparator()
        self.menu.addAction(act_exit)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_sites)

        self.triggers = TriggerManager()
        self.triggers.set_callback(self.toggle_main)
        self.apply_triggers()
        self.apply_timer()
        self.refresh_sites()
        self.main.hide()

    def apply_timer(self):
        self.timer.stop()
        self.timer.start(int(self.cfg["refresh_interval_sec"]) * 1000)

    def apply_triggers(self):
        self.triggers.unregister_all()
        if self.cfg["trigger_hotkey_enabled"] and self.cfg["trigger_hotkey"]:
            self.triggers.register_hotkey(self.cfg["trigger_hotkey"])

    def on_tray_activated(self, reason):
        if self.cfg["trigger_tray_enabled"]:
            self.toggle_main()

    def toggle_main(self):
        if self.main.isVisible():
            self.main.hide()
        else:
            self.main.show()
            self.main.raise_()
            self.main.activateWindow()

    def open_settings(self):
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    def on_settings_saved(self, new_cfg):
        self.cfg.update(new_cfg)
        save_config(self.cfg)
        self.apply_triggers()
        self.apply_timer()
        self.refresh_sites()

    def refresh_sites(self):
        self.main.set_loading()
        items = read_recent_sites(limit=int(self.cfg["sites_limit"]))
        save_sites(items)
        if not items:
            self.main.set_empty()
            return
        self.main.show_sites(
            items,
            mode=self.cfg["layout_mode"],
            density=self.cfg["visual_density"]
        )