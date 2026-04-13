"""Main orchestration — ties all modules together."""

import traceback

from .config import SEARCH_FILTERS, NEIGHBORHOODS, TODAY
from .dedup import load_seen, save_seen
from .fetcher import SELENIUM_AVAILABLE, close_driver, get_blocked_sites
from .scrapers import SCRAPERS
from .excel import build_excel
from .emailer import send_email


def main():
    total_hoods = sum(len(v) for v in NEIGHBORHOODS.values())

    print("=" * 60)
    print(f"  🏠 NYC Apartment Scraper — {TODAY}")
    print("=" * 60)
    print(f"  Budget:    ${SEARCH_FILTERS['min_price']:,} – ${SEARCH_FILTERS['max_price']:,}")
    print(f"  Beds:      {SEARCH_FILTERS['min_beds']} – {SEARCH_FILTERS['max_beds']}")
    print(f"  Hoods:     {total_hoods} neighborhoods across Queens & Brooklyn")
    print(f"  Selenium:  {'Available' if SELENIUM_AVAILABLE else 'Not installed (requests only)'}")
    print(f"  Max pages: {SEARCH_FILTERS['max_pages']} per neighborhood per site")
    print("=" * 60)

    # 1. Load seen listings
    seen_urls = load_seen()
    print(f"\n  Loaded {len(seen_urls)} previously seen listing URLs")

    # 2. Run scrapers
    all_new_listings = []
    results = {}

    for name, scraper_fn in SCRAPERS:
        print(f"\n  ▸ Scraping {name}...")
        try:
            site_listings = scraper_fn(seen_urls)
            all_new_listings.extend(site_listings)
            blocked = get_blocked_sites()
            method = "Selenium" if name in blocked else "requests"
            results[name] = (len(site_listings), method)
            print(f"    ✓ {len(site_listings)} new listings ({method})")
        except Exception as e:
            results[name] = (0, "error")
            print(f"    ✘ Failed: {e}")
            traceback.print_exc()

    # 3. Close Selenium
    close_driver()

    # 4. Save seen listings
    save_seen(seen_urls)
    print(f"\n  Saved {len(seen_urls)} total seen URLs to seen_listings.json")

    # 5. Build Excel
    print("\n  Building Excel workbook...")
    build_excel(all_new_listings)

    # 6. Send email
    print("\n  Sending email...")
    send_email(all_new_listings)

    # 7. Final summary
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    for name, (count, method) in results.items():
        status = f"{count} listings" if method != "error" else "FAILED"
        print(f"  {name:20s} {status:>15s}  ({method})")
    print(f"  {'─' * 50}")
    print(f"  {'TOTAL':20s} {len(all_new_listings):>15d} new listings")
    print("=" * 60)
