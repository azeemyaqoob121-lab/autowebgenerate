"""
Test WOW Factor Template Generation
Tests the new ULTIMATE modern design template generation with animations and professional styling
"""
import sys
sys.path.insert(0, 'C:\\Users\\rabia\\Documents\\project AutoWeb Outreach AI\\AutoWeb_Outreach_AI\\backend')

from app.database import SessionLocal
from app.services.template_modernization_service import TemplateModernizationService
from app.models.business import Business
from app.models.template import Template
import json

# Business ID for C.C Electrical & Sons (has 34 components, good data)
BUSINESS_ID = "8f92f1dc-a9e7-4685-95f1-aa0c8a908d62"

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("TESTING WOW FACTOR TEMPLATE GENERATION")
        print("=" * 80)

        # Load business
        business = db.query(Business).filter(Business.id == BUSINESS_ID).first()

        if not business:
            print(f"[ERROR] Business {BUSINESS_ID} not found - check database!")
            return

        print(f"\nBusiness: {business.name}")
        print(f"URL: {business.website_url}")
        print(f"Component Count: {business.component_count}")
        print(f"Images: {len(business.image_urls or [])}")
        print(f"Logos: {len(business.logo_urls or [])}")
        print(f"Videos: {len(business.video_urls or [])}")
        print(f"Colors: {len(business.color_palette or [])}")

        print("\n" + "=" * 80)
        print("STEP 1: Deleting old templates (if any)...")
        print("=" * 80)

        # Delete old templates
        old_templates = db.query(Template).filter(Template.business_id == BUSINESS_ID).all()
        for template in old_templates:
            db.delete(template)
        db.commit()
        print(f"✅ Deleted {len(old_templates)} old templates")

        print("\n" + "=" * 80)
        print("STEP 2: Generating NEW ULTIMATE WOW FACTOR template...")
        print("=" * 80)
        print("\n⏳ This may take 2-5 minutes with GPT-4 Turbo...")
        print("   - Building detailed prompt with all scraped data")
        print("   - Sending to OpenAI GPT-4 Turbo with max tokens (16384)")
        print("   - Waiting for STUNNING, PROFESSIONAL, MODERN HTML generation")

        # Generate new template with WOW factor
        service = TemplateModernizationService(db)
        templates = service.generate_modernized_templates(str(business.id), force_rescrape=False)

        if not templates:
            print("\n[ERROR] No templates generated!")
            return

        print("\n" + "=" * 80)
        print("✅ SUCCESS! TEMPLATE GENERATED")
        print("=" * 80)

        # Analyze generated template
        template = templates[0]
        print(f"\nTemplate ID: {template.id}")
        print(f"Variant Number: {template.variant_number}")
        print(f"HTML Length: {len(template.html_content):,} characters")
        print(f"Generated At: {template.generated_at}")

        # Check improvements made
        improvements = template.improvements_made or {}
        print(f"\nVariant Name: {improvements.get('variant_name', 'Unknown')}")
        print(f"CSS Framework: {improvements.get('css_framework', 'Unknown')}")
        print(f"Generation Method: {improvements.get('generation_method', 'Unknown')}")
        print(f"Component Count: {improvements.get('component_count', 0)}")
        print(f"Colors Preserved: {improvements.get('colors_preserved', 0)}")

        # Validate HTML quality
        html = template.html_content
        print("\n" + "=" * 80)
        print("QUALITY CHECK")
        print("=" * 80)

        checks = {
            "Has DOCTYPE": "<!doctype html" in html.lower(),
            "Has <html> tag": "<html" in html.lower() and "</html>" in html.lower(),
            "Has <head> tag": "<head" in html.lower() and "</head>" in html.lower(),
            "Has <body> tag": "<body" in html.lower() and "</body>" in html.lower(),
            "Has Tailwind CDN": "tailwindcss.com" in html.lower(),
            "Has animations (@keyframes)": "@keyframes" in html.lower(),
            "Has fadeInUp animation": "fadeinup" in html.lower(),
            "Has hover effects": "hover:" in html.lower(),
            "Has transitions": "transition" in html.lower(),
            "Has shadows": "shadow" in html.lower(),
            "Has gradients": "gradient" in html.lower(),
            "Has rounded corners": "rounded" in html.lower(),
            "Sufficient length (>10k chars)": len(html) > 10000,
            "No explanatory text": not any(phrase in html.lower() for phrase in [
                "this design implementation",
                "this template modernizes",
                "improvements include"
            ])
        }

        passed_checks = 0
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if result:
                passed_checks += 1

        print(f"\nQuality Score: {passed_checks}/{len(checks)} checks passed ({passed_checks * 100 // len(checks)}%)")

        # Count specific components in HTML
        print("\n" + "=" * 80)
        print("COMPONENT VERIFICATION")
        print("=" * 80)

        component_keywords = {
            "Header/Navigation": any(tag in html.lower() for tag in ["<header", "<nav"]),
            "Hero Section": any(word in html.lower() for word in ["hero", "jumbotron", "banner"]),
            "Services/Features": any(word in html.lower() for word in ["service", "feature"]),
            "About Section": "about" in html.lower(),
            "Contact Section": "contact" in html.lower(),
            "Footer": "<footer" in html.lower(),
            "Images": "<img" in html.lower(),
            "Videos": any(tag in html.lower() for tag in ["<video", "youtube", "vimeo"]),
        }

        for component, found in component_keywords.items():
            status = "✅" if found else "❌"
            print(f"{status} {component}")

        print("\n" + "=" * 80)

        if passed_checks >= 12:  # 12/14 = 86%+
            print("🎉 EXCELLENT! Template has WOW factor styling!")
            print("   Ready to show to business owners for impressive demos!")
        elif passed_checks >= 10:
            print("✅ GOOD! Template is professional and modern")
            print("   May need minor enhancements for maximum WOW factor")
        else:
            print("⚠️  WARNING! Template may not meet WOW factor standards")
            print("   Consider reviewing prompt and regenerating")

        print("=" * 80)

        # Save first 2000 chars of HTML for review
        print("\n📄 First 2000 characters of generated HTML:")
        print("-" * 80)
        print(html[:2000])
        print("-" * 80)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    main()
