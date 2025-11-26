"""Check if any businesses have scraped HTML data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business

db = SessionLocal()

# Check businesses with scraped HTML
businesses = db.query(Business).filter(
    Business.scraped_html.isnot(None)
).all()

print(f"\nFound {len(businesses)} businesses with scraped HTML:\n")

for biz in businesses:
    print(f"   - {biz.name} ({biz.website_url})")
    print(f"     HTML: {len(biz.scraped_html)} chars")
    print(f"     Images: {len(biz.image_urls) if biz.image_urls else 0}")
    print(f"     Colors: {len(biz.color_palette) if biz.color_palette else 0}")
    print(f"     Components: {biz.component_count}\n")

# If none found, check all businesses
if not businesses:
    print("No businesses with scraped HTML. Checking all businesses:\n")
    all_biz = db.query(Business).filter(
        Business.website_url.isnot(None),
        Business.deleted_at.is_(None)
    ).limit(10).all()

    for biz in all_biz:
        print(f"   - {biz.name} ({biz.website_url})")

db.close()
