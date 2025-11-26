"""
Component-Based Template Generator
Preserves ALL components from original website while applying modern design
"""

from typing import Optional
from app.models import Business, Template
from app.config import settings
from openai import OpenAI
from datetime import datetime
from app.utils.logging_config import get_logger
import re
import json

logger = get_logger(__name__)
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


def generate_component_based_template(business: Business) -> Optional[Template]:
    """
    Generate modern template preserving ALL components from original website.

    Args:
        business: Business with scraped data and component_structure

    Returns:
        Template with ALL components modernized
    """
    if not openai_client:
        logger.error("OpenAI API key not configured")
        return None

    # Extract business info
    business_name = business.name
    phone = business.phone or "Contact us"
    email = business.email or "info@business.com"
    address = business.address or "Location"

    # Get media
    images = (business.image_urls or [])[:10]
    logos = business.logo_urls or []
    logo = logos[0] if logos else ""
    videos = business.video_urls or []
    maps = business.map_embeds or []
    colors = business.color_palette or []

    # Get component structure - THIS IS CRITICAL
    components = business.component_structure or []
    component_count = len(components)

    logger.info(f"[ComponentGenerator] Business has {component_count} components")

    # Build DETAILED component list - EVERY component individually
    component_list = []
    for i, comp in enumerate(components, 1):
        comp_type = comp.get('type', 'content')
        heading = comp.get('heading', '')
        comp_id = comp.get('id', '')
        classes = comp.get('classes', '')

        # Build detailed description for each component
        desc = f"SECTION {i}: {comp_type.upper()}"
        if heading:
            desc += f" - '{heading[:100]}'"
        if comp_id:
            desc += f" (id={comp_id})"
        component_list.append(desc)

    component_text = "\n".join(component_list)

    # Format images for easy reference
    image_list = '\n'.join([f"  - {img}" for img in images[:10]])
    video_list = '\n'.join([f"  - {vid}" for vid in videos[:5]]) if videos else "  (none)"

    # Build section-by-section requirements
    section_requirements = []
    img_idx = 0
    for i, comp in enumerate(components, 1):
        comp_type = comp.get('type', 'content')
        heading = comp.get('heading', '') or f"{comp_type.title()} Section {i}"

        # Assign images to sections
        img_to_use = images[img_idx] if img_idx < len(images) else ""
        img_idx = (img_idx + 1) % max(len(images), 1)

        section_requirements.append(
            f"<section class=\"py-16 px-4\"><!-- SECTION {i}: {comp_type.upper()} -->\n"
            f"  <h2>{heading[:100]}</h2>\n"
            f"  {f'<img src=\"{img_to_use}\" class=\"w-full max-w-2xl mx-auto rounded-lg shadow-lg\">' if img_to_use else ''}\n"
            f"  <p>Add content for {comp_type} here</p>\n"
            f"</section>"
        )

    sections_template = '\n\n'.join(section_requirements)

    # Build ULTRA-EXPLICIT prompt with HTML skeleton
    prompt = f"""You are generating a complete modern website. Follow this EXACT structure:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <!-- HEADER/NAVBAR with logo -->
    <header class="bg-white shadow-md p-4">
        <img src="{logo}" alt="Logo" class="h-12">
        <nav>Links to sections</nav>
    </header>

{sections_template}

    <!-- CONTACT/FOOTER -->
    <footer class="bg-gray-800 text-white py-8">
        <p>Phone: {phone}</p>
        <p>Email: {email}</p>
        <p>Address: {address}</p>
    </footer>
</body>
</html>

CRITICAL INSTRUCTIONS:
1. REPLACE the placeholder content in EACH of the {component_count} sections above
2. USE ALL THESE IMAGES - distribute them across sections:
{image_list}
3. Add modern Tailwind styling: gradients, shadows, hover effects, rounded corners
4. Make it fully responsive (use sm:, md:, lg: breakpoints)
5. Use colors: {', '.join(colors[:3])}
6. Professional, modern, "WOW factor" design
7. DO NOT remove any sections - expand and style ALL {component_count} sections
8. Output ONLY the complete HTML - no explanations"""

    try:
        logger.info(f"[ComponentGenerator] Generating template for {business_name}")
        logger.info(f"[ComponentGenerator] Including {component_count} components")
        logger.info(f"[ComponentGenerator] Prompt size: {len(prompt)} chars")

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional web developer. Your task is to generate COMPLETE HTML code with EVERY SINGLE section requested. CRITICAL RULES:\n1. Output ONLY HTML code - NO explanations, NO markdown\n2. Start with <!DOCTYPE html>\n3. Create a <section> tag for EVERY section listed in the requirements\n4. Use ALL images and videos provided\n5. DO NOT skip any sections\n6. Make it modern and professional with Tailwind CSS"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Lower temperature for more consistent output
            max_tokens=16384  # Maximum to get full website
        )

        html = response.choices[0].message.content.strip()

        # Clean markdown if present
        if "```" in html:
            html = re.sub(r'^```(?:html)?\s*\n', '', html, flags=re.MULTILINE)
            html = re.sub(r'\n```\s*$', '', html, flags=re.MULTILINE)

        # Extract HTML document
        doctype_match = re.search(r'<!DOCTYPE\s+html[^>]*>', html, re.IGNORECASE)
        if doctype_match:
            start_pos = doctype_match.start()
            end_match = re.search(r'</html\s*>', html, re.IGNORECASE)
            if end_match:
                html = html[start_pos:end_match.end()]

        logger.info(f"[ComponentGenerator] Generated {len(html)} chars of HTML")

        # Count sections in generated HTML
        section_count = html.lower().count('<section')
        logger.info(f"[ComponentGenerator] Generated HTML contains {section_count} sections (expected {component_count})")

        # Validate minimum
        if len(html) < 1000 or '<!doctype' not in html.lower():
            logger.error("[ComponentGenerator] Invalid HTML generated")
            return None

        # Create template
        template = Template(
            business_id=business.id,
            variant_number=1,
            html_content=html,
            css_content="",
            js_content=None,
            improvements_made={
                "method": "component_based_generation",
                "status": "success",
                "original_components": component_count,
                "sections_generated": section_count
            },
            generated_at=datetime.utcnow()
        )

        logger.info(f"[ComponentGenerator] ✅ Template created with {section_count} sections")
        return template

    except Exception as e:
        logger.error(f"[ComponentGenerator] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
