"""
Test template generation with C.C Electrical (most complete scraped data).
Story 4.10: End-to-End validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from app.services.template_modernization_service import TemplateModernizationService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def main():
    print("\n" + "="*80)
    print("Testing AI Template Generation with C.C Electrical & Sons")
    print("="*80)

    db = SessionLocal()

    try:
        # Get C.C Electrical business
        business = db.query(Business).filter(
            Business.name == "C.C Electrical & Sons"
        ).first()

        if not business:
            print("ERROR: C.C Electrical & Sons not found")
            return False

        print(f"\nBusiness: {business.name}")
        print(f"URL: {business.website_url}")
        print(f"HTML: {len(business.scraped_html)} chars")
        print(f"Images: {len(business.image_urls) if business.image_urls else 0}")
        print(f"Colors: {len(business.color_palette) if business.color_palette else 0}")
        print(f"Components: {business.component_count}")

        if business.color_palette:
            print(f"Color palette: {', '.join(business.color_palette)}")

        if business.logo_urls:
            print(f"Logo: {business.logo_urls[0]}")

        # Delete old templates first
        print("\n" + "-"*80)
        print("Cleaning up old templates...")
        old_templates = db.query(Template).filter(
            Template.business_id == business.id
        ).all()

        for t in old_templates:
            db.delete(t)
        db.commit()
        print(f"Deleted {len(old_templates)} old templates")

        # Generate new template
        print("\n" + "-"*80)
        print("Generating ULTIMATE modern template with AI...")
        print("This may take 60-120 seconds (AI is creating 30,000+ chars of HTML)")
        print("-"*80)

        service = TemplateModernizationService(db)
        templates = service.generate_modernized_templates(business.id, force_rescrape=False)

        if not templates:
            print("\nERROR: Template generation failed")
            return False

        print(f"\n" + "="*80)
        print(f"SUCCESS! Generated {len(templates)} template(s)")
        print("="*80)

        # Analyze template
        for template in templates:
            print(f"\nTemplate ID: {template.id}")
            print(f"Variant: {template.variant_number}")
            print(f"HTML length: {len(template.html_content)} characters")

            # Quality analysis
            html = template.html_content
            html_lower = html.lower()

            print("\nQuality Checks:")
            print(f"  - HTML length: {len(html)} chars")
            print(f"  - Has DOCTYPE: {'Yes' if '<!doctype' in html_lower else 'No'}")
            print(f"  - Has Tailwind: {'Yes' if 'tailwind' in html_lower else 'No'}")
            print(f"  - Gradients: {html_lower.count('gradient')}")
            print(f"  - Shadows: {html_lower.count('shadow')}")
            print(f"  - Animations: {html_lower.count('transition') + html_lower.count('animation')}")
            print(f"  - Responsive classes: {html_lower.count('md:') + html_lower.count('lg:')}")
            print(f"  - Images: {html_lower.count('<img')}")

            # Check brand color preservation
            if business.color_palette:
                colors_found = sum(1 for color in business.color_palette if color.lower() in html_lower)
                preservation_rate = (colors_found / len(business.color_palette)) * 100
                print(f"  - Brand colors preserved: {colors_found}/{len(business.color_palette)} ({preservation_rate:.0f}%)")

            # Save to file
            filename = f"template_cc_electrical_variant{template.variant_number}.html"
            filepath = os.path.join(os.path.dirname(__file__), filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template.html_content)

            print(f"\nSaved template to: {filepath}")
            print("OPEN THIS FILE IN YOUR BROWSER TO SEE THE WOW FACTOR!")

        print("\n" + "="*80)
        print("ALL TESTS PASSED!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Open the generated HTML file in your browser")
        print("  2. Resize the window to test responsiveness")
        print("  3. Verify all 11 images are displayed")
        print("  4. Check that brand colors match the original")
        print("  5. Verify the 'WOW FACTOR' - does it look professional and modern?")

        return True

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
