"""Verify HTML is correct by saving to file"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.website_scraper import WebsiteContentScraper

scraper = WebsiteContentScraper("https://www.ccelectricalservices.co.uk")
success = scraper.fetch_website()

print(f"Fetch success: {success}")
print(f"HTML length: {len(scraper.html) if scraper.html else 0}")

# Save to file
if scraper.html:
    with open("test_scraped_html.html", "w", encoding="utf-8") as f:
        f.write(scraper.html)
    print("Saved HTML to test_scraped_html.html")

    # Check tags
    html_lower = scraper.html.lower()
    print(f"Has <!doctype: {('<!doctype' in html_lower)}")
    print(f"Has <html: {('<html' in html_lower)}")
    print(f"Has <body: {('<body' in html_lower)}")
    print(f"Has <div: {('<div' in html_lower)}")

    # Save first 500 chars (ASCII only)
    first_500_ascii = ''.join(c if ord(c) < 128 else '?' for c in scraper.html[:500])
    print(f"\nFirst 500 chars (ASCII only):")
    print(first_500_ascii)
