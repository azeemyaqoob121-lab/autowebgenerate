"""
Generate a TRULY modern template that preserves ALL original content.
The AI must modernize the DESIGN only, not replace the content!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from openai import OpenAI
from app.config import settings
import re

def main():
    print("\n" + "="*80)
    print("GENERATING REAL MODERN TEMPLATE WITH ACTUAL BUSINESS CONTENT")
    print("="*80)

    db = SessionLocal()
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        # Get business
        business = db.query(Business).filter(
            Business.name == "C.C Electrical & Sons"
        ).first()

        if not business:
            print("ERROR: Business not found")
            return False

        print(f"\nBusiness: {business.name}")
        print(f"Scraped HTML: {len(business.scraped_html)} characters")
        print(f"Images: {len(business.image_urls)}")
        print(f"Videos: {len(business.video_urls) if business.video_urls else 0}")

        # Extract body content from scraped HTML (keep all the actual content!)
        body_match = re.search(r'<body[^>]*>(.*)</body>', business.scraped_html, re.DOTALL | re.IGNORECASE)
        body_content = body_match.group(1) if body_match else business.scraped_html

        # Create prompt that emphasizes content preservation
        prompt = f"""
You are redesigning a website with Tailwind CSS.

🚨 CRITICAL: PRESERVE ALL EXISTING CONTENT - DO NOT CHANGE TEXT, IMAGES, LINKS, OR INFORMATION!

Your ONLY job is to make it look MODERN and PROFESSIONAL by:
1. Using Tailwind CSS classes
2. Improving layout and spacing
3. Adding modern design elements (gradients, shadows, rounded corners)
4. Making it fully responsive

==================== ORIGINAL HTML CONTENT ====================
{body_content[:30000]}

==================== YOUR TASK ====================

Transform this HTML into a STUNNING modern design by:

1. **ADD TAILWIND CSS**:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

2. **CREATE MODERN NAVBAR** (sticky with logo):
```html
<nav class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-lg shadow-xl">
  <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
    <img src="http://cc-electrical.co.uk/images/logo.svg" alt="Logo" class="h-16">
    <div class="hidden md:flex space-x-8">
      <a href="#home" class="text-lg font-semibold hover:text-blue-600 transition">Home</a>
      <a href="#about" class="text-lg font-semibold hover:text-blue-600 transition">About</a>
      <a href="#services" class="text-lg font-semibold hover:text-blue-600 transition">Services</a>
      <a href="#contact" class="text-lg font-semibold hover:text-blue-600 transition">Contact</a>
    </div>
    <a href="tel:01274783598" class="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition">Call Now</a>
  </div>
</nav>
```

3. **CREATE HERO SECTION** (use actual heading from original HTML):
```html
<section class="pt-32 pb-20 bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-900 text-white">
  <div class="max-w-6xl mx-auto px-6 text-center">
    <h1 class="text-7xl md:text-9xl font-black mb-8">[ACTUAL HEADING FROM ORIGINAL]</h1>
    <p class="text-3xl md:text-4xl mb-12">[ACTUAL TAGLINE FROM ORIGINAL]</p>
    <div class="flex gap-6 justify-center">
      <a href="#contact" class="bg-white text-blue-600 px-12 py-6 rounded-2xl text-xl font-bold shadow-2xl hover:scale-110 transition">Get Free Quote</a>
      <a href="tel:01274783598" class="bg-white/10 backdrop-blur-md border-2 border-white px-12 py-6 rounded-2xl text-xl font-bold hover:bg-white/20 transition">Call: 01274 783598</a>
    </div>
  </div>
</section>
```

4. **ALL OTHER SECTIONS**: Convert each section from original HTML:
   - Keep EXACT same text content
   - Keep ALL images (use rounded-3xl shadow-2xl)
   - Keep ALL links
   - Keep ALL contact info
   - Just add Tailwind classes for modern styling

5. **SERVICES SECTION** (grid of cards):
```html
<section class="py-24 bg-gray-100">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-6xl font-bold text-center mb-16">Our Services</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
      <!-- For EACH service from original -->
      <div class="bg-white rounded-3xl shadow-2xl p-8 hover:shadow-3xl hover:-translate-y-2 transition duration-500">
        <img src="[USE ACTUAL IMAGE FROM ORIGINAL]" class="w-full h-64 object-cover rounded-2xl mb-6">
        <h3 class="text-3xl font-bold mb-4">[ACTUAL SERVICE NAME]</h3>
        <p class="text-lg text-gray-600">[ACTUAL DESCRIPTION]</p>
      </div>
    </div>
  </div>
</section>
```

