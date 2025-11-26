"""Direct test to see if scraper changes are loaded"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Importing scraper...")
from app.services.website_scraper import WebsiteContentScraper

print("Creating scraper instance...")
scraper = WebsiteContentScraper("https://www.ccelectricalservices.co.uk")

print("Fetching website...")
success = scraper.fetch_website()

print(f"Fetch success: {success}")
print(f"HTML length: {len(scraper.html) if scraper.html else 0}")
print(f"First 200 chars: {scraper.html[:200] if scraper.html else 'NONE'}")

# Check for HTML tags
if scraper.html:
    html_lower = scraper.html.lower()
    print(f"Has <!doctype: {('<!doctype' in html_lower)}")
    print(f"Has <html: {('<html' in html_lower)}")
    print(f"Has <body: {('<body' in html_lower)}")
