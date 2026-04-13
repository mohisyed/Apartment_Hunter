"""
NYC Apartment Scraper
=====================
Scrapes rental listings daily from 5 sites (StreetEasy, Zillow, Apartments.com,
Craigslist NYC, RentHop), deduplicates across runs, saves to a formatted Excel
workbook, and emails the workbook as an attachment.

Scheduling
----------
Mac/Linux crontab:
    0 8 * * * /path/to/venv/bin/python -m apt_scraper

Windows Task Scheduler:
    Daily trigger, action = /path/to/venv/Scripts/python -m apt_scraper

Dependencies
------------
Core (always needed):
    pip install requests beautifulsoup4 lxml openpyxl

Failsafe (optional, auto-detected):
    pip install undetected-chromedriver selenium
"""
