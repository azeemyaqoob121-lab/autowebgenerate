"""Test template regeneration to find the error"""
import sys
import codecs
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Business
from app.services.template_generator_premium import generate_templates_for_business

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Create database connection
engine = create_engine(settings.DATABASE_URL)
db = Session(bind=engine)

async def test_regenerate():
    try:
        # Get the business
        business_id = "ed21e169-7aa3-4461-8d89-9faf827402ff"

        print(f"Testing regeneration for business: {business_id}")

        business = db.query(Business).filter(
            Business.id == business_id,
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            print(f"❌ Business not found: {business_id}")
            return

        print(f"✓ Business found: {business.name}")
        print(f"  Website: {business.website_url}")

        # Try to generate templates
        print("\nGenerating templates...")
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1
        )

        print(f"\n✅ SUCCESS! Generated {len(templates)} template(s)")

    except Exception as e:
        print(f"\n❌ ERROR during generation:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_regenerate())
