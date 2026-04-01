import os
import json
from config import BASE_DIR


CACHE_FILE = os.path.join(BASE_DIR, "sites_cache.json")


def save_sites(items):
    payload = []
    for i in items:
        payload.append({
            "title": i.title,
            "url": i.url,
            "domain": i.domain,
            "visited_at": i.visited_at,
            "icon_path": i.icon_path
        })
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_sites():
    if not os.path.exists(CACHE_FILE):
        return []
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)