import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_CONFIG = {
    "cards_size": "medium",
    "layout_mode": "thumbnails",
    "color_theme": "dark",
    "visual_density": "comfortable",
    "sites_limit": 20,
    "refresh_interval_sec": 15,
    "double_click_action": "open_url",
    "trigger_hotkey_enabled": True,
    "trigger_hotkey": "ctrl+shift+h",
    "trigger_tray_enabled": True,
    "trigger_mouse_enabled": False,
    "trigger_desktop_shortcut_enabled": True
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG.copy())
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)