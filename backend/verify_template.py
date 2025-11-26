"""
Script to verify that a template has proper HTML structure.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Template

def verify_template(business_id: str):
    """Verify a template has proper structure"""
    db: Session = SessionLocal()

    try:
        # Find templates for the business
        templates = db.query(Template).filter(
            Template.business_id == business_id
        ).all()

        if not templates:
            print(f"[ERROR] No templates found for business {business_id}")
            return False

        print(f"[SUCCESS] Found {len(templates)} template(s)")
        print()

        for i, template in enumerate(templates, 1):
            print(f"{'='*60}")
            print(f"Template {i}/{len(templates)}")
            print(f"{'='*60}")
            print(f"ID: {template.id}")
            print(f"Business ID: {template.business_id}")
            print(f"Variant: {template.variant_number}")
            print(f"Generated At: {template.generated_at}")
            print(f"HTML Length: {len(template.html_content)} characters")
            print()

            # Check HTML structure
            html = template.html_content
            html_lower = html.lower()

            checks = {
                "Has DOCTYPE or <html>": ('<!doctype' in html_lower or '<html' in html_lower),
                "Has <head> tag": '<head' in html_lower,
                "Has </head> tag": '</head>' in html_lower,
                "Has <body> tag": '<body' in html_lower,
                "Has </body> tag": '</body>' in html_lower,
                "Has </html> tag": '</html>' in html_lower,
                "Length > 1000": len(html) > 1000,
                "Has CSS styles": '<style' in html_lower or 'style=' in html_lower,
            }

            print("HTML Structure Checks:")
            all_passed = True
            for check_name, passed in checks.items():
                status = "[OK]" if passed else "[FAIL]"
                print(f"  {status} {check_name}")
                if not passed:
                    all_passed = False

            print()

            if all_passed:
                print("[SUCCESS] Template structure is VALID!")
            else:
                print("[WARNING] Template has structure issues")

            # Show HTML preview
            print()
            print("HTML Preview (first 500 characters):")
            print("-" * 60)
            print(html[:500])
            print("-" * 60)
            print()

            print("HTML Preview (last 200 characters):")
            print("-" * 60)
            print(html[-200:])
            print("-" * 60)
            print()

        return True

    except Exception as e:
        print(f"[ERROR] Error verifying template: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify template HTML structure")
    parser.add_argument("business_id", help="Business ID to verify")

    args = parser.parse_args()

    print(f"Verifying templates for business: {args.business_id}")
    print()

    verify_template(args.business_id)
