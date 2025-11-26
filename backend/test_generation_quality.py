"""
Test template generation quality - Check if ChatGPT generation is working.
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
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_generation():
    """Test template generation for a low-score business"""
    db: Session = SessionLocal()

    try:
        logger.info("="*80)
        logger.info("TESTING TEMPLATE GENERATION QUALITY")
        logger.info("="*80)
        logger.info("")

        # Check configuration
        logger.info(f"USE_CHATGPT_HTML_GENERATION: {settings.USE_CHATGPT_HTML_GENERATION}")
        logger.info(f"OPENAI_API_KEY configured: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
        logger.info("")

        # Find a low-score business
        business = db.query(Business).filter(
            Business.score < 70
        ).order_by(Business.created_at.desc()).first()

        if not business:
            logger.error("No low-score business found")
            return

        logger.info(f"Testing with business: {business.name}")
        logger.info(f"  Score: {business.score}")
        logger.info(f"  URL: {business.website_url}")
        logger.info("")

        # Delete existing templates first
        existing_templates = db.query(Template).filter(
            Template.business_id == business.id
        ).all()

        if existing_templates:
            logger.info(f"Deleting {len(existing_templates)} existing template(s)...")
            for template in existing_templates:
                db.delete(template)
            db.commit()
            logger.info("")

        # Try to generate fresh template
        logger.info("Generating fresh template...")
        logger.info("="*80)

        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        logger.info("")
        logger.info("="*80)
        logger.info("GENERATION COMPLETE")
        logger.info("="*80)

        if templates:
            template = templates[0]
            logger.info(f"✅ Generated template ID: {template.id}")
            logger.info(f"   HTML length: {len(template.html_content)} characters")
            logger.info("")

            # Analyze what was generated
            html_lower = template.html_content.lower()

            # Check for modern design indicators
            modern_indicators = {
                'Has gradient': 'gradient' in html_lower,
                'Has glassmorphism/backdrop-filter': 'backdrop-filter' in html_lower or 'glassmorphism' in html_lower,
                'Has animations': 'animation' in html_lower or '@keyframes' in html_lower or 'transform' in html_lower,
                'Has modern CSS grid': 'grid' in html_lower or 'display: grid' in html_lower,
                'Has flexbox': 'flex' in html_lower or 'display: flex' in html_lower,
                'Has CSS variables': '--' in template.html_content[:5000],  # Check first 5KB
                'Has modern meta tags': 'viewport' in html_lower and 'charset' in html_lower,
                'Has semantic HTML5': '<header' in html_lower and '<footer' in html_lower and '<section' in html_lower
            }

            logger.info("QUALITY ANALYSIS:")
            modern_count = 0
            for indicator, present in modern_indicators.items():
                status = "✅" if present else "❌"
                logger.info(f"  {status} {indicator}: {present}")
                if present:
                    modern_count += 1

            logger.info("")
            logger.info(f"Modern design score: {modern_count}/{len(modern_indicators)} ({modern_count/len(modern_indicators)*100:.0f}%)")
            logger.info("")

            # Check if it's cloned or generated
            preview = template.html_content[:1000]
            logger.info("HTML Preview (first 1000 chars):")
            logger.info(preview)
            logger.info("")

            # Look for signs of cloning vs fresh generation
            if business.website_url in template.html_content:
                logger.warning("⚠️  WARNING: Original website URL found in HTML - likely CLONED")
            else:
                logger.info("✅ Original website URL NOT found - likely FRESH GENERATION")

            # Check for WordPress/common CMS markers (sign of cloning)
            cms_markers = ['wp-content', 'wordpress', 'wix.com', 'squarespace', 'weebly']
            found_markers = [marker for marker in cms_markers if marker in html_lower]
            if found_markers:
                logger.warning(f"⚠️  WARNING: CMS markers found: {found_markers} - likely CLONED")
            else:
                logger.info("✅ No CMS markers found - likely FRESH GENERATION")

            logger.info("")
            logger.info("="*80)
            logger.info("VERDICT:")
            if modern_count >= 6 and not found_markers and business.website_url not in template.html_content:
                logger.info("✅ ✅ ✅ HIGH QUALITY MODERN GENERATION - ChatGPT working correctly!")
            elif modern_count >= 4:
                logger.info("⚠️  MODERATE QUALITY - Some modern features but may need improvement")
            else:
                logger.info("❌ ❌ ❌ LOW QUALITY - Likely just CLONED original website")
                logger.info("      ChatGPT generation may have FAILED or is not being used")
            logger.info("="*80)
        else:
            logger.error("❌ No templates were generated")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_generation())
