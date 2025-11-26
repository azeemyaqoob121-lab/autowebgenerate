"""
Clear corrupted scraped data and regenerate template from scratch.
"""

import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business, Template
from app.services.template_generator_premium import generate_templates_for_business

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def clear_and_regenerate(business_id: str):
    """Clear corrupted data and regenerate template from scratch"""
    db: Session = SessionLocal()

    try:
        # Find the business
        business = db.query(Business).filter(Business.id == business_id).first()

        if not business:
            logger.error(f"Business with ID {business_id} not found")
            return False

        logger.info(f"Found business: {business.name}")
        logger.info(f"Website URL: {business.website_url}")

        # Step 1: Clear corrupted scraped data
        logger.info("Step 1: Clearing corrupted scraped data...")
        business.scraped_data = None
        business.scraped_html = None
        business.scraped_css = None
        db.commit()
        logger.info("✅ Cleared scraped data")

        # Step 2: Delete existing templates
        logger.info("Step 2: Deleting existing templates...")
        existing_templates = db.query(Template).filter(
            Template.business_id == business_id
        ).all()

        if existing_templates:
            for template in existing_templates:
                db.delete(template)
            db.commit()
            logger.info(f"✅ Deleted {len(existing_templates)} existing templates")
        else:
            logger.info("No existing templates to delete")

        # Step 3: Generate fresh template (will scrape with fixed code)
        logger.info("Step 3: Generating fresh template with fixed scraper...")
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        if templates:
            logger.info(f"✅ Successfully generated {len(templates)} template(s)!")
            for template in templates:
                logger.info(f"   Template ID: {template.id}")
                logger.info(f"   HTML length: {len(template.html_content)} characters")

                html_lower = template.html_content.lower()
                logger.info(f"   Has <html>: {'<html' in html_lower}")
                logger.info(f"   Has <head>: {'<head' in html_lower}")
                logger.info(f"   Has <body>: {'<body' in html_lower}")
                logger.info(f"   Has </body>: {'</body>' in html_lower}")
                logger.info(f"   Has </html>: {'</html>' in html_lower}")

                # Check for corruption
                has_corruption = any(char in template.html_content[:500] for char in ['\x01', '\x02', '\x03', '\x10', '\x9f'])
                if has_corruption:
                    logger.error("   ❌ STILL HAS CORRUPTION IN HTML!")
                else:
                    logger.info("   ✅ HTML looks clean (no binary characters)")

                # Show preview
                preview = template.html_content[:200]
                logger.info(f"   HTML preview: {repr(preview)}")

            return True
        else:
            logger.error("❌ No templates were generated")
            return False

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clear and regenerate template")
    parser.add_argument("business_id", help="Business ID")

    args = parser.parse_args()

    logger.info(f"Clearing and regenerating for business: {args.business_id}")
    logger.info("")

    asyncio.run(clear_and_regenerate(args.business_id))
