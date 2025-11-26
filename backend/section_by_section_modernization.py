"""
Section-by-Section Modernization
Extract sections from original HTML, modernize each separately, then combine.
This ensures ALL content is preserved while achieving modern design.
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
from bs4 import BeautifulSoup

def extract_sections(html: str):
    """Extract key sections from the HTML."""
    soup = BeautifulSoup(html, 'html.parser')

    sections = {}

    # Extract header/nav
    header = soup.find(['header', 'nav'])
    if header:
        sections['header'] = str(header)

    # Extract main sections
    main_sections = soup.find_all(['section', 'div'], class_=re.compile(r'(hero|banner|intro|welcome)', re.I)) or \
                   soup.find_all(['section', 'div'], id=re.compile(r'(hero|banner|intro|home)', re.I))

    if main_sections:
        sections['hero'] = str(main_sections[0])

    # Extract services section
    services = soup.find_all(['section', 'div'], class_=re.compile(r'service', re.I)) or \
              soup.find_all(['section', 'div'], id=re.compile(r'service', re.I))

    if services:
        sections['services'] = str(services[0])

    # Extract about section
    about = soup.find_all(['section', 'div'], class_=re.compile(r'about', re.I)) or \
           soup.find_all(['section', 'div'], id=re.compile(r'about', re.I))

    if about:
        sections['about'] = str(about[0])

    # Extract testimonials
    testimonials = soup.find_all(['section', 'div'], class_=re.compile(r'(testimonial|review)', re.I)) or \
                  soup.find_all(['section', 'div'], id=re.compile(r'(testimonial|review)', re.I))

    if testimonials:
        sections['testimonials'] = str(testimonials[0])

    # Extract contact section
    contact = soup.find_all(['section', 'div'], class_=re.compile(r'contact', re.I)) or \
             soup.find_all(['section', 'div'], id=re.compile(r'contact', re.I))

    if contact:
        sections['contact'] = str(contact[0])

    # Extract footer
    footer = soup.find('footer')
    if footer:
        sections['footer'] = str(footer)

    # Get all remaining content if sections are missing
    if not sections:
        # Fall back to body content
        body = soup.find('body')
        if body:
            sections['full_body'] = str(body)

    return sections


def modernize_section(client: OpenAI, section_name: str, section_html: str, business_name: str) -> str:
    """Modernize a single section using AI."""

    prompt = f"""
Transform this {section_name} section for "{business_name}" into a MODERN design using Tailwind CSS.

🚨 CRITICAL RULES:
1. PRESERVE ALL text content exactly as-is
2. PRESERVE ALL image URLs exactly as-is
3. PRESERVE ALL links exactly as-is
4. ONLY change CSS classes to Tailwind classes
5. ONLY improve layout and spacing

========== ORIGINAL HTML ==========
{section_html[:15000]}

========== MODERNIZATION INSTRUCTIONS ==========

For {section_name.upper()}:

1. **Convert to Tailwind CSS classes**:
   - Remove old CSS classes
   - Add modern Tailwind classes
   - Keep all content, text, images, links unchanged

2. **Modern styling for {section_name}**:
   {'- Large gradient hero: bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-900' if section_name == 'hero' else ''}
   {'- Huge headings: text-7xl md:text-9xl font-black' if section_name == 'hero' else ''}
   {'- Service cards: bg-white rounded-3xl shadow-2xl p-8 hover:shadow-3xl hover:-translate-y-2' if section_name == 'services' else ''}
   {'- Testimonial cards: bg-white rounded-2xl shadow-xl p-6' if section_name == 'testimonials' else ''}
   {'- Large spacing: py-24 or py-32' if section_name != 'header' else 'sticky top-0 z-50 bg-white/95 backdrop-blur-lg'}
   - Responsive: use sm:, md:, lg:, xl: breakpoints

3. **Preserve**:
   - ALL text content
   - ALL image src attributes
   - ALL href links
   - ALL phone numbers, emails, addresses

