"""
Database Cleanup Script - Find and fix ALL corrupted data

This script will:
1. Scan all businesses for corrupted scraped_html/scraped_data
2. Clear corrupted data from database
3. Optionally delete corrupted templates
4. Generate report of what was cleaned
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business, Template

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_html_corrupted(html: str) -> bool:
    """
    Detect if HTML content is corrupted (contains binary garbage).

    Args:
        html: HTML string to check

    Returns:
        True if corrupted, False if clean
    """
    if not html or len(html) < 50:
        return False

    # Check for binary/control characters in the first 500 characters
    binary_chars = [
        '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08',
        '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15',
        '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d',
        '\x1e', '\x1f', '\x7f', '\x80', '\x81', '\x82', '\x83', '\x84',
        '\x85', '\x86', '\x87', '\x88', '\x89', '\x8a', '\x8b', '\x8c',
        '\x8d', '\x8e', '\x8f', '\x90', '\x91', '\x92', '\x93', '\x94',
        '\x95', '\x96', '\x97', '\x98', '\x99', '\x9a', '\x9b', '\x9c',
        '\x9d', '\x9e', '\x9f'
    ]

    # Check first 500 characters for binary data
    preview = html[:500]
    for char in binary_chars:
        if char in preview:
            return True

    # Check if HTML has basic structure tags
    html_lower = html.lower()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    has_body_tag = '<body' in html_lower

    # If HTML is longer than 200 chars but missing basic tags, it's likely corrupted
    if len(html) > 200 and not (has_html_tag or has_body_tag):
        return True

    # Check if HTML starts with binary garbage
    first_char = html.strip()[0] if html.strip() else ''
    if first_char and first_char not in ['<', '{', '[']:
        first_20 = html.strip()[:20]
        non_printable_count = sum(1 for c in first_20 if ord(c) < 32 or ord(c) > 126)
        if non_printable_count > 5:
            return True

    return False


def scan_for_corruption(db: Session, fix: bool = False) -> Dict:
    """
    Scan all businesses for corrupted data.

    Args:
        db: Database session
        fix: If True, clean corrupted data. If False, only report.

    Returns:
        Dictionary with scan results
    """
    logger.info("="*80)
    logger.info("SCANNING DATABASE FOR CORRUPTED DATA")
    logger.info("="*80)
    logger.info("")

    # Get all businesses
    all_businesses = db.query(Business).all()
    logger.info(f"Found {len(all_businesses)} businesses in database")
    logger.info("")

    corrupted_businesses = []
    clean_businesses = []

    for business in all_businesses:
        logger.info(f"Checking business: {business.name} (ID: {business.id})")

        has_corruption = False
        corruption_details = []

        # Check scraped_html field
        if business.scraped_html:
            if is_html_corrupted(business.scraped_html):
                has_corruption = True
                corruption_details.append("scraped_html")
                logger.warning(f"  ❌ CORRUPTED: scraped_html field ({len(business.scraped_html)} chars)")
            else:
                logger.info(f"  ✅ Clean: scraped_html field ({len(business.scraped_html)} chars)")

        # Check scraped_data['raw_html'] field
        if business.scraped_data and isinstance(business.scraped_data, dict):
            raw_html = business.scraped_data.get('raw_html', '')
            if raw_html:
                if is_html_corrupted(raw_html):
                    has_corruption = True
                    corruption_details.append("scraped_data.raw_html")
                    logger.warning(f"  ❌ CORRUPTED: scraped_data.raw_html ({len(raw_html)} chars)")
                else:
                    logger.info(f"  ✅ Clean: scraped_data.raw_html ({len(raw_html)} chars)")

        if has_corruption:
            corrupted_businesses.append({
                'id': str(business.id),
                'name': business.name,
                'website_url': business.website_url,
                'corruption_fields': corruption_details
            })
            logger.warning(f"  🔴 CORRUPTION FOUND in: {', '.join(corruption_details)}")

            if fix:
                logger.info(f"  🔧 FIXING: Clearing corrupted data...")
                business.scraped_data = None
                business.scraped_html = None
                business.scraped_css = None
                db.commit()
                logger.info(f"  ✅ FIXED: Cleared corrupted data")

                # Check if there are templates for this business
                templates = db.query(Template).filter(Template.business_id == business.id).all()
                if templates:
                    logger.info(f"  📝 Found {len(templates)} template(s) for this business")
                    logger.info(f"  ⚠️  Note: Templates may need regeneration")

        else:
            clean_businesses.append({
                'id': str(business.id),
                'name': business.name
            })
            logger.info(f"  ✅ All clean - no corruption detected")

        logger.info("")

    # Print summary
    logger.info("="*80)
    logger.info("SCAN SUMMARY")
    logger.info("="*80)
    logger.info(f"Total businesses scanned: {len(all_businesses)}")
    logger.info(f"Clean businesses: {len(clean_businesses)}")
    logger.info(f"Corrupted businesses: {len(corrupted_businesses)}")
    logger.info("")

    if corrupted_businesses:
        logger.info("CORRUPTED BUSINESSES:")
        for biz in corrupted_businesses:
            logger.info(f"  - {biz['name']} (ID: {biz['id']})")
            logger.info(f"    URL: {biz['website_url']}")
            logger.info(f"    Corrupted fields: {', '.join(biz['corruption_fields'])}")
            logger.info("")

        if fix:
            logger.info("✅ All corrupted data has been CLEANED")
            logger.info("⚠️  You may want to regenerate templates for these businesses")
        else:
            logger.info("⚠️  Run with --fix flag to clean corrupted data")

    else:
        logger.info("✅ No corruption found! All businesses have clean data.")

    logger.info("="*80)

    return {
        'total': len(all_businesses),
        'clean': len(clean_businesses),
        'corrupted': len(corrupted_businesses),
        'corrupted_businesses': corrupted_businesses
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scan and cleanup corrupted data in database")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix corrupted data (default is scan-only mode)"
    )

    args = parser.parse_args()

    mode = "FIX MODE" if args.fix else "SCAN-ONLY MODE"
    logger.info(f"Starting cleanup script in {mode}")
    logger.info("")

    db: Session = SessionLocal()
    try:
        results = scan_for_corruption(db, fix=args.fix)

        if not args.fix and results['corrupted'] > 0:
            logger.info("")
            logger.info("To clean corrupted data, run:")
            logger.info("  python cleanup_corrupted_data.py --fix")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
