"""
Site-specific scrapers for NYC apartment listings.

Each scraper function takes a set of seen URLs (mutated in-place to track
new listings) and returns a list of listing dicts.
"""

import time
from urllib.parse import urlencode, quote

from bs4 import BeautifulSoup

from .config import SEARCH_FILTERS, NEIGHBORHOODS
from .fetcher import fetch
from .parsers import extract_price, extract_beds, extract_baths, extract_sqft, make_listing


# ──────────────────────────────────────────────────────────────────────────────
# StreetEasy
# ──────────────────────────────────────────────────────────────────────────────

def scrape_streeteasy(seen_urls: set[str]) -> list[dict]:
    """Scrape StreetEasy rental listings."""
    source = "StreetEasy"
    listings = []
    all_neighborhoods = NEIGHBORHOODS["queens"] + NEIGHBORHOODS["brooklyn"]

    for hood in all_neighborhoods:
        for page in range(1, SEARCH_FILTERS["max_pages"] + 1):
            params = {
                "price": f"{SEARCH_FILTERS['min_price']}-{SEARCH_FILTERS['max_price']}",
                "beds": f"{SEARCH_FILTERS['min_beds']}-{SEARCH_FILTERS['max_beds']}",
            }
            if SEARCH_FILTERS["no_fee"]:
                params["no_fee"] = "true"

            url = (
                f"https://streeteasy.com/for-rent/{hood}?"
                f"{urlencode(params)}&page={page}"
            )

            html, _ = fetch(url, site=source)
            if not html:
                break

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(
                "div.searchCardList--listItem, "
                "div.listingCard, "
                "article[data-testid='listing-card'], "
                "div[class*='listing'], "
                "li[class*='result']"
            )
            if not cards:
                break

            for card in cards:
                text = card.get_text(" ", strip=True)

                link_tag = card.select_one("a[href*='/rental/']") or card.select_one("a[href]")
                if not link_tag:
                    continue
                href = link_tag.get("href", "")
                if href.startswith("/"):
                    href = "https://streeteasy.com" + href
                if href in seen_urls:
                    continue

                addr_tag = card.select_one(
                    "address, [class*='address'], "
                    "[data-testid='listing-address'], span[class*='street']"
                )
                address = addr_tag.get_text(strip=True) if addr_tag else ""

                notes_tag = card.select_one("[class*='subtitle'], [class*='detail']")
                notes = notes_tag.get_text(strip=True) if notes_tag else ""

                listings.append(make_listing(
                    source, hood, extract_price(text), extract_beds(text),
                    extract_baths(text), extract_sqft(text), address, href, notes,
                ))
                seen_urls.add(href)

            time.sleep(1.5)

    return listings


# ──────────────────────────────────────────────────────────────────────────────
# Zillow
# ──────────────────────────────────────────────────────────────────────────────

ZILLOW_BOROUGH_MAP = {
    "queens": "queens-new-york-ny",
    "brooklyn": "brooklyn-new-york-ny",
}