6. **TESTIMONIALS** (if present - use actual testimonials):
```html
<div class="bg-white rounded-2xl shadow-xl p-8">
  <blockquote class="text-lg text-gray-700 mb-4">[ACTUAL TESTIMONIAL TEXT]</blockquote>
  <p class="font-semibold">[ACTUAL NAME/DATE]</p>
</div>
```

7. **CONTACT SECTION** (use all actual contact info):
- Phone: 01274 783598, 0113 871 5075, 07834 319787
- Email: cc.electrical.sons@gmail.com
- Addresses from original

8. **STYLING REQUIREMENTS**:
   ✓ Huge headings (text-6xl, text-7xl, text-8xl)
   ✓ Large spacing (py-24, py-32)
   ✓ Rounded corners (rounded-2xl, rounded-3xl)
   ✓ Shadows (shadow-xl, shadow-2xl)
   ✓ Hover effects on everything
   ✓ Gradient backgrounds on hero/CTA sections
   ✓ Responsive (sm:, md:, lg:, xl:)

🚨 CRITICAL RULES:
- DO NOT invent new content!
- DO NOT remove any sections from original!
- DO NOT use generic placeholder text!
- USE every image URL from the original!
- KEEP all contact information!
- PRESERVE all testimonials!
- MAINTAIN all service descriptions!

OUTPUT: Complete HTML document with <!DOCTYPE html>, proper <head>, and Tailwind CDN script tag.
"""

        print("\nCalling OpenAI API...")
        print("This will take 30-60 seconds...\n")

        # Call OpenAI with explicit instructions
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a web designer who modernizes websites with Tailwind CSS while PRESERVING ALL original content. Never invent content - only redesign the layout and styling."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,  # Lower temperature for more faithful content preservation
            max_tokens=16384
        )

        html = response.choices[0].message.content.strip()

        # Clean HTML
        if "```" in html:
            html = re.sub(r'^```(?:html)?\s*\n', '', html, flags=re.MULTILINE)
            html = re.sub(r'\n```\s*$', '', html, flags=re.MULTILINE)

        # Extract complete HTML document
        doctype_match = re.search(r'<!DOCTYPE\s+html[^>]*>', html, re.IGNORECASE)
        html_tag_match = re.search(r'<html[^>]*>', html, re.IGNORECASE)
        start_pos = doctype_match.start() if doctype_match else (html_tag_match.start() if html_tag_match else 0)
        end_match = re.search(r'</html\s*>', html, re.IGNORECASE)
        end_pos = end_match.end() if end_match else len(html)
        html = html[start_pos:end_pos].strip()

        print(f"Generated HTML: {len(html)} characters")
        has_tailwind = 'YES' if '<script src="https://cdn.tailwindcss.com"' in html else 'NO - ERROR!'
        print(f"Has Tailwind script: {has_tailwind}")
        print(f"Has gradients: {html.lower().count('gradient')}")
        print(f"Has shadows: {html.lower().count('shadow')}")
        print(f"Has rounded corners: {html.lower().count('rounded')}")
        img_count = sum(1 for img in business.image_urls if img in html) if business.image_urls else 0
        print(f"Has original images: {img_count}")

        # Delete old templates
        old_templates = db.query(Template).filter(Template.business_id == business.id).all()
        for t in old_templates:
            db.delete(t)
        db.commit()
        print(f"\nDeleted {len(old_templates)} old templates")

        # Save new template
        template = Template(
            business_id=business.id,
            variant_number=1,
            html_content=html,
            css_content="",
            js_content=None,
            improvements_made={"method": "content_preserving_modernization"},
            generated_at=__import__('datetime').datetime.utcnow()
        )

        db.add(template)
        db.commit()

        # Save to file
        filename = "template_cc_electrical_FINAL.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print("\n" + "="*80)
        print("✅ SUCCESS - TEMPLATE GENERATED!")
        print("="*80)
        print(f"\nFile saved: backend/{filename}")
        print(f"Size: {len(html):,} characters")
        print("\n🌟 OPEN THIS FILE IN YOUR BROWSER TO SEE THE RESULT!")
        print(f"\nFull path: {os.path.abspath(filename)}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    main()
