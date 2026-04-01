from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QCheckBox, QPushButton, QLineEdit


class SettingsWindow(QWidget):
    saved = Signal(dict)

    def __init__(self, cfg):
        super().__init__()
        self.setWindowTitle("Configuración")
        self.resize(420, 430)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.cards_size = QComboBox()
        self.cards_size.addItems(["small", "medium", "large"])
        self.cards_size.setCurrentText(cfg["cards_size"])

        self.layout_mode = QComboBox()
        self.layout_mode.addItems(["thumbnails", "text", "compact"])
        self.layout_mode.setCurrentText(cfg["layout_mode"])

        self.color_theme = QComboBox()
        self.color_theme.addItems(["dark", "light"])
        self.color_theme.setCurrentText(cfg["color_theme"])

        self.visual_density = QComboBox()
        self.visual_density.addItems(["compact", "comfortable"])
        self.visual_density.setCurrentText(cfg["visual_density"])

        self.sites_limit = QSpinBox()
        self.sites_limit.setRange(5, 100)
        self.sites_limit.setValue(int(cfg["sites_limit"]))

        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 600)
        self.refresh_interval.setValue(int(cfg["refresh_interval_sec"]))

        self.double_click_action = QComboBox()
        self.double_click_action.addItems(["open_url"])
        self.double_click_action.setCurrentText(cfg["double_click_action"])

        self.hotkey_enabled = QCheckBox()
        self.hotkey_enabled.setChecked(bool(cfg["trigger_hotkey_enabled"]))

        self.hotkey = QLineEdit(cfg["trigger_hotkey"])

        self.tray_enabled = QCheckBox()
        self.tray_enabled.setChecked(bool(cfg["trigger_tray_enabled"]))

        self.mouse_enabled = QCheckBox()
        self.mouse_enabled.setChecked(bool(cfg["trigger_mouse_enabled"]))

        self.shortcut_enabled = QCheckBox()
        self.shortcut_enabled.setChecked(bool(cfg["trigger_desktop_shortcut_enabled"]))

        form.addRow("Tamaño tarjetas", self.cards_size)
        form.addRow("Modo vista", self.layout_mode)
        form.addRow("Tema", self.color_theme)
        form.addRow("Densidad visual", self.visual_density)
        form.addRow("Cantidad de sitios", self.sites_limit)
        form.addRow("Intervalo actualización (seg)", self.refresh_interval)
        form.addRow("Doble click", self.double_click_action)
        form.addRow("Hotkey activo", self.hotkey_enabled)
        form.addRow("Combinación hotkey", self.hotkey)
        form.addRow("Trigger bandeja", self.tray_enabled)
        form.addRow("Trigger mouse", self.mouse_enabled)
        form.addRow("Trigger acceso directo", self.shortcut_enabled)

        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self._emit_save)

        root.addLayout(form)
        root.addWidget(btn_save)

    def _emit_save(self):
        self.saved.emit({
            "cards_size": self.cards_size.currentText(),
            "layout_mode": self.layout_mode.currentText(),
            "color_theme": self.color_theme.currentText(),
            "visual_density": self.visual_density.currentText(),
            "sites_limit": int(self.sites_limit.value()),
            "refresh_interval_sec": int(self.refresh_interval.value()),
            "double_click_action": self.double_click_action.currentText(),
            "trigger_hotkey_enabled": bool(self.hotkey_enabled.isChecked()),
            "trigger_hotkey": self.hotkey.text().strip().lower(),
            "trigger_tray_enabled": bool(self.tray_enabled.isChecked()),
            "trigger_mouse_enabled": bool(self.mouse_enabled.isChecked()),
            "trigger_desktop_shortcut_enabled": bool(self.shortcut_enabled.isChecked())
        })