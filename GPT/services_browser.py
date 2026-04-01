import os
import winreg


def get_default_browser_prog_id():
    key_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        prog_id, _ = winreg.QueryValueEx(key, "ProgId")
    return prog_id.lower()


def resolve_browser_family():
    prog = get_default_browser_prog_id()
    if "chrome" in prog:
        return "chromium"
    if "edge" in prog or "microsoftedge" in prog:
        return "chromium"
    if "firefox" in prog:
        return "firefox"
    if "opera" in prog:
        return "chromium"
    return "chromium"


def get_possible_history_paths(family):
    local = os.environ.get("LOCALAPPDATA", "")
    roaming = os.environ.get("APPDATA", "")
    paths = []
    if family == "chromium":
        paths.extend([
            os.path.join(local, "Google", "Chrome", "User Data", "Default", "History"),
            os.path.join(local, "Microsoft", "Edge", "User Data", "Default", "History"),
            os.path.join(roaming, "Opera Software", "Opera Stable", "History"),
            os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data", "Default", "History")
        ])
    if family == "firefox":
        ff_profiles = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
        if os.path.isdir(ff_profiles):
            for p in os.listdir(ff_profiles):
                paths.append(os.path.join(ff_profiles, p, "places.sqlite"))
    return paths