def scrape_zillow(seen_urls: set[str]) -> list[dict]:
    """Scrape Zillow rental listings."""
    source = "Zillow"
    listings = []

    for borough, hoods in NEIGHBORHOODS.items():
        for hood in hoods:
            for page in range(1, SEARCH_FILTERS["max_pages"] + 1):
                url = (
                    f"https://www.zillow.com/{ZILLOW_BOROUGH_MAP[borough]}/rentals/"
                    f"?searchQueryState="
                    f'{{"filterState":{{"price":{{"min":{SEARCH_FILTERS["min_price"]},'
                    f'"max":{SEARCH_FILTERS["max_price"]}}},'
                    f'"beds":{{"min":{SEARCH_FILTERS["min_beds"]},'
                    f'"max":{SEARCH_FILTERS["max_beds"]}}},'
                    f'"isForRent":{{"value":true}},'
                    f'"isForSaleByAgent":{{"value":false}},'
                    f'"isForSaleByOwner":{{"value":false}},'
                    f'"isNewConstruction":{{"value":false}},'
                    f'"isComingSoon":{{"value":false}},'
                    f'"isAuction":{{"value":false}},'
                    f'"isForSaleForeclosure":{{"value":false}}}}}}'
                )
                if page > 1:
                    url += f"&pagination=%7B%22currentPage%22%3A{page}%7D"

                html, _ = fetch(url, site=source)
                if not html:
                    break

                soup = BeautifulSoup(html, "lxml")
                cards = soup.select(
                    "article[data-test='property-card'], "
                    "div[class*='ListItem'], li[class*='ListItem'], "
                    "div[id*='grid-search-results'] li, "
                    "ul[class*='photo-cards'] li"
                )
                if not cards:
                    break

                for card in cards:
                    text = card.get_text(" ", strip=True)

                    link_tag = (
                        card.select_one("a[href*='/homedetails/']")
                        or card.select_one("a[href*='/b/']")
                        or card.select_one("a[href]")
                    )
                    if not link_tag:
                        continue
                    href = link_tag.get("href", "")
                    if href.startswith("/"):
                        href = "https://www.zillow.com" + href
                    if href in seen_urls:
                        continue

                    addr_tag = card.select_one(
                        "address, [data-test='property-card-addr'], [class*='address']"
                    )
                    address = addr_tag.get_text(strip=True) if addr_tag else ""

                    listings.append(make_listing(
                        source, hood, extract_price(text), extract_beds(text),
                        extract_baths(text), extract_sqft(text), address, href,
                    ))
                    seen_urls.add(href)

                time.sleep(2)

    return listings


# ──────────────────────────────────────────────────────────────────────────────
# Apartments.com
# ──────────────────────────────────────────────────────────────────────────────

def scrape_apartments_com(seen_urls: set[str]) -> list[dict]:
    """Scrape Apartments.com rental listings."""
    source = "Apartments.com"
    listings = []
    all_neighborhoods = NEIGHBORHOODS["queens"] + NEIGHBORHOODS["brooklyn"]

    for hood in all_neighborhoods:
        for page in range(1, SEARCH_FILTERS["max_pages"] + 1):
            url = (
                f"https://www.apartments.com/{hood}-new-york-ny/"
                f"{SEARCH_FILTERS['min_beds']}-to-{SEARCH_FILTERS['max_beds']}-bedrooms/"
                f"?bb=1&p={page}&px={SEARCH_FILTERS['max_price']}"
            )

            html, _ = fetch(url, site=source)
            if not html:
                break

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(
                "li.mortar-wrapper, article[data-listingid], "
                "div[class*='placard'], section[id*='placard']"
            )
            if not cards:
                break

            for card in cards:
                text = card.get_text(" ", strip=True)

                link_tag = (
                    card.select_one("a[href*='apartments.com']")
                    or card.select_one("a[href]")
                )
                if not link_tag:
                    continue
                href = link_tag.get("href", "")
                if href.startswith("/"):
                    href = "https://www.apartments.com" + href
                if not href.startswith("http"):
                    continue
                if href in seen_urls:
                    continue

                addr_tag = card.select_one(
                    "[class*='property-address'], [class*='location'], "
                    "p[class*='address'], div.property-address"
                )
                address = addr_tag.get_text(strip=True) if addr_tag else ""

                title_tag = card.select_one("[class*='property-title'], [class*='js-placardTitle']")
                notes = title_tag.get_text(strip=True) if title_tag else ""

                listings.append(make_listing(
                    source, hood, extract_price(text), extract_beds(text),
                    extract_baths(text), extract_sqft(text), address, href, notes,
                ))
                seen_urls.add(href)

            time.sleep(1.5)

    return listings


# ──────────────────────────────────────────────────────────────────────────────
# Craigslist
# ──────────────────────────────────────────────────────────────────────────────

CRAIGSLIST_BOROUGH_MAP = {"queens": "que", "brooklyn": "brk"}


