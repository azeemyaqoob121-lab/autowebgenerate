"""
Test calling the generate API directly to bypass frontend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.services.template_modernization_service import TemplateModernizationService

def main():
    print("\n" + "="*80)
    print("TESTING GENERATE API DIRECTLY")
    print("="*80)

    db = SessionLocal()

    try:
        # Get a business with scraped data
        business = db.query(Business).filter(
            Business.scraped_html.isnot(None),
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            print("ERROR: No businesses with scraped data found!")
            return False

        print(f"\nBusiness: {business.name}")
        print(f"Business ID: {business.id}")
        print(f"Has scraped HTML: Yes ({len(business.scraped_html):,} chars)")

        # Call the service directly
        print("\n" + "-"*80)
        print("Calling generate_modernized_templates()...")
        print("This should take 30-60 seconds...")
        print("-"*80 + "\n")

        service = TemplateModernizationService(db)

        try:
            templates = service.generate_modernized_templates(
                business_id=str(business.id),
                force_rescrape=False
            )

            print(f"\n" + "="*80)
            print(f"RESULT: Generated {len(templates)} template(s)")
            print("="*80)

            if templates:
                for i, template in enumerate(templates, 1):
                    print(f"\nTemplate {i}:")
                    print(f"  ID: {template.id}")
                    print(f"  Business: {business.name}")
                    print(f"  Variant: {template.variant_number}")
                    print(f"  HTML length: {len(template.html_content):,} characters")
                    print(f"  First 300 chars: {template.html_content[:300]}")

                    # Save to file
                    filename = f"debug_template_{business.name.replace(' ', '_')}_v{template.variant_number}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(template.html_content)
                    print(f"  Saved to: {filename}")
            else:
                print("\nWARNING: No templates were generated!")
                print("Check the logs above for errors")

            return True

        except Exception as e:
            print(f"\n" + "="*80)
            print(f"ERROR during generation: {str(e)}")
            print("="*80)
            import traceback
            traceback.print_exc()
            return False

    finally:
        db.close()


if __name__ == "__main__":
    main()
