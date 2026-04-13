"""
HTTP fetching with automatic Selenium failsafe.

Primary method: requests with a realistic browser User-Agent header.
On block detection (403/429/503 or known block strings in HTML),
automatically switches that site to Selenium (undetected-chromedriver).
"""

import time

import requests

from .config import USER_AGENT, REQUEST_HEADERS, BLOCK_STRINGS

# ──────────────────────────────────────────────────────────────────────────────
# SELENIUM (optional)
# ──────────────────────────────────────────────────────────────────────────────

try:
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

_chrome_driver = None
_blocked_sites: set[str] = set()


def _get_driver():
    """Lazy-init a shared headless Chrome driver."""
    global _chrome_driver
    if _chrome_driver is None:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={USER_AGENT}")
        _chrome_driver = uc.Chrome(options=options)
    return _chrome_driver


def close_driver():
    """Close the shared Chrome driver if it was opened."""
    global _chrome_driver
    if _chrome_driver is not None:
        try:
            _chrome_driver.quit()
        except Exception:
            pass
        _chrome_driver = None


def _is_blocked(status_code: int, html: str) -> bool:
    """Detect if a response indicates blocking."""
    if status_code in (403, 429, 503):
        return True
    html_lower = html.lower()
    return any(s in html_lower for s in BLOCK_STRINGS)


def _fetch_selenium(url: str, site: str) -> tuple[str, str]:
    """Fetch a page via Selenium."""
    if not SELENIUM_AVAILABLE:
        print(
            f"\n  ✘ Selenium is not installed but {site} requires it.\n"
            f"    Install with:  pip install undetected-chromedriver selenium\n"
        )
        return "", url

    driver = _get_driver()
    driver.get(url)
    time.sleep(3)  # let JS render
    return driver.page_source, driver.current_url


def fetch(url: str, site: str = "") -> tuple[str, str]:
    """
    Fetch a URL transparently.

    Uses requests by default. Auto-switches to Selenium for a site if
    blocking is detected. Once a site switches, all future pages for
    that site use Selenium.

    Returns (html_string, final_url).
    """
    if site in _blocked_sites:
        return _fetch_selenium(url, site)

    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
        html = resp.text
        if not _is_blocked(resp.status_code, html):
            return html, resp.url
        print(f"  ⚠ Block detected on {site or url} (HTTP {resp.status_code}), switching to Selenium...")
    except requests.RequestException as e:
        print(f"  ⚠ Request failed for {site or url}: {e}, trying Selenium...")

    _blocked_sites.add(site)
    return _fetch_selenium(url, site)


def get_blocked_sites() -> set[str]:
    """Return set of site names that have been switched to Selenium."""
    return _blocked_sites
