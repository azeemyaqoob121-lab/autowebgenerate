"""
Regenerate C.C Electrical template with ULTRA MODERN design.
Fix all issues and create a truly stunning template.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from openai import OpenAI
from app.config import settings

# Ultra modern prompt
ULTRA_MODERN_PROMPT = """
You are an ELITE web designer from a TOP agency (think Apple, Stripe, Airbnb level).

CREATE A STUNNING, BREATHTAKING WEBSITE for C.C Electrical & Sons.

🎯 CRITICAL REQUIREMENTS:

1. **TAILWIND CSS - USE SCRIPT TAG**:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

2. **MODERN HERO SECTION**:
```html
<section class="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-900 overflow-hidden">
  <div class="absolute inset-0 opacity-20">
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-white rounded-full blur-3xl"></div>
    <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-300 rounded-full blur-3xl"></div>
  </div>
  <div class="relative z-10 text-center text-white px-6 max-w-6xl mx-auto">
    <h1 class="text-7xl md:text-8xl lg:text-9xl font-black mb-8 leading-tight animate-fade-in">
      Electrician in Leeds, Bradford
    </h1>
    <p class="text-3xl md:text-4xl mb-12 font-light">
      Professional Electrical Services Across Yorkshire
    </p>
    <div class="flex flex-col sm:flex-row gap-6 justify-center">
      <a href="#contact" class="bg-white text-blue-600 px-12 py-6 rounded-2xl text-xl font-bold shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-300">
        Get Free Quote
      </a>
      <a href="tel:01274783598" class="bg-white/10 backdrop-blur-md border-2 border-white text-white px-12 py-6 rounded-2xl text-xl font-bold hover:bg-white/20 transition-all duration-300">
        Call Now: 01274 783598
      </a>
    </div>
  </div>
</section>
```

3. **MODERN SERVICE CARDS**:
```html
<div class="bg-white rounded-3xl shadow-2xl p-8 hover:shadow-3xl hover:-translate-y-2 transition-all duration-500 border border-gray-100">
  <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mb-6">
    <span class="text-4xl">⚡</span>
  </div>
  <h3 class="text-3xl font-bold mb-4">Service Name</h3>
  <p class="text-lg text-gray-600">Description here</p>
</div>
```

4. **PRESERVE ALL DATA**:
- Logo: http://cc-electrical.co.uk/images/logo.svg
- Images: Use these actual image URLs:
  * http://cc-electrical.co.uk/images/12.webp
  * http://cc-electrical.co.uk/images/33403823_c325cbd499.webp
  * http://cc-electrical.co.uk/images/33404573_60521b0bb3.webp
  * http://cc-electrical.co.uk/images/adding-wires-to-office.webp
  * http://cc-electrical.co.uk/images/33404347_02e1cf6e5e.webp
- Phone: 01274 783598, 0113 871 5075, 07834 319787
- Email: cc.electrical.sons@gmail.com

5. **DESIGN REQUIREMENTS**:
✓ Large, bold typography everywhere
✓ Gradient backgrounds (hero, sections, buttons)
✓ Glass-morphism effects
✓ Huge spacing (py-24, py-32)
✓ Rounded corners everywhere (rounded-2xl, rounded-3xl)
✓ Shadows on everything (shadow-xl, shadow-2xl)
✓ Smooth hover animations
✓ Responsive mobile-first design

OUTPUT ONLY THE COMPLETE HTML DOCUMENT - NO EXPLANATIONS OR MARKDOWN!
"""

def main():
    print("\n" + "="*80)
    print("REGENERATING C.C ELECTRICAL TEMPLATE WITH ULTRA MODERN DESIGN")
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
        print("Generating ULTRA MODERN template...")

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite web designer. Create STUNNING, modern websites with Tailwind CSS. Output ONLY HTML - no explanations."
                },
                {
                    "role": "user",
                    "content": ULTRA_MODERN_PROMPT
                }
            ],
            temperature=0.8,
            max_tokens=16384
        )

        html = response.choices[0].message.content.strip()

        # Clean HTML (remove markdown if present)
        import re
        if "```" in html:
            html = re.sub(r'^```(?:html)?\s*\n', '', html, flags=re.MULTILINE)
            html = re.sub(r'\n```\s*$', '', html, flags=re.MULTILINE)

        # Extract HTML document
        doctype_match = re.search(r'<!DOCTYPE\s+html[^>]*>', html, re.IGNORECASE)
        html_tag_match = re.search(r'<html[^>]*>', html, re.IGNORECASE)

        start_pos = doctype_match.start() if doctype_match else (html_tag_match.start() if html_tag_match else 0)
        end_match = re.search(r'</html\s*>', html, re.IGNORECASE)
        end_pos = end_match.end() if end_match else len(html)

        html = html[start_pos:end_pos].strip()

        print(f"\nGenerated HTML: {len(html)} characters")
        has_script = 'Yes' if '<script src="https://cdn.tailwindcss.com"' in html else 'NO - WRONG!'
        print(f"Has <script>: {has_script}")
        print(f"Has gradients: {html.lower().count('gradient')}")
        print(f"Has shadows: {html.lower().count('shadow')}")

        # Delete old templates
        old_templates = db.query(Template).filter(Template.business_id == business.id).all()
        for t in old_templates:
            db.delete(t)
        db.commit()

        # Save new template
        template = Template(
            business_id=business.id,
            variant_number=1,
            html_content=html,
            css_content="",
            js_content=None,
            improvements_made={"method": "ultra_modern_regeneration"},
            generated_at=__import__('datetime').datetime.utcnow()
        )

        db.add(template)
        db.commit()

        # Save to file
        with open("template_cc_electrical_ULTRA_MODERN.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"\nSaved to: backend/template_cc_electrical_ULTRA_MODERN.html")
        print("\nOPEN THIS FILE IN YOUR BROWSER NOW!")

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
