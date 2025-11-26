"""
SIMPLE Template Generator - Fits within GPT-4 token limits
Generates modern templates WITHOUT exceeding context window
"""

from typing import Optional
from app.models import Business, Template
from app.config import settings
from openai import OpenAI
from datetime import datetime
from app.utils.logging_config import get_logger
import re

logger = get_logger(__name__)
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


def generate_simple_modern_template(business: Business) -> Optional[Template]:
    """
    Generate ONE modern template using a SIMPLE prompt that fits within token limits.

    Args:
        business: Business with scraped data

    Returns:
        Template or None
    """
    if not openai_client:
        logger.error("OpenAI API key not configured")
        return None

    # Extract key info from business
    business_name = business.name
    phone = business.phone or "Contact us"
    email = business.email or "info@business.com"
    address = business.address or "Location"

    # Get first few images
    images = (business.image_urls or [])[:5]
    logo = (business.logo_urls or [""])[0] if business.logo_urls else ""

    # Get limited HTML snippet (first 8000 chars only)
    html_snippet = (business.scraped_html or "")[:8000]

    # Simple, SHORT prompt
    prompt = f"""Create a modern website for "{business_name}".

Business Info:
- Name: {business_name}
- Phone: {phone}
- Email: {email}
- Address: {address}
- Logo: {logo}
- Images: {', '.join(images[:3])}

Original HTML (first part):
{html_snippet}

Requirements:
1. Use Tailwind CSS: <script src="https://cdn.tailwindcss.com"></script>
2. Modern design: gradients, shadows, rounded corners, hover effects
3. Include: navbar, hero, services, about, contact sections
4. Use the business info above
5. Responsive: mobile, tablet, desktop
6. Professional and clean

Output ONLY the complete HTML. Start with <!DOCTYPE html>"""

    try:
        logger.info(f"[SimpleGenerator] Generating template for {business_name}")
        logger.info(f"[SimpleGenerator] Prompt size: {len(prompt)} chars")

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You generate HTML code. Output ONLY HTML - no explanations. Start with <!DOCTYPE html>"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=16384
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

        logger.info(f"[SimpleGenerator] Generated {len(html)} chars of HTML")

        # Validate minimum
        if len(html) < 500 or '<!doctype' not in html.lower():
            logger.error("[SimpleGenerator] Invalid HTML generated")
            return None

        # Create template
        template = Template(
            business_id=business.id,
            variant_number=1,
            html_content=html,
            css_content="",
            js_content=None,
            improvements_made={"method": "simple_generation", "status": "success"},
            generated_at=datetime.utcnow()
        )

        logger.info(f"[SimpleGenerator] ✅ Template created successfully")
        return template

    except Exception as e:
        logger.error(f"[SimpleGenerator] Error: {str(e)}")
        return None
