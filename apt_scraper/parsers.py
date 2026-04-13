"""Helper functions for extracting listing fields from raw text."""

import re

from .config import TODAY


def extract_beds(text: str) -> str:
    """Extract bed count from text → e.g. '2 bd'."""
    if not text:
        return ""
    text = text.lower()
    if "studio" in text:
        return "Studio"
    m = re.search(r"(\d+)\s*(?:bd|bed|br|bedroom)", text)
    return f"{m.group(1)} bd" if m else ""


def extract_baths(text: str) -> str:
    """Extract bath count from text → e.g. '1 ba'."""
    if not text:
        return ""
    m = re.search(r"(\d+\.?\d*)\s*(?:ba|bath|bathroom)", text.lower())
    return f"{m.group(1)} ba" if m else ""


def extract_sqft(text: str) -> str:
    """Extract square footage from text → e.g. '800 sqft'."""
    if not text:
        return ""
    m = re.search(r"([\d,]+)\s*(?:sq\.?\s*ft|sqft|sf)", text.lower())
    return f"{m.group(1).replace(',', '')} sqft" if m else ""


def extract_price(text: str) -> str:
    """Extract price from text → e.g. '$2,500'."""
    if not text:
        return ""
    m = re.search(r"\$?([\d,]+)", text.replace(" ", ""))
    if m:
        val = m.group(1).replace(",", "")
        if val.isdigit() and int(val) >= 500:
            return f"${int(val):,}"
    return ""


def make_listing(
    source: str,
    neighborhood: str,
    price: str,
    beds: str,
    baths: str,
    sqft: str,
    address: str,
    url: str,
    notes: str = "",
) -> dict:
    """Create a listing dict with the standard schema."""
    return {
        "source": source,
        "neighborhood": neighborhood.replace("-", " ").title(),
        "price": price,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "address": address.strip() if address else "",
        "url": url.strip() if url else "",
        "notes": notes.strip() if notes else "",
        "date_found": TODAY,
    }
