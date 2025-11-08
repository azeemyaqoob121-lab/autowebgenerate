"""Test template generation to debug empty website issue"""
import asyncio
import sys
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Business
from app.services.template_generator import generate_templates_for_business

# Fix Windows encoding issue
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_template_generation():
    """Test generating templates for a business"""

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    db = Session(bind=engine)

    try:
        # Get the first business from database
        business = db.query(Business).filter(
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            logger.error("No businesses found in database!")
            print("\n❌ ERROR: No businesses found!")
            print("Please create a business first before testing template generation.")
            return

        logger.info(f"Found business: {business.name} (ID: {business.id})")
        print(f"\n✓ Found business: {business.name}")
        print(f"  - Category: {business.category}")
        print(f"  - Location: {business.location}")
        print(f"  - Website: {business.website_url}")
        print(f"  - Description: {business.description[:100] if business.description else 'None'}...")

        # Check OpenAI API key
        if not settings.OPENAI_API_KEY:
            logger.error("OpenAI API key not configured!")
            print("\n❌ ERROR: OpenAI API key not configured!")
            print("Please set OPENAI_API_KEY in your .env file.")
            return

        print(f"\n✓ OpenAI API key configured: {settings.OPENAI_API_KEY[:10]}...")

        # Try to generate templates
        print("\n🔄 Generating templates (this may take 30-60 seconds)...")
        print("=" * 60)

        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1  # Generate just 1 for testing
        )

        print("=" * 60)
        print(f"\n✓ Successfully generated {len(templates)} template(s)!")

        for i, template in enumerate(templates, 1):
            html_length = len(template.html_content) if template.html_content else 0
            css_length = len(template.css_content) if template.css_content else 0

            print(f"\nTemplate {i}:")
            print(f"  - ID: {template.id}")
            print(f"  - Variant: {template.variant_number}")
            print(f"  - HTML length: {html_length:,} characters")
            print(f"  - CSS length: {css_length:,} characters")
            print(f"  - Improvements: {len(template.improvements_made) if template.improvements_made else 0}")

            # Check if HTML is empty or minimal
            if html_length < 1000:
                print(f"  ⚠️  WARNING: HTML seems too short! (< 1000 characters)")
                print(f"  First 500 characters:")
                print(f"  {template.html_content[:500]}")
            else:
                print(f"  ✓ HTML looks good!")
                # Show preview of HTML
                html_preview = template.html_content[:200].replace('\n', ' ')
                print(f"  Preview: {html_preview}...")

    except Exception as e:
        logger.exception(f"Error during template generation: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}")
        print(f"\nFull error details above.")

    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Template Generation Debug Test")
    print("=" * 60)
    asyncio.run(test_template_generation())
