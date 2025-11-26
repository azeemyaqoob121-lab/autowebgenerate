"""
Script to regenerate corrupted templates with proper validation.

This script will:
1. Find the corrupted template
2. Delete it
3. Regenerate with the new validation and cleaning logic
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Business, Template
from app.services.template_generator_premium import generate_templates_for_business

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def regenerate_corrupted_template(business_id: str):
    """Regenerate a corrupted template for a business"""
    db: Session = SessionLocal()

    try:
        # Find the business
        business = db.query(Business).filter(Business.id == business_id).first()

        if not business:
            logger.error(f"Business with ID {business_id} not found")
            return False

        logger.info(f"Found business: {business.name}")

        # Find and delete existing templates
        existing_templates = db.query(Template).filter(
            Template.business_id == business_id
        ).all()

        if existing_templates:
            logger.info(f"Deleting {len(existing_templates)} existing templates...")
            for template in existing_templates:
                db.delete(template)
            db.commit()
            logger.info("✅ Deleted existing templates")
        else:
            logger.info("No existing templates found")

        # Regenerate with new validation
        logger.info("Generating new template with improved validation...")
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        if templates:
            logger.info(f"✅ Successfully generated {len(templates)} template(s)")
            for template in templates:
                logger.info(f"   Template ID: {template.id}")
                logger.info(f"   HTML length: {len(template.html_content)} characters")
                logger.info(f"   Has <body>: {'<body' in template.html_content.lower()}")
                logger.info(f"   Has </html>: {'</html>' in template.html_content.lower()}")
            return True
        else:
            logger.error("No templates were generated")
            return False

    except Exception as e:
        logger.error(f"Error regenerating template: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()


async def regenerate_all_corrupted_templates():
    """Find and regenerate all corrupted templates"""
    db: Session = SessionLocal()

    try:
        # Find all templates
        all_templates = db.query(Template).all()
        logger.info(f"Found {len(all_templates)} total templates")

        corrupted_templates = []

        # Check each template for corruption
        for template in all_templates:
            html = template.html_content.lower()

            # Check if HTML is corrupted (missing body or malformed)
            is_corrupted = (
                len(template.html_content) < 500 or  # Too short
                '<body' not in html or  # Missing body tag
                '</body>' not in html or  # Missing closing body
                '</html>' not in html  # Missing closing html
            )

            if is_corrupted:
                logger.warning(f"⚠️  Corrupted template found: {template.id} for business {template.business_id}")
                corrupted_templates.append((template, template.business_id))

        logger.info(f"Found {len(corrupted_templates)} corrupted templates")

        if not corrupted_templates:
            logger.info("✅ No corrupted templates found!")
            return True

        # Regenerate each corrupted template
        for template, business_id in corrupted_templates:
            logger.info(f"\n{'='*60}")
            logger.info(f"Regenerating template {template.id}...")
            logger.info(f"{'='*60}\n")

            success = await regenerate_corrupted_template(str(business_id))

            if success:
                logger.info(f"✅ Successfully regenerated template for business {business_id}")
            else:
                logger.error(f"❌ Failed to regenerate template for business {business_id}")

        return True

    except Exception as e:
        logger.error(f"Error finding corrupted templates: {e}", exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate corrupted templates")
    parser.add_argument("--business-id", help="Specific business ID to regenerate")
    parser.add_argument("--all", action="store_true", help="Regenerate all corrupted templates")

    args = parser.parse_args()

    if args.business_id:
        # Regenerate specific business
        logger.info(f"Regenerating template for business: {args.business_id}")
        asyncio.run(regenerate_corrupted_template(args.business_id))
    elif args.all:
        # Regenerate all corrupted templates
        logger.info("Finding and regenerating all corrupted templates...")
        asyncio.run(regenerate_all_corrupted_templates())
    else:
        # Default: regenerate all
        logger.info("Finding and regenerating all corrupted templates...")
        asyncio.run(regenerate_all_corrupted_templates())
