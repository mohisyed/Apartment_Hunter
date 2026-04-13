"""Deduplication via persisted seen-listing URLs."""

import json
import os
from datetime import datetime

from .config import SEEN_FILE


def load_seen() -> set[str]:
    """Load seen listing URLs from disk."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("seen_urls", []))
    return set()


def save_seen(seen_urls: set[str]) -> None:
    """Save seen listing URLs to disk."""
    data = {
        "seen_urls": sorted(seen_urls),
        "last_run": datetime.now().isoformat(),
    }
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f, indent=2)
