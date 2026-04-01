from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SiteEntry:
    title: str = ""
    url: str = ""
    domain: str = ""
    visit_time: str = ""
    favicon_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


@dataclass
class TriggerConfig:
    hotkey_enabled: bool = True
    hotkey_combo: str = "ctrl+shift+b"
    tray_click_enabled: bool = True
    mouse_gesture_enabled: bool = False
    mouse_gesture_type: str = "double_right"
    desktop_shortcut_enabled: bool = True


@dataclass
class AppConfig:
    card_width: int = 280
    card_height: int = 160
    columns: int = 4
    max_sites: int = 20
    refresh_interval: int = 300
    view_mode: str = "thumbnails"
    double_click_action: str = "open_browser"
    theme: str = "dark"
    accent_color: str = "#3B82F6"
    card_border_radius: int = 12
    card_spacing: int = 10
    font_size: int = 13
    show_domain: bool = True
    show_time: bool = True
    show_favicon: bool = True
    trigger: TriggerConfig = field(default_factory=TriggerConfig)

    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, TriggerConfig):
                d[k] = v.__dict__
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data):
        trigger_data = data.get("trigger", {})
        trigger = TriggerConfig(**trigger_data) if trigger_data else TriggerConfig()
        return cls(trigger=trigger, **{k: v for k, v in data.items() if k in cls.__dataclass_fields__ and k != "trigger"})