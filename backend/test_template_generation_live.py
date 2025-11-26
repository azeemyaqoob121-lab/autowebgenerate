"""
Test template generation LIVE to see what HTML is being produced
"""
import asyncio
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Business, Template
from app.services.template_generator_premium import generate_templates_for_business

async def test_generation():
    """Test generating a template for a real business"""

    db: Session = SessionLocal()

    try:
        # Get a business that has been scraped
        business = db.query(Business).filter(
            Business.website_url.isnot(None),
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            print("[ERROR] No businesses found in database!")
            return

        print(f"[SUCCESS] Found business: {business.name}")
        print(f"   Website: {business.website_url}")
        print(f"   ID: {business.id}")
        print()

        # Delete existing templates for this business
        existing = db.query(Template).filter(Template.business_id == business.id).all()
        if existing:
            print(f"[DELETE] Deleting {len(existing)} existing templates...")
            for t in existing:
                db.delete(t)
            db.commit()
            print("   Deleted!")

        print()
        print("[START] Starting template generation...")
        print("=" * 80)

        # Generate template
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        print("=" * 80)
        print()

        if templates and len(templates) > 0:
            template = templates[0]
            html = template.html_content

            print("[SUCCESS] TEMPLATE GENERATED!")
            print(f"   HTML Size: {len(html)} characters")
            print()

            # Analyze the HTML
            print("[ANALYSIS] HTML ANALYSIS:")
            print(f"   Has <!DOCTYPE>: {'<!doctype' in html.lower() or '<!DOCTYPE' in html}")
            print(f"   Has <html> tag: {'<html' in html.lower()}")
            print(f"   Has <head> tag: {'<head' in html.lower()}")
            print(f"   Has <body> tag: {'<body' in html.lower()}")
            print(f"   Has </html>: {'</html>' in html}")
            print()

            # Check for Tailwind CSS
            print(f"   Uses Tailwind CSS: {'cdn.tailwindcss.com' in html}")
            print(f"   Uses modern gradients: {'gradient-to-' in html or 'bg-gradient' in html}")
            print(f"   Uses Inter font: {'Inter' in html or 'font-inter' in html}")
            print()

            # Show first 1000 chars
            print("[PREVIEW] HTML PREVIEW (first 1000 chars):")
            print("-" * 80)
            print(html[:1000])
            print("-" * 80)
            print()

            # Show last 500 chars
            print("[PREVIEW] HTML PREVIEW (last 500 chars):")
            print("-" * 80)
            print(html[-500:])
            print("-" * 80)
            print()

            # Save to file for inspection
            output_file = "test_generated_template.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[SAVED] Saved full HTML to: {output_file}")
            print(f"   You can open this file in a browser to see the result!")

        else:
            print("[ERROR] No templates generated!")

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    print("TESTING TEMPLATE GENERATION")
    print("=" * 80)
    print()

    asyncio.run(test_generation())
