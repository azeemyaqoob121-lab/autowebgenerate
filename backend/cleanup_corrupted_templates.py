"""
Cleanup script to remove corrupted templates and scraped data
Run this AFTER the scraper fix to ensure fresh generation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business, Template

def is_html_corrupted(html: str) -> bool:
    """Check if HTML contains binary corruption"""
    if not html or len(html) < 50:
        return False

    # Check for binary/control characters
    binary_chars = [
        '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08',
        '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15',
    ]

    preview = html[:500]
    for char in binary_chars:
        if char in preview:
            return True

    # Check for basic HTML structure
    html_lower = html.lower()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    has_body_tag = '<body' in html_lower or '<div' in html_lower

    if len(html) > 200 and not (has_html_tag or has_body_tag):
        return True

    return False


def cleanup_corrupted_data(db: Session):
    """Remove all corrupted templates and scraped data"""

    print("=" * 80)
    print("  CLEANUP CORRUPTED TEMPLATES & SCRAPED DATA")
    print("=" * 80)

    # Step 1: Check all templates for corruption
    print("\nStep 1: Checking templates for corruption...")
    all_templates = db.query(Template).all()
    corrupted_template_count = 0

    for template in all_templates:
        if is_html_corrupted(template.html_content):
            print(f"  [CORRUPTED] Template {template.id} for business {template.business_id}")
            db.delete(template)
            corrupted_template_count += 1

    db.commit()
    print(f"\n[OK] Deleted {corrupted_template_count} corrupted templates")

    # Step 2: Check all scraped data for corruption
    print("\nStep 2: Checking scraped data for corruption...")
    all_businesses = db.query(Business).all()
    corrupted_scraped_count = 0

    for business in all_businesses:
        needs_cleanup = False

        # Check scraped_html field
        if business.scraped_html and is_html_corrupted(business.scraped_html):
            print(f"  [CORRUPTED] Business {business.name} - scraped_html is corrupted")
            business.scraped_html = None
            needs_cleanup = True

        # Check scraped_data JSON field
        if business.scraped_data:
            raw_html = business.scraped_data.get('raw_html', '')
            if raw_html and is_html_corrupted(raw_html):
                print(f"  [CORRUPTED] Business {business.name} - scraped_data.raw_html is corrupted")
                business.scraped_data = None
                needs_cleanup = True

        if needs_cleanup:
            corrupted_scraped_count += 1

    db.commit()
    print(f"\n[OK] Cleaned {corrupted_scraped_count} businesses with corrupted scraped data")

    # Step 3: Summary
    print("\n" + "=" * 80)
    print("  CLEANUP SUMMARY")
    print("=" * 80)
    print(f"Total corrupted templates deleted: {corrupted_template_count}")
    print(f"Total businesses with scraped data cleaned: {corrupted_scraped_count}")
    print("\n[OK] Cleanup complete! You can now:")
    print("  1. Search for businesses (scraper is now fixed)")
    print("  2. Generate fresh templates (no more corruption)")
    print("  3. View clean previews in the UI")
    print("=" * 80)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        cleanup_corrupted_data(db)
    finally:
        db.close()
