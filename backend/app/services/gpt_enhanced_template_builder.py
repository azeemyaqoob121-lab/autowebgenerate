"""
GPT-Enhanced Template Builder

This module builds templates using ChatGPT-4 to create STUNNING modern designs
while preserving all scraped content.
"""

import logging
from typing import Optional
from bs4 import BeautifulSoup
import re
from openai import OpenAI

from app.config import settings
from app.models.template import Template
from app.models.business import Business
from app.services.template_validator import TemplateValidator

logger = logging.getLogger(__name__)

def clean_html_for_prompt(html: str) -> str:
    """Clean HTML for ChatGPT - remove scripts, styles, comments but keep structure"""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove all scripts, styles, and SVGs
    for tag in soup(['script', 'style', 'svg', 'noscript', 'iframe']):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup))):
        if comment.parent.name != 'style':
            comment.extract()

    # Get text representation
    cleaned = str(soup)

    # Remove excessive whitespace
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    cleaned = re.sub(r'  +', ' ', cleaned)

    return cleaned.strip()


def build_gpt_enhanced_template(business: Business) -> Optional[Template]:
    """
    Build a template using ChatGPT-4 with ALL scraped content

    This function sends the scraped HTML + all media to ChatGPT-4
    and gets back a STUNNING modern redesigned version
    """
    logger.info(f"[GPTEnhanced] Building template for {business.name}")
    logger.info(f"[GPTEnhanced] Components: {business.component_count}, Images: {len(business.image_urls or [])}, Videos: {len(business.video_urls or [])}")

    # Get all scraped assets
    scraped_html = business.scraped_html or ""
    images = business.image_urls or []
    videos = business.video_urls or []
    logos = business.logo_urls or []
    colors = business.color_palette or []
    component_count = business.component_count or 0

    # Business info
    business_name = business.name or "Business"
    phone = business.phone or ""
    email = business.email or ""
    address = business.address or ""

    if not scraped_html:
        logger.error(f"[GPTEnhanced] No scraped HTML for {business_name}")
        return None

    # Clean HTML to reduce tokens
    logger.info(f"[GPTEnhanced] Original scraped HTML size: {len(scraped_html):,} characters")
    cleaned_html = clean_html_for_prompt(scraped_html)
    logger.info(f"[GPTEnhanced] Cleaned HTML size: {len(cleaned_html):,} characters")

    # Format lists
    all_images_list = "\n".join([f"- {img}" for img in images])
    all_videos_list = "\n".join([f"- {vid}" for vid in videos]) if videos else "No videos"
    all_logos_list = "\n".join([f"- {logo}" for logo in logos]) if logos else "No logos"

    # Create PREMIUM-FOCUSED prompt with specific design guidance
    prompt = f"""Create an ULTRA-PREMIUM modern website that looks like it cost $50,000+.

BUSINESS: {business_name}
Contact: {phone} | {email} | {address}

═══════════════════════════════════════════════════════════════
CRITICAL: USE EVERY SINGLE ASSET
═══════════════════════════════════════════════════════════════
✓ ALL {len(images)} images - Place strategically with hover effects
✓ ALL {len(videos)} videos - Feature prominently with autoplay/controls
✓ ALL {len(logos)} logos - Use in header/footer with proper branding
✓ ALL {component_count} sections - Preserve structure, modernize styling

AVAILABLE IMAGES ({len(images)}):
{all_images_list}

AVAILABLE VIDEOS ({len(videos)}):
{all_videos_list}

AVAILABLE LOGOS ({len(logos)}):
{all_logos_list}

═══════════════════════════════════════════════════════════════
PREMIUM DESIGN REQUIREMENTS
═══════════════════════════════════════════════════════════════

1. HERO SECTION - Make it WOW:
   - Full viewport height (min-h-screen)
   - Massive gradient heading (text-6xl md:text-7xl lg:text-8xl)
   - Animated gradient text (bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600)
   - Floating elements with parallax effect
   - CTA button with glow effect (shadow-2xl shadow-blue-500/50)

2. TYPOGRAPHY - Make it BOLD:
   - Headings: text-5xl to text-8xl with font-bold
   - Gradient text on all major headings
   - Perfect line-height (leading-tight for headings, leading-relaxed for body)
   - Use Inter or Poppins font

3. IMAGES - Make them POP:
   - Every image in a container with: rounded-2xl overflow-hidden shadow-2xl
   - Hover effect: transform hover:scale-110 transition-transform duration-500
   - Add subtle border: ring-2 ring-white/20
   - Wrap in perspective containers for 3D effect

4. SECTIONS - Premium Spacing:
   - Every section: py-24 md:py-32 lg:py-40
   - Alternate backgrounds: white, gradient, or subtle pattern
   - Add animated gradient blobs in background
   - Use max-w-7xl mx-auto for content

5. CARDS/COMPONENTS - Floating Effect:
   - White cards with: bg-white rounded-3xl shadow-2xl p-8
   - Hover: hover:-translate-y-4 hover:shadow-3xl transition-all duration-300
   - Add subtle gradient borders

6. COLORS - Rich & Vibrant:
   - Use bold gradients: bg-gradient-to-br from-purple-600 via-pink-600 to-red-600
   - Glassmorphism effects: backdrop-blur-lg bg-white/10
   - Bright accent colors for CTAs

7. ANIMATIONS - Smooth & Professional:
   - All hover effects: transition-all duration-300
   - Entrance animations on scroll (animate-fade-in-up)
   - Floating/pulsing elements
   - Smooth parallax on images

8. LAYOUT - Modern Grid:
   - Use CSS Grid for sections: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
   - Asymmetric layouts for visual interest
   - Overlapping elements for depth

9. CALL-TO-ACTION - Make it Convert:
   - Large, prominent buttons with gradients
   - Hover effects that scale and glow
   - Multiple CTAs throughout

10. FOOTER - Premium Finish:
    - Dark gradient background
    - Multi-column layout with all links
    - Social media icons with hover effects

═══════════════════════════════════════════════════════════════
STRUCTURE TO FOLLOW
═══════════════════════════════════════════════════════════════
Based on the original HTML, create these sections with premium styling:
1. Hero with gradient heading + primary image/video
2. About/Services with cards and images
3. Gallery/Portfolio with ALL remaining images in grid
4. Video section if videos exist
5. Contact section with gradient background
6. Footer with all business info

ORIGINAL WEBSITE HTML (use this structure and content):
{cleaned_html}

═══════════════════════════════════════════════════════════════
REQUIRED CSS (Include in <head>)
═══════════════════════════════════════════════════════════════
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');

@keyframes fade-in-up {{
    from {{ opacity: 0; transform: translateY(40px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-20px); }}
}}

@keyframes blob {{
    0%, 100% {{ transform: translate(0, 0) scale(1) rotate(0deg); }}
    25% {{ transform: translate(20px, -50px) scale(1.1) rotate(90deg); }}
    50% {{ transform: translate(-30px, 20px) scale(0.9) rotate(180deg); }}
    75% {{ transform: translate(40px, 30px) scale(1.05) rotate(270deg); }}
}}

@keyframes gradient-shift {{
    0%, 100% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
}}

@keyframes pulse-glow {{
    0%, 100% {{ box-shadow: 0 0 20px rgba(139, 92, 246, 0.5); }}
    50% {{ box-shadow: 0 0 60px rgba(139, 92, 246, 0.8), 0 0 100px rgba(139, 92, 246, 0.4); }}
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; }}
html {{ scroll-behavior: smooth; }}

.animate-fade-in-up {{ animation: fade-in-up 0.8s ease-out forwards; }}
.animate-float {{ animation: float 3s ease-in-out infinite; }}
.animate-blob {{ animation: blob 15s infinite; }}
.animate-gradient {{ animation: gradient-shift 8s ease infinite; background-size: 200% 200%; }}
.animate-pulse-glow {{ animation: pulse-glow 2s ease-in-out infinite; }}

.gradient-text {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.glass {{
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}}

.card-hover {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

.card-hover:hover {{
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}}

img {{ transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1); }}
img:hover {{ transform: scale(1.1); }}
</style>

<script src="https://cdn.tailwindcss.com"></script>

═══════════════════════════════════════════════════════════════
OUTPUT: Complete HTML website with:
- ALL {component_count} sections from original (modernized)
- ALL {len(images)} images (with hover effects)
- ALL {len(videos)} videos (featured prominently)
- ALL {len(logos)} logos (in header/footer)
- Ultra-premium design that looks expensive
- Smooth animations and interactions everywhere
═══════════════════════════════════════════════════════════════"""

    logger.info(f"[GPTEnhanced] Prompt size: {len(prompt):,} chars")

    # Call ChatGPT-4
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an ELITE web designer who redesigns websites to be ULTRA-MODERN and STUNNING using Tailwind CSS.