def scrape_craigslist(seen_urls: set[str]) -> list[dict]:
    """Scrape Craigslist NYC rental listings."""
    source = "Craigslist"
    listings = []

    for borough, hoods in NEIGHBORHOODS.items():
        for hood in hoods:
            for page in range(SEARCH_FILTERS["max_pages"]):
                offset = page * 120
                params = {
                    "min_price": SEARCH_FILTERS["min_price"],
                    "max_price": SEARCH_FILTERS["max_price"],
                    "min_bedrooms": SEARCH_FILTERS["min_beds"],
                    "max_bedrooms": SEARCH_FILTERS["max_beds"],
                    "availabilityMode": 0,
                    "s": offset,
                }
                url = (
                    f"https://newyork.craigslist.org/search/"
                    f"{CRAIGSLIST_BOROUGH_MAP[borough]}/apa?"
                    f"{urlencode(params)}&query={quote(hood.replace('-', ' '))}"
                )

                html, _ = fetch(url, site=source)
                if not html:
                    break

                soup = BeautifulSoup(html, "lxml")
                rows = soup.select(
                    "li.cl-static-search-result, li.result-row, "
                    "div.result-info, ol.cl-static-search-results > li, "
                    "li[data-pid]"
                )
                if not rows:
                    break

                for row in rows:
                    text = row.get_text(" ", strip=True)

                    link_tag = (
                        row.select_one("a[href*='craigslist']")
                        or row.select_one("a[href]")
                    )
                    if not link_tag:
                        continue
                    href = link_tag.get("href", "")
                    if href.startswith("/"):
                        href = "https://newyork.craigslist.org" + href
                    if href in seen_urls:
                        continue

                    title = link_tag.get_text(strip=True)
                    hood_tag = row.select_one("[class*='hood'], small")
                    address = hood_tag.get_text(strip=True).strip("() ") if hood_tag else ""

                    listings.append(make_listing(
                        source, hood, extract_price(text), extract_beds(text),
                        extract_baths(text), extract_sqft(text), address, href, title,
                    ))
                    seen_urls.add(href)

                time.sleep(1)

    return listings


# ──────────────────────────────────────────────────────────────────────────────
# RentHop
# ──────────────────────────────────────────────────────────────────────────────

def scrape_renthop(seen_urls: set[str]) -> list[dict]:
    """Scrape RentHop rental listings."""
    source = "RentHop"
    listings = []
    all_neighborhoods = NEIGHBORHOODS["queens"] + NEIGHBORHOODS["brooklyn"]

    for hood in all_neighborhoods:
        for page in range(1, SEARCH_FILTERS["max_pages"] + 1):
            url = (
                f"https://www.renthop.com/{hood}-apartments-for-rent"
                f"?min_price={SEARCH_FILTERS['min_price']}"
                f"&max_price={SEARCH_FILTERS['max_price']}"
                f"&min_bed={SEARCH_FILTERS['min_beds']}"
                f"&max_bed={SEARCH_FILTERS['max_beds']}"
                f"&page={page}"
            )

            html, _ = fetch(url, site=source)
            if not html:
                break

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(
                "div.search-listing, div[class*='listing-card'], "
                "div[class*='search-result'], div[data-listing-id], "
                "article[class*='listing']"
            )
            if not cards:
                break

            for card in cards:
                text = card.get_text(" ", strip=True)

                link_tag = card.select_one("a[href*='/listings/']") or card.select_one("a[href]")
                if not link_tag:
                    continue
                href = link_tag.get("href", "")
                if href.startswith("/"):
                    href = "https://www.renthop.com" + href
                if href in seen_urls:
                    continue

                addr_tag = card.select_one(
                    "[class*='address'], [class*='street'], a[class*='listing-title']"
                )
                address = addr_tag.get_text(strip=True) if addr_tag else ""

                notes_tag = card.select_one("[class*='detail'], [class*='feature']")
                notes = notes_tag.get_text(strip=True) if notes_tag else ""

                listings.append(make_listing(
                    source, hood, extract_price(text), extract_beds(text),
                    extract_baths(text), extract_sqft(text), address, href, notes,
                ))
                seen_urls.add(href)

            time.sleep(1.5)

    return listings


# ──────────────────────────────────────────────────────────────────────────────
# REGISTRY — ordered list of (name, function) for the main loop
# ──────────────────────────────────────────────────────────────────────────────

SCRAPERS = [
    ("StreetEasy", scrape_streeteasy),
    ("Zillow", scrape_zillow),
    ("Apartments.com", scrape_apartments_com),
    ("Craigslist", scrape_craigslist),
    ("RentHop", scrape_renthop),
]
