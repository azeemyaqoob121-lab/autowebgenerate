"""Test color extraction from business websites"""
import sys
import codecs
from app.services.website_scraper import scrape_business_website
from app.services.content_extractor import extract_business_content

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Test with a real business website
test_url = input("Enter business website URL to test: ")

print(f"\n{'='*80}")
print(f"Testing color extraction from: {test_url}")
print(f"{'='*80}\n")

# Step 1: Scrape website
print("Step 1: Scraping website...")
try:
    scraped_data = scrape_business_website(test_url)
    raw_html = scraped_data.get("raw_html", "")
    print(f"✓ Successfully scraped {len(raw_html)} characters of HTML")
except Exception as e:
    print(f"✗ Scraping failed: {e}")
    sys.exit(1)

# Step 2: Extract colors
print("\nStep 2: Extracting colors from HTML...")
try:
    extracted_content = extract_business_content(
        html_content=raw_html,
        base_url=test_url,
        business_phone=None
    )

    colors = extracted_content.get("colors", [])
    logos = extracted_content.get("logos", [])

    print(f"\n{'='*80}")
    print(f"EXTRACTION RESULTS:")
    print(f"{'='*80}")
    print(f"\n🎨 Colors extracted: {len(colors)}")

    if colors:
        print("\nExtracted colors (in order of frequency):")
        for i, color in enumerate(colors, 1):
            # Show color preview
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            print(f"  {i}. {color} - RGB({r}, {g}, {b})")
    else:
        print("  ✗ NO COLORS FOUND!")
        print("\nDebug: Showing first 1000 chars of HTML:")
        print(raw_html[:1000])

    print(f"\n🖼️ Logos extracted: {len(logos)}")
    if logos:
        for i, logo in enumerate(logos, 1):
            print(f"  {i}. {logo}")
    else:
        print("  ✗ NO LOGOS FOUND!")

    print(f"\n📊 Metadata:")
    metadata = extracted_content.get("metadata", {})
    for key, value in metadata.items():
        print(f"  - {key}: {value}")

except Exception as e:
    print(f"✗ Extraction failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}\n")
