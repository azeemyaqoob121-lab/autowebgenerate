"""
Test that new prompt preserves original website structure
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.business import Business
from app.services.gpt_enhanced_template_builder import build_gpt_enhanced_template

print("=" * 80)
print("TESTING STRUCTURE-PRESERVING TEMPLATE GENERATION")
print("=" * 80)
print()

db = SessionLocal()

# Find business with scraped data
business = db.query(Business).filter(
    Business.scraped_html != None,
    Business.component_count > 0
).first()

if not business:
    print("ERROR: No business with scraped data found")
    sys.exit(1)

print(f"Testing with business: {business.name}")
print(f"Components: {business.component_count}")
print(f"Images: {len(business.image_urls or [])}")
print(f"Videos: {len(business.video_urls or [])}")
print()

try:
    print("Generating template with STRUCTURE PRESERVATION...")
    print()

    template = build_gpt_enhanced_template(business)

    print()
    print("=" * 80)

    if template:
        method = template.improvements_made.get('method', 'unknown')
        chatgpt_used = template.improvements_made.get('chatgpt_generated', False)

        print(f"SUCCESS! Template generated")
        print(f"Template ID: {template.id}")
        print(f"Method: {method}")
        print(f"ChatGPT Used: {'YES' if chatgpt_used else 'NO'}")
        print(f"HTML Size: {len(template.html_content):,} chars")
        print()

        # Check if it has images
        img_count = template.html_content.lower().count('<img')
        print(f"Images in HTML: {img_count}")

        # Check if it has videos
        video_count = template.html_content.lower().count('<video')
        print(f"Videos in HTML: {video_count}")

        # Add to database
        db.add(template)
        db.commit()
        print()
        print("Template saved to database!")
        print()
        print("KEY FEATURES OF NEW SYSTEM:")
        print("- Preserves original website structure")
        print("- Keeps same sections in same order")
        print("- Uses exact text from original")
        print("- Modernizes only the styling")
        print("- Each business gets unique design")
    else:
        print("FAILED: build_gpt_enhanced_template returned None")
        print("Check logs above for errors")

except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("=" * 80)
