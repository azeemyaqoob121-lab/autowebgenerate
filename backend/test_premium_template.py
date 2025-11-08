"""Test PREMIUM template generation"""
import asyncio
import sys
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Business
from app.services.template_generator_premium import generate_templates_for_business

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_premium_generation():
    """Test PREMIUM template generation"""

    engine = create_engine(settings.DATABASE_URL)
    db = Session(bind=engine)

    try:
        # Get first business
        business = db.query(Business).filter(
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            print("\n❌ ERROR: No businesses found!")
            return

        print(f"\n{'='*60}")
        print(f"TESTING PREMIUM TEMPLATE GENERATION")
        print(f"{'='*60}")
        print(f"Business: {business.name}")
        print(f"Category: {business.category}")
        print(f"Website: {business.website_url}")
        print(f"{'='*60}\n")

        print("🚀 Generating PREMIUM template...")
        print("This uses:")
        print("  ✓ PremiumTemplateBuilder (guaranteed quality)")
        print("  ✓ Business intelligence & classification")
        print("  ✓ Content extraction from old website")
        print("  ✓ Gap analysis")
        print("  ✓ Premium media sourcing (Unsplash/Pexels)")
        print("  ✓ GPT-4 content enhancement")
        print("  ✓ Validation against standards\n")
        print(f"{'='*60}\n")

        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS!")
        print(f"{'='*60}\n")

        for i, template in enumerate(templates, 1):
            html_length = len(template.html_content) if template.html_content else 0

            print(f"Template {i}:")
            print(f"  - ID: {template.id}")
            print(f"  - Variant: {template.variant_number}")
            print(f"  - HTML length: {html_length:,} characters")
            print(f"  - Improvements: {len(template.improvements_made) if template.improvements_made else 0}")

            if html_length < 10000:
                print(f"  ⚠️  WARNING: HTML seems short (< 10,000 characters)")
            else:
                print(f"  ✅ PREMIUM HTML length looks excellent!")

            # Show first 500 chars
            if template.html_content:
                preview = template.html_content[:500].replace('\n', ' ')
                print(f"\n  Preview:\n  {preview}...\n")

            # Check for key features
            html = template.html_content or ""
            features = {
                "Responsive navbar": "navbar" in html.lower(),
                "Mobile menu": "hamburger" in html.lower() or "mobile-menu" in html.lower(),
                "Glassmorphism": "backdrop-filter" in html,
                "Media queries": "@media" in html,
                "Grid layout": "grid-template-columns" in html,
                "Google Fonts": "fonts.googleapis.com" in html,
                "Font Awesome": "fontawesome" in html.lower(),
                "Schema.org": "schema.org" in html,
                "Animations": "animation" in html.lower() or "transition" in html,
                "Contact form": "<form" in html.lower(),
            }

            print("  Feature Checklist:")
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"    {status} {feature}")

    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}")

    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PREMIUM TEMPLATE GENERATION TEST")
    print("="*60)
    asyncio.run(test_premium_generation())
