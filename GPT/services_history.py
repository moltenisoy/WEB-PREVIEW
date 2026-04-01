import os
import shutil
import sqlite3
import tempfile
from urllib.parse import urlparse
from datetime import datetime, timedelta
from models import SiteItem
from services_browser import resolve_browser_family, get_possible_history_paths


def _domain(url):
    return urlparse(url).netloc.replace("www.", "").strip().lower()


def _chrome_time_to_str(v):
    base = datetime(1601, 1, 1)
    dt = base + timedelta(microseconds=int(v))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _normalize(rows, title_i, url_i, time_i, icon_i=None):
    out = []
    for r in rows:
        t = (r[title_i] or "").strip()
        u = (r[url_i] or "").strip()
        d = _domain(u)
        vv = ""
        if time_i is not None and r[time_i]:
            vv = str(r[time_i])
        ip = ""
        if icon_i is not None and r[icon_i]:
            ip = str(r[icon_i])
        if u:
            out.append(SiteItem(title=t or d, url=u, domain=d, visited_at=vv, icon_path=ip))
    return out


def _read_sqlite_copy(db_path, query):
    tmp = os.path.join(tempfile.gettempdir(), os.path.basename(db_path) + ".tmp_copy")
    shutil.copy2(db_path, tmp)
    conn = sqlite3.connect(tmp)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    os.remove(tmp)
    return rows


def read_recent_sites(limit=20):
    family = resolve_browser_family()
    paths = get_possible_history_paths(family)
    existing = [p for p in paths if os.path.exists(p)]

    if family == "chromium":
        for p in existing:
            rows = _read_sqlite_copy(
                p,
                f"SELECT title, url, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT {int(limit)}"
            )
            items = _normalize(rows, 0, 1, 2, None)
            normalized = []
            for i in items:
                v = ""
                if i.visited_at:
                    v = _chrome_time_to_str(i.visited_at)
                normalized.append(SiteItem(i.title, i.url, i.domain, v, ""))
            if normalized:
                return normalized

    if family == "firefox":
        for p in existing:
            rows = _read_sqlite_copy(
                p,
                f"""SELECT p.title, p.url, h.visit_date
                    FROM moz_places p
                    JOIN moz_historyvisits h ON p.id = h.place_id
                    ORDER BY h.visit_date DESC
                    LIMIT {int(limit)}"""
            )
            items = _normalize(rows, 0, 1, 2, None)
            normalized = []
            for i in items:
                v = ""
                if i.visited_at:
                    us = int(i.visited_at)
                    dt = datetime.fromtimestamp(us / 1000000.0)
                    v = dt.strftime("%Y-%m-%d %H:%M:%S")
                normalized.append(SiteItem(i.title, i.url, i.domain, v, ""))
            if normalized:
                return normalized

    return []