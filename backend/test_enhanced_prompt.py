"""
Test the enhanced premium prompt
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.business import Business
from app.services.gpt_enhanced_template_builder import build_gpt_enhanced_template

print("=" * 80)
print("TESTING ENHANCED PREMIUM PROMPT")
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
print(f"Logos: {len(business.logo_urls or [])}")
print()

print("The new enhanced prompt includes:")
print("- 10 specific premium design requirements")
print("- Detailed styling guidance for each element type")
print("- More CSS animations (fade-in-up, float, blob, gradient-shift, pulse-glow)")
print("- Gradient text class")
print("- Glass morphism class")
print("- Card hover effects")
print()

try:
    print("Generating template with ENHANCED PREMIUM PROMPT...")
    print("This should produce a much more premium-looking design!")
    print()

    template = build_gpt_enhanced_template(business)

    print()
    print("=" * 80)

    if template:
        method = template.improvements_made.get('method', 'unknown')
        chatgpt_used = template.improvements_made.get('chatgpt_generated', False)

        print(f"SUCCESS! Template generated")
        print(f"Method: {method}")
        print(f"ChatGPT Used: {'YES' if chatgpt_used else 'NO'}")
        print(f"HTML Size: {len(template.html_content):,} chars")
        print()

        # Check content
        img_count = template.html_content.lower().count('<img')
        video_count = template.html_content.lower().count('<video') + template.html_content.lower().count('<iframe')
        gradient_count = template.html_content.lower().count('gradient')
        animation_count = template.html_content.lower().count('animate-')
        hover_count = template.html_content.lower().count('hover:')

        print(f"Images in HTML: {img_count}")
        print(f"Videos/iframes in HTML: {video_count}")
        print(f"Gradients: {gradient_count}")
        print(f"Animations: {animation_count}")
        print(f"Hover effects: {hover_count}")
        print()

        # Add to database
        db.add(template)
        db.commit()
        print("Template saved to database!")
        print()
        print("KEY IMPROVEMENTS IN ENHANCED VERSION:")
        print("- More specific design guidance (10 detailed requirements)")
        print("- Better CSS animations and effects")
        print("- Gradient text and glassmorphism classes")
        print("- Professional hover and transition effects")
        print("- Should result in more premium-looking output")
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