OUTPUT: Only the modernized HTML for this section - no explanations!
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You modernize HTML sections with Tailwind CSS while preserving ALL content. Never change text, images, or links - only styling."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,  # Low temperature for faithful preservation
        max_tokens=8000
    )

    result = response.choices[0].message.content.strip()

    # Clean markdown if present
    if "```" in result:
        result = re.sub(r'^```(?:html)?\s*\n', '', result, flags=re.MULTILINE)
        result = re.sub(r'\n```\s*$', '', result, flags=re.MULTILINE)

    return result


def main():
    print("\n" + "="*80)
    print("SECTION-BY-SECTION MODERNIZATION")
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
        print(f"Original HTML: {len(business.scraped_html):,} characters")

        # Extract sections
        print("\nStep 1: Extracting sections from original HTML...")
        sections = extract_sections(business.scraped_html)
        print(f"Found {len(sections)} sections: {', '.join(sections.keys())}")

        # Modernize each section
        modernized_sections = {}

        for i, (section_name, section_html) in enumerate(sections.items(), 1):
            print(f"\nStep {i+1}: Modernizing {section_name} section ({len(section_html)} chars)...")

            modernized = modernize_section(
                openai_client,
                section_name,
                section_html,
                business.name
            )

            modernized_sections[section_name] = modernized
            print(f"  Result: {len(modernized)} characters")

            # Verify content preservation
            soup_orig = BeautifulSoup(section_html, 'html.parser')
            soup_mod = BeautifulSoup(modernized, 'html.parser')

            orig_images = len(soup_orig.find_all('img'))
            mod_images = len(soup_mod.find_all('img'))

            print(f"  Images: {orig_images} -> {mod_images} {'OK' if orig_images == mod_images else 'MISSING!'}")

        # Build complete HTML
        print("\nStep Final: Building complete HTML document...")

        complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business.name} - Professional Electrical Services</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in-up {{ animation: fadeInUp 0.8s ease-out; }}
        html {{ scroll-behavior: smooth; }}
    </style>
</head>
<body class="font-sans antialiased bg-white text-gray-900">

{modernized_sections.get('header', '')}

{modernized_sections.get('hero', '')}

{modernized_sections.get('services', '')}

{modernized_sections.get('about', '')}

{modernized_sections.get('testimonials', '')}

{modernized_sections.get('contact', '')}

{modernized_sections.get('footer', '')}

{modernized_sections.get('full_body', '')}

</body>
</html>"""

        print(f"\nComplete HTML: {len(complete_html):,} characters")

        # Count elements
        soup_final = BeautifulSoup(complete_html, 'html.parser')
        print(f"Total images: {len(soup_final.find_all('img'))}")
        print(f"Total links: {len(soup_final.find_all('a'))}")
        print(f"Total sections: {len(soup_final.find_all(['section', 'div'], class_=True))}")

        # Save to database
        print("\nSaving to database...")
        old_templates = db.query(Template).filter(Template.business_id == business.id).all()
        for t in old_templates:
            db.delete(t)
        db.commit()

        template = Template(
            business_id=business.id,
            variant_number=1,
            html_content=complete_html,
            css_content="",
            js_content=None,
            improvements_made={"method": "section_by_section_modernization"},
            generated_at=__import__('datetime').datetime.utcnow()
        )

        db.add(template)
        db.commit()

        # Save to file
        filename = "template_cc_electrical_SECTION_BY_SECTION.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(complete_html)

        print("\n" + "="*80)
        print("SUCCESS - SECTION-BY-SECTION MODERNIZATION COMPLETE!")
        print("="*80)
        print(f"\nFile: backend/{filename}")
        print(f"Size: {len(complete_html):,} characters")
        print(f"\nFull path: {os.path.abspath(filename)}")
        print("\nOPEN THIS FILE IN YOUR BROWSER!")

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
