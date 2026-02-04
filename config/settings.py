# settings.py
import os

def base_url() -> str:
    target_url = (os.getenv("TARGET_URL") or "").strip()
    if not target_url:
        raise RuntimeError("TARGET_URL is not set.")
    return target_url.rstrip("/")  # normalize once

def url(path: str) -> str:
    return f"{base_url()}/{path.lstrip('/')}"
