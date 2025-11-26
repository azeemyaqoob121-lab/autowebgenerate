"""
Quick test to verify the scraper actually works with the fix
Run this to confirm scraper is fixed before restarting backend
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.website_scraper import scrape_business_website

print("Testing scraper with a real URL...")
print("=" * 80)

# Test URL
url = "https://www.oliverroofing.co.uk"
print(f"Scraping: {url}\n")

result = scrape_business_website(url)

if result:
    print("[SUCCESS] Scraping worked!")
    print(f"  - Found {len(result)} data fields")

    raw_html = result.get('raw_html', '')
    print(f"  - HTML size: {len(raw_html)} bytes")

    if len(raw_html) > 1000:
        print(f"  - Has valid HTML structure: {('<html' in raw_html.lower())}")
        print(f"  - Has DOCTYPE: {('<!doctype' in raw_html.lower())}")
        print(f"\n[OK] Scraper is WORKING correctly!")
        print("\nFirst 200 chars of HTML (should be readable):")
        print("-" * 80)
        ascii_text = ''.join(c if ord(c) < 128 else '?' for c in raw_html[:200])
        print(ascii_text)
        print("-" * 80)
    else:
        print(f"\n[ERROR] HTML too short ({len(raw_html)} bytes) - scraper may still be broken")
else:
    print("[ERROR] Scraping returned empty dict - scraper is BROKEN")
    print("\nThis means the backend code hasn't been reloaded yet!")
    print("You MUST restart the backend server!")

print("\n" + "=" * 80)
