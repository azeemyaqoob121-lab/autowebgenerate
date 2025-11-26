"""
Test regenerate directly without authentication to see what's generated
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from app.services.template_modernization_service import TemplateModernizationService

def main():
    print("\n" + "="*80)
    print("TESTING REGENERATE DIRECTLY")
    print("="*80)

    db = SessionLocal()

    try:
        # Get C.C Electrical business
        business = db.query(Business).filter(
            Business.name == "C.C Electrical & Sons"
        ).first()

        print(f"\nBusiness: {business.name}")
        print(f"Business ID: {business.id}")
        print(f"Has scraped HTML: {'Yes' if business.scraped_html else 'No'}")
        if business.scraped_html:
            print(f"Scraped HTML length: {len(business.scraped_html):,} characters")

        # Check current templates
        current_templates = db.query(Template).filter(
            Template.business_id == business.id
        ).all()

        print(f"\nCurrent templates: {len(current_templates)}")
        for t in current_templates:
            print(f"  - Template {t.id}: {len(t.html_content):,} chars")

        # Regenerate
        print("\n" + "-"*80)
        print("Calling regenerate_templates()...")
        print("-"*80)

        service = TemplateModernizationService(db)
        templates = service.regenerate_templates(
            business_id=str(business.id),
            force_rescrape=False
        )

        print(f"\nRegeneration complete!")
        print(f"Templates returned: {len(templates)}")

        for i, template in enumerate(templates, 1):
            print(f"\nTemplate {i}:")
            has_doctype = 'Yes' if '<!DOCTYPE' in template.html_content else 'No'
            has_tailwind = 'Yes' if '<script src="https://cdn.tailwindcss.com"' in template.html_content else 'No'
            print(f"  ID: {template.id}")
            print(f"  Variant: {template.variant_number}")
            print(f"  HTML length: {len(template.html_content):,} characters")
            print(f"  Has DOCTYPE: {has_doctype}")
            print(f"  Has Tailwind: {has_tailwind}")
            print(f"  Improvements: {template.improvements_made}")

            # Save preview
            filename = f"template_regenerate_test_variant{template.variant_number}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(template.html_content)
            print(f"  Saved to: {filename}")

        # Check database
        print("\n" + "-"*80)
        print("Checking database...")
        print("-"*80)

        db_templates = db.query(Template).filter(
            Template.business_id == business.id
        ).all()

        print(f"Templates in database: {len(db_templates)}")
        for t in db_templates:
            print(f"  - {t.id}: {len(t.html_content):,} chars, variant {t.variant_number}")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    main()
