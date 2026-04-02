import os
import shutil
import sqlite3
import tempfile
import winreg
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from models import SiteEntry


def _detect_default_browser() -> str:
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice",
        ) as key:
            prog_id = winreg.QueryValueEx(key, "ProgId")[0].lower()
            if "chrome" in prog_id:
                return "chrome"
            if "firefox" in prog_id:
                return "firefox"
            if "msedge" in prog_id or "edge" in prog_id:
                return "edge"
            if "opera" in prog_id:
                return "opera"
            if "brave" in prog_id:
                return "brave"
            if "vivaldi" in prog_id:
                return "vivaldi"
    except Exception:
        pass
    return "chrome"


def _get_chromium_paths(browser: str) -> list:
    local = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")
    paths = {
        "chrome": [os.path.join(local, r"Google\Chrome\User Data")],
        "edge": [os.path.join(local, r"Microsoft\Edge\User Data")],
        "brave": [os.path.join(local, r"BraveSoftware\Brave-Browser\User Data")],
        "opera": [
            os.path.join(appdata, r"Opera Software\Opera Stable"),
            os.path.join(appdata, r"Opera Software\Opera GX Stable"),
        ],
        "vivaldi": [os.path.join(local, r"Vivaldi\User Data")],
    }
    return paths.get(browser, paths["chrome"])


def _read_chromium_history(browser: str, max_sites: int) -> list:
    entries = []
    try:
        base_paths = _get_chromium_paths(browser)
        history_file = None
        for base in base_paths:
            if browser == "opera":
                candidate = os.path.join(base, "History")
                if os.path.exists(candidate):
                    history_file = candidate
                    break
            for profile in ["Default", "Profile 1", "Profile 2", "Profile 3"]:
                candidate = os.path.join(base, profile, "History")
                if os.path.exists(candidate):
                    history_file = candidate
                    break
            if history_file:
                break
        if not history_file:
            return entries
        tmp = os.path.join(tempfile.gettempdir(), f"browsedash_{browser}_history")
        shutil.copy2(history_file, tmp)
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?",
            (max_sites * 3,),
        )
        seen = set()
        for row in cursor.fetchall():
            url, title, visit_time = row[0], row[1], row[2]
            domain = urlparse(url).netloc.replace("www.", "")
            if not domain or domain in seen:
                continue
            if any(s in url for s in ["chrome://", "edge://", "brave://", "opera://", "vivaldi://", "chrome-extension://"]):
                continue
            seen.add(domain)
            time_str = ""
            try:
                epoch = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=visit_time)
                time_str = epoch.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
            entries.append(SiteEntry(
                title=title or domain,
                url=url,
                domain=domain,
                visit_time=time_str,
            ))
            if len(entries) >= max_sites:
                break
        conn.close()
        try:
            os.remove(tmp)
        except Exception:
            pass
    except Exception:
        pass
    return entries


def _get_firefox_profile() -> str:
    try:
        appdata = os.environ.get("APPDATA", "")
        profiles_dir = os.path.join(appdata, r"Mozilla\Firefox\Profiles")
        if not os.path.exists(profiles_dir):
            return ""
        for d in os.listdir(profiles_dir):
            full = os.path.join(profiles_dir, d)
            if os.path.isdir(full) and os.path.exists(os.path.join(full, "places.sqlite")):
                return full
    except Exception:
        pass
    return ""


def _read_firefox_history(max_sites: int) -> list:
    entries = []
    try:
        profile = _get_firefox_profile()
        if not profile:
            return entries
        db_path = os.path.join(profile, "places.sqlite")
        tmp = os.path.join(tempfile.gettempdir(), "browsedash_firefox_places")
        shutil.copy2(db_path, tmp)
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT p.url, p.title, h.visit_date FROM moz_places p "
            "JOIN moz_historyvisits h ON p.id = h.place_id "
            "ORDER BY h.visit_date DESC LIMIT ?",
            (max_sites * 3,),
        )
        seen = set()
        for row in cursor.fetchall():
            url, title, visit_date = row[0], row[1], row[2]
            domain = urlparse(url).netloc.replace("www.", "")
            if not domain or domain in seen:
                continue
            if any(s in url for s in ["about:", "moz-extension://"]):
                continue
            seen.add(domain)
            time_str = ""
            try:
                epoch = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=visit_date)
                time_str = epoch.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
            entries.append(SiteEntry(
                title=title or domain,
                url=url,
                domain=domain,
                visit_time=time_str,
            ))
            if len(entries) >= max_sites:
                break
        conn.close()
        try:
            os.remove(tmp)
        except Exception:
            pass
    except Exception:
        pass
    return entries


def get_browser_history(max_sites: int = 20) -> list:
    browser = _detect_default_browser()
    if browser == "firefox":
        entries = _read_firefox_history(max_sites)
    else:
        entries = _read_chromium_history(browser, max_sites)
    if not entries:
        for fallback in ["chrome", "edge", "firefox", "brave", "opera", "vivaldi"]:
            if fallback == browser:
                continue
            if fallback == "firefox":
                entries = _read_firefox_history(max_sites)
            else:
                entries = _read_chromium_history(fallback, max_sites)
            if entries:
                break
    return entries