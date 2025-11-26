"""
Force regenerate templates using Gemini with ENHANCED prompts
Run this to regenerate a business's templates with perfect quality
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business, Template
from app.services.template_generator_premium import generate_templates_for_business
from app.config import settings
import uuid

async def force_regenerate_business(business_id: str, db: Session):
    """Force regenerate templates for a business using Gemini"""

    print("=" * 80)
    print("  FORCE REGENERATE WITH GEMINI - MAXIMUM QUALITY")
    print("=" * 80)

    # Get business
    business = db.query(Business).filter(Business.id == uuid.UUID(business_id)).first()

    if not business:
        print(f"[ERROR] Business not found: {business_id}")
        return

    print(f"\nBusiness: {business.name}")
    print(f"URL: {business.website_url}")
    print(f"Category: {business.category}")

    # Check Gemini configuration
    print(f"\n[CONFIG] Checking Gemini configuration...")
    print(f"  USE_GEMINI_GENERATION: {settings.USE_GEMINI_GENERATION}")
    print(f"  GEMINI_MODEL: {settings.GEMINI_MODEL}")
    print(f"  GEMINI_API_KEY: {'Configured' if settings.GEMINI_API_KEY else 'NOT SET'}")

    if not settings.USE_GEMINI_GENERATION:
        print(f"\n[WARNING] Gemini is DISABLED! Setting it to True for this generation...")
        settings.USE_GEMINI_GENERATION = True

    if not settings.GEMINI_API_KEY:
        print(f"\n[ERROR] Gemini API key is not configured!")
        return

    # Delete old templates
    old_templates = db.query(Template).filter(Template.business_id == business.id).all()
    print(f"\n[CLEANUP] Deleting {len(old_templates)} old templates...")
    for template in old_templates:
        db.delete(template)
    db.commit()
    print(f"[OK] Old templates deleted")

    # Generate new templates with Gemini
    print(f"\n[GEMINI] Starting MAXIMUM QUALITY generation...")
    print(f"[GEMINI] This will generate 3 variants and select the best one")
    print(f"[GEMINI] Please wait 30-60 seconds...\n")

    try:
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True  # Uses Gemini if USE_GEMINI_GENERATION=True
        )

        if templates:
            print(f"\n[SUCCESS] Generated {len(templates)} template(s)!")
            for i, template in enumerate(templates, 1):
                print(f"\nTemplate #{i}:")
                print(f"  ID: {template.id}")
                print(f"  Variant: {template.variant_number}")
                print(f"  HTML size: {len(template.html_content)} bytes")

                # Check HTML quality
                html = template.html_content
                has_doctype = '<!DOCTYPE' in html or '<!doctype' in html
                has_html = '<html' in html
                has_body = '<body' in html
                has_tailwind = 'tailwindcss' in html or 'tailwind' in html
                has_gradients = 'gradient' in html

                print(f"  Quality checks:")
                print(f"    - Has DOCTYPE: {has_doctype}")
                print(f"    - Has <html>: {has_html}")
                print(f"    - Has <body>: {has_body}")
                print(f"    - Uses Tailwind CSS: {has_tailwind}")
                print(f"    - Has gradients: {has_gradients}")

                if all([has_doctype, has_html, has_body]):
                    print(f"  [OK] Template structure looks good!")
                else:
                    print(f"  [WARNING] Template may have structural issues!")
        else:
            print(f"\n[ERROR] No templates generated!")

    except Exception as e:
        print(f"\n[ERROR] Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("  REGENERATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Refresh your frontend browser")
    print("2. Click on the business to view the new template")
    print("3. The template should now be modern and professional!")
    print("=" * 80)


async def main():
    # Get business ID from user
    business_id = input("\nEnter the Business ID to regenerate (or press Enter for latest): ").strip()

    db = SessionLocal()

    try:
        if not business_id:
            # Get the most recently created business
            latest = db.query(Business).order_by(Business.created_at.desc()).first()
            if latest:
                print(f"\nUsing latest business: {latest.name} ({latest.id})")
                business_id = str(latest.id)
            else:
                print("[ERROR] No businesses found in database!")
                return

        await force_regenerate_business(business_id, db)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
