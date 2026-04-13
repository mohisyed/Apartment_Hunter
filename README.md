# Apartment Hunter

A Python scraper that collects NYC rental listings daily from 5 major sites, deduplicates across runs, saves everything to a formatted Excel workbook, and emails it as an attachment.

## Sites Scraped

| Site | URL |
|------|-----|
| StreetEasy | streeteasy.com |
| Zillow | zillow.com |
| Apartments.com | apartments.com |
| Craigslist NYC | newyork.craigslist.org |
| RentHop | renthop.com |

## Neighborhoods Covered

**Queens:** Sunnyside, Woodhaven, Woodside, Long Island City, Hunters Point, Maspeth, Middle Village, Queens Village, Ridgewood, Astoria, Ditmars-Steinway, Auburndale

**Brooklyn:** Bedford-Stuyvesant, Bushwick, DUMBO, Downtown Brooklyn, Greenpoint, Park Slope, Prospect Heights, Prospect Park South, Williamsburg, East Williamsburg

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/mohisyed/Apartment_Hunter.git
cd Apartment_Hunter
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

Open `apt_scraper/config.py` and update:

- **Search filters** — price range, bedroom count, no-fee preference, max pages per neighborhood
- **Neighborhoods** — add or remove neighborhoods from either borough
- **Email** — set your Gmail address, recipient(s), and [App Password](https://myaccount.google.com/apppasswords)

### 5. Run

```bash
python -m apt_scraper
```

## Configuration

All settings live in `apt_scraper/config.py`:

```python
SEARCH_FILTERS = {
    "min_price": 1500,
    "max_price": 3000,
    "min_beds": 1,       # 0 = studio
    "max_beds": 3,
    "no_fee": False,
    "max_pages": 5,      # per neighborhood per site
}
```

### Email Setup

The scraper sends results via Gmail SMTP. You need a **Gmail App Password** (not your regular password):

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Generate a new app password for "Mail"
3. Paste it into `EMAIL_CONFIG["password"]` in `config.py`

```python
EMAIL_CONFIG = {
    "enabled": True,
    "from": "you@gmail.com",
    "to": ["you@gmail.com", "gf@gmail.com"],
    "password": "xxxx xxxx xxxx xxxx",  # App Password here
}
```

Set `"enabled": False` to skip email and just generate the Excel file.

## How It Works

### Scraping

Each run hits all 5 sites across every configured neighborhood. The scraper uses `requests` with a realistic browser User-Agent by default. If a site blocks the request (HTTP 403/429/503 or known block strings like "captcha", "cloudflare", etc.), it automatically switches that site to Selenium via `undetected-chromedriver` for the rest of the run.

### Deduplication

Listing URLs are persisted in `seen_listings.json`. On every run, the scraper loads this file first and skips any URL already seen. New URLs are appended after scraping completes. This means **no listing ever appears twice** across runs.

### Excel Output

Results are saved to `apartments_NYC.xlsx` with these sheets:

| Sheet | Purpose |
|-------|---------|
| Summary | Per-site counts (new today + total), refreshed each run |
| All Listings | Master sheet, all sites combined |
| StreetEasy | StreetEasy listings only |
| Zillow | Zillow listings only |
| Apartments.com | Apartments.com listings only |
| Craigslist | Craigslist listings only |
| RentHop | RentHop listings only |

Each sheet has:
- Auto-filters and frozen header row
- Clickable URL hyperlinks
- Alternating row colors for readability
- Green highlighting on new listings from the current run

The workbook is cumulative — each run appends new listings to existing sheets.

### Email

After saving the Excel file, the scraper emails it as an attachment with an HTML summary showing how many new listings were found per site.

## Selenium Failsafe (Optional)

Selenium is **not required** — the scraper works with `requests` alone. But if sites start blocking you, install the optional dependencies:

```bash
pip install undetected-chromedriver selenium
```

The scraper auto-detects whether Selenium is available and prints a helpful message if it's needed but not installed. Switching is per-site and transparent — you don't need to configure anything.

## Scheduling

Set it up to run daily and wake up to fresh listings.

**Mac/Linux (crontab):**

```bash
crontab -e
# Add this line (adjust paths):
0 8 * * * /path/to/Apartment_Hunter/venv/bin/python -m apt_scraper
```

**Windows (Task Scheduler):**

Create a daily trigger with action:
```
Program: C:\path\to\Apartment_Hunter\venv\Scripts\python.exe
Arguments: -m apt_scraper
Start in: C:\path\to\Apartment_Hunter
```

## Project Structure

```
Apartment_Hunter/
├── apt_scraper/
│   ├── __init__.py      # Package docstring
│   ├── __main__.py      # Entry point for python -m apt_scraper
│   ├── config.py        # All settings: filters, neighborhoods, email, paths
│   ├── dedup.py         # Seen-URL persistence (seen_listings.json)
│   ├── emailer.py       # Gmail SMTP sender with HTML body + attachment
│   ├── excel.py         # Workbook creation, styling, and sheet management
│   ├── fetcher.py       # HTTP requests + automatic Selenium fallback
│   ├── main.py          # Orchestration: ties all modules together
│   ├── parsers.py       # Regex extractors for price, beds, baths, sqft
│   └── scrapers.py      # One function per site + SCRAPERS registry
├── venv/                # Python virtual environment (not committed)
├── .gitignore
├── CONTRIBUTING.md      # Branching conventions and workflow
├── README.md
└── requirements.txt     # Pinned Python dependencies
```

## Dependencies

**Core (required):**

| Package | Purpose |
|---------|---------|
| requests | HTTP requests with browser headers |
| beautifulsoup4 | HTML parsing |
| lxml | Fast HTML parser backend |
| openpyxl | Excel workbook creation and formatting |

**Optional (auto-detected):**

| Package | Purpose |
|---------|---------|
| undetected-chromedriver | Bypass bot detection via headless Chrome |
| selenium | Browser automation (used by undetected-chromedriver) |

## Output Files

These files are generated at runtime and excluded from git:

| File | Purpose |
|------|---------|
| `apartments_NYC.xlsx` | Cumulative Excel workbook with all listings |
| `seen_listings.json` | Deduplication state — tracks every URL ever scraped |

## Listing Schema

Every listing captured contains:

| Field | Example |
|-------|---------|
| source | StreetEasy |
| neighborhood | Long Island City |
| price | $2,500 |
| beds | 2 bd |
| baths | 1 ba |
| sqft | 800 sqft |
| address | 45-10 Court Square |
| url | https://streeteasy.com/rental/... |
| notes | No fee, doorman building |
| date_found | 2026-04-12 |
