import json
import os
from models import AppConfig


_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".browsedash_config.json")
_current_config: AppConfig = None


def load_config() -> AppConfig:
    global _current_config
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _current_config = AppConfig.from_dict(data)
    except Exception:
        _current_config = AppConfig()
        save_config(_current_config)
    return _current_config


def save_config(config: AppConfig):
    global _current_config
    _current_config = config
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)
    except Exception:
        pass


def get_config() -> AppConfig:
    global _current_config
    if _current_config is None:
        return load_config()
    return _current_config


def get_cache_dir() -> str:
    d = os.path.join(os.path.expanduser("~"), ".browsedash_cache")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d