CRITICAL FAILURE CONDITIONS - If you violate these, your output is WORTHLESS:

1. DO NOT COMBINE SECTIONS - If the input has 18 sections, output MUST have 18 sections
2. DO NOT SKIP SECTIONS - Every single section from input must appear in output
3. DO NOT SIMPLIFY STRUCTURE - Keep the EXACT same structure and section order
4. DO NOT REMOVE CONTENT - Every image, video, text must be in output
5. ONLY ADD STYLING - Your ONLY job is to add Tailwind CSS classes and modern effects

WHAT SUCCESS LOOKS LIKE:
- Input has X sections -> Output has X sections (SAME NUMBER)
- Each section gets modern Tailwind styling
- All images, videos, text preserved
- Output looks like a $10,000+ website

WHAT FAILURE LOOKS LIKE:
- Combining "About" and "Services" into one section (WRONG!)
- Skipping sections because they seem redundant (WRONG!)
- Creating your own simplified structure (WRONG!)
- Removing images or content to "clean up" (WRONG!)

Remember: You're a STYLIST, not a RESTRUCTURER. Add modern CSS, DON'T change structure!

Output ONLY pure HTML, no explanations, no markdown."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=16384,
            temperature=0.4
        )

        html_content = response.choices[0].message.content.strip()

        # Clean up any markdown code fences
        html_content = re.sub(r'^```html\s*', '', html_content)
        html_content = re.sub(r'```\s*$', '', html_content)
        html_content = html_content.strip()

        logger.info(f"[GPTEnhanced] Generated {len(html_content):,} characters")

        # Validate
        validator = TemplateValidator(business)
        validation_result = validator.validate_template(html_content)

        logger.info(f"[GPTEnhanced] Validation: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")

        # Create template
        template = Template(
            business_id=business.id,
            html_content=html_content,
            css_content="",
            improvements_made={
                "method": "chatgpt_modern_redesign",
                "chatgpt_generated": True,
                "validation": {
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            },
            variant_number=1
        )

        logger.info(f"[GPTEnhanced] SUCCESS - Template created for {business_name}")
        return template

    except Exception as e:
        logger.error(f"[GPTEnhanced] ERROR calling ChatGPT: {str(e)}")
        return None
