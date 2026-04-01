import os
import hashlib
import urllib.request
import ssl
from storage import get_cache_dir


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def get_favicon_path(domain: str) -> str:
    try:
        cache = get_cache_dir()
        fname = _url_hash(domain) + ".png"
        fpath = os.path.join(cache, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            return fpath
        urls_to_try = [
            f"https://www.google.com/s2/favicons?domain={domain}&sz=64",
            f"https://{domain}/favicon.ico",
        ]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        for url in urls_to_try:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=5, context=ctx)
                data = resp.read()
                if len(data) > 100:
                    with open(fpath, "wb") as f:
                        f.write(data)
                    return fpath
            except Exception:
                continue
    except Exception:
        pass
    return ""


def get_favicon_for_entries(entries):
    for entry in entries:
        try:
            if entry.domain:
                path = get_favicon_path(entry.domain)
                if path:
                    entry.favicon_path = path
        except Exception:
            pass
    return entries