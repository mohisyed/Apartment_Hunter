"""Central configuration for the NYC apartment scraper."""

from datetime import date

# ──────────────────────────────────────────────────────────────────────────────
# SEARCH FILTERS (tweak these)
# ──────────────────────────────────────────────────────────────────────────────

SEARCH_FILTERS = {
    "min_price": 1500,
    "max_price": 3000,
    "min_beds": 1,       # 0 = studio
    "max_beds": 3,
    "no_fee": False,
    "max_pages": 5,      # per neighborhood per site
}

# ──────────────────────────────────────────────────────────────────────────────
# NEIGHBORHOODS
# ──────────────────────────────────────────────────────────────────────────────

NEIGHBORHOODS = {
    "queens": [
        "sunnyside", "woodhaven", "woodside", "long-island-city",
        "hunters-point", "maspeth", "middle-village", "queens-village",
        "ridgewood", "astoria", "ditmars-steinway", "auburndale",
    ],
    "brooklyn": [
        "bedford-stuyvesant", "bushwick", "dumbo", "downtown-brooklyn",
        "greenpoint", "park-slope", "prospect-heights",
        "prospect-park-south", "williamsburg", "east-williamsburg",
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# EMAIL
# ──────────────────────────────────────────────────────────────────────────────

EMAIL_CONFIG = {
    "enabled": True,
    "from": "you@gmail.com",
    "to": ["you@gmail.com", "gf@gmail.com"],
    "subject": "🏠 NYC Apartments — Daily Update {date}",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "password": "xxxx xxxx xxxx xxxx",  # Gmail App Password
}

# ──────────────────────────────────────────────────────────────────────────────
# FILE PATHS
# ──────────────────────────────────────────────────────────────────────────────

SEEN_FILE = "seen_listings.json"
EXCEL_FILE = "apartments_NYC.xlsx"

# ──────────────────────────────────────────────────────────────────────────────
# HTTP
# ──────────────────────────────────────────────────────────────────────────────

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

BLOCK_STRINGS = [
    "captcha", "robot", "access denied", "are you a human",
    "unusual traffic", "verify you are", "cloudflare", "just a moment",
    "enable javascript", "checking your browser",
]

# ──────────────────────────────────────────────────────────────────────────────
# SITE SHEET NAMES (Excel tab labels)
# ──────────────────────────────────────────────────────────────────────────────

SITE_SHEET_NAMES = {
    "StreetEasy": "🏠 StreetEasy",
    "Zillow": "🏠 Zillow",
    "Apartments.com": "🏠 Apartments.com",
    "Craigslist": "🏠 Craigslist",
    "RentHop": "🏠 RentHop",
}

# ──────────────────────────────────────────────────────────────────────────────
# DERIVED
# ──────────────────────────────────────────────────────────────────────────────

TODAY = date.today().isoformat()
