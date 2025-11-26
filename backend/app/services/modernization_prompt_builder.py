"""
Modernization Prompt Builder
Builds AI prompts for template modernization with exact brand preservation.
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

import json
from typing import Optional
from app.models.business import Business
from app.prompts.modernization_prompts import (
    MODERNIZATION_PROMPT,
    VARIANT_INSTRUCTIONS,
    CSS_FRAMEWORK_INSTRUCTIONS
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class ModernizationPromptBuilder:
    """
    Service for building AI modernization prompts.

    Creates prompts that:
    - Preserve exact component structure
    - Preserve brand colors, logos, images, videos, maps
    - Apply modern CSS frameworks (Tailwind, Bootstrap, Material)
    - Create "WOW factor" professional designs
    """

    def __init__(self, business: Business):
        """
        Initialize prompt builder with business data.

        Args:
            business: Business model with scraped data
        """
        self.business = business

    def _clean_html_for_ai(self, html: str) -> str:
        """
        Clean HTML for GPT-4 while PRESERVING all structural information.

        KEEPS (CRITICAL for understanding component structure):
        - All class attributes (e.g., "hero", "services", "contact-form")
        - All id attributes (e.g., "about", "portfolio")
        - All text content
        - All semantic HTML tags
        - All image src and alt attributes

        REMOVES (not needed for redesign):
        - JavaScript (<script> tags)
        - HTML comments
        - Meta tags
        - Inline styles (CSS extracted separately)
        - Event handlers (onclick, etc.)
        - Data attributes

        Args:
            html: Raw HTML string

        Returns:
            Optimized HTML with full structural information preserved
        """
        import re

        # Remove all <script> tags and their content (largest reduction)
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # Remove <meta> tags (not needed for visual structure)
        html = re.sub(r'<meta[^>]*>', '', html, flags=re.IGNORECASE)

        # Remove <link> tags (CSS already extracted separately)
        html = re.sub(r'<link[^>]*>', '', html, flags=re.IGNORECASE)

        # Remove <style> tags (CSS already extracted)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # CRITICAL: KEEP class and id attributes!
        # These are ESSENTIAL for GPT-4 to understand component structure
        # (e.g., class="hero-section", class="services", id="about", id="contact")
        # DO NOT REMOVE THEM!

        # Remove data- attributes (not needed for structure)
        html = re.sub(r'\s+data-[a-zA-Z0-9_-]+="[^"]*"', '', html)
        html = re.sub(r"\s+data-[a-zA-Z0-9_-]+='[^']*'", '', html)

        # Remove inline event handlers
        html = re.sub(r'\s+on[a-z]+="[^"]*"', '', html, flags=re.IGNORECASE)
        html = re.sub(r"\s+on[a-z]+='[^']*'", '', html, flags=re.IGNORECASE)

        # Remove style attributes (CSS already extracted)
        html = re.sub(r'\s+style="[^"]*"', '', html)
        html = re.sub(r"\s+style='[^']*'", '', html)

        # Collapse multiple whitespace into single space
        html = re.sub(r'\s+', ' ', html)

        # Collapse multiple newlines
        html = re.sub(r'\n+', '\n', html)

        # Remove leading/trailing whitespace on each line
        html = '\n'.join(line.strip() for line in html.split('\n'))

        # Remove empty lines
        html = '\n'.join(line for line in html.split('\n') if line.strip())

        original_size = len(self.business.scraped_html or '')
        cleaned_size = len(html)

        # CRITICAL: Further reduce to fit in GPT-4's context limit
        # GPT-4 has 128K token limit. With our prompt, we can use max ~15K chars of HTML
        MAX_HTML_CHARS = 15000
        if cleaned_size > MAX_HTML_CHARS:
            html = html[:MAX_HTML_CHARS]
            logger.warning(f"[PromptBuilder] HTML truncated to {MAX_HTML_CHARS} chars to fit token limit")

        reduction_pct = 100 - (len(html) * 100 // max(original_size, 1))

        logger.info(f"[PromptBuilder] Optimized HTML from {original_size} chars "
                   f"to {len(html)} chars (reduced {reduction_pct}%) - KEPT all classes/IDs/structure")

        return html.strip()

    def _format_component_details(self, component_structure: list) -> str:
        """
        Format component structure into explicit component-by-component requirements.

        Args:
            component_structure: List of component dictionaries with content

        Returns:
            Formatted string with explicit component requirements
        """
        if not component_structure:
            return "No components found - create a professional single-page website with hero, about, services, and contact sections."

        details = []
        for i, comp in enumerate(component_structure, 1):
            comp_type = comp.get('type', 'content')
            heading = comp.get('heading', '')
            content = comp.get('content', '')
            comp_id = comp.get('id', '')
            comp_classes = comp.get('classes', '')

            # Format component requirement
            details.append(f"\nCOMPONENT {i}: {comp_type.upper()}")
            if heading:
                details.append(f"  Heading: {heading}")
            if content:
                details.append(f"  Content: {content}")
            if comp_id:
                details.append(f"  Original ID: {comp_id}")
            if comp_classes:
                details.append(f"  Original Classes: {comp_classes}")
            details.append(f"  REQUIREMENT: Create a modern, styled <section> for this {comp_type} component")
            details.append(f"              Include ALL the text content shown above")
            details.append(f"              Apply modern {comp_type} styling with Tailwind classes")

        formatted = '\n'.join(details)
        return formatted

    def build_prompt(self, variant_number: int, problems_list: Optional[str] = None) -> str:
        """
        Build complete modernization prompt for specified variant.

        Args:
            variant_number: Variant number (1=Tailwind, 2=Bootstrap, 3=Material)
            problems_list: Optional list of identified website problems

        Returns:
            Complete prompt string ready for OpenAI API
        """
        logger.info(f"[PromptBuilder] Building prompt for variant {variant_number}")

        # Validate variant number
        if variant_number not in [1, 2, 3]:
            raise ValueError(f"Invalid variant number: {variant_number}. Must be 1, 2, or 3.")

        # Get variant configuration
        variant_config = VARIANT_INSTRUCTIONS[variant_number]

        # Prepare data for injection - CLEAN HTML to reduce size
        raw_html = self.business.scraped_html or ""
        scraped_html = self._clean_html_for_ai(raw_html)  # Strip unnecessary content
        scraped_css = self.business.scraped_css or ""

        # Component data
        component_count = self.business.component_count or 0
        component_structure = self.business.component_structure or []

        # Format component details for prompt - make it VERY explicit
        component_details = self._format_component_details(component_structure)

        # Brand colors
        color_palette = json.dumps(self.business.color_palette) if self.business.color_palette else '[]'

        # Media assets
        logo_urls = json.dumps(self.business.logo_urls) if self.business.logo_urls else '[]'
        image_urls = json.dumps(self.business.image_urls) if self.business.image_urls else '[]'
        video_urls = json.dumps(self.business.video_urls) if self.business.video_urls else '[]'
        map_embeds = json.dumps(self.business.map_embeds) if self.business.map_embeds else '[]'

        # Business info
        business_name = self.business.name or "Business"
        category = self.business.category or "General Business"
        description = self.business.description or "A local business"

        # Problems list
        if not problems_list:
            problems_list = self._generate_default_problems()

        # Framework-specific instructions
        framework_instructions = variant_config['framework_instructions']
        variant_type = variant_config['type']
        variant_detailed = variant_config['detailed']
        css_framework = variant_config['css_framework']

        # Build complete prompt by injecting variables
        prompt = MODERNIZATION_PROMPT.format(
            scraped_html=scraped_html,
            scraped_css=scraped_css,
            component_count=component_count,
            component_details=component_details,  # NEW: Detailed component-by-component requirements
            color_palette=color_palette,
            logo_urls=logo_urls,
            image_urls=image_urls,
            video_urls=video_urls,
            map_embeds=map_embeds,
            business_name=business_name,
            category=category,
            description=description,
            problems_list=problems_list,
            css_framework=css_framework,
            framework_specific_instructions=framework_instructions,
            variant_type=variant_type,
            variant_detailed_instructions=variant_detailed
        )

        logger.info(f"[PromptBuilder] ✅ Built prompt for {business_name} - "
                   f"Variant {variant_number} ({css_framework}) - "
                   f"{len(scraped_html)} chars HTML, {component_count} components")

        return prompt

    def _generate_default_problems(self) -> str:
        """
        Generate default list of problems to fix based on evaluation score.

        Returns:
            String listing problems to address
        """
        problems = []

        score = self.business.score or 50

        if score < 70:
            problems.append("- Website looks outdated and unprofessional")
            problems.append("- Poor mobile responsiveness")
            problems.append("- Lacks modern design patterns and visual hierarchy")
            problems.append("- Typography needs improvement")
            problems.append("- Navigation could be cleaner and more intuitive")

        if score < 50:
            problems.append("- Very dated appearance hurting credibility")
            problems.append("- Confusing layout and information architecture")
            problems.append("- Poor use of whitespace and spacing")

        if not problems:
            problems.append("- Modernize overall aesthetic while preserving brand identity")
            problems.append("- Enhance visual appeal with contemporary design patterns")
            problems.append("- Improve typography and spacing for better readability")

        return '\n'.join(problems)

    def get_variant_name(self, variant_number: int) -> str:
        """
        Get human-readable name for variant.

        Args:
            variant_number: Variant number (1-3)

        Returns:
            Variant name (e.g., "Tailwind CSS - Clean Modern")
        """
        if variant_number not in [1, 2, 3]:
            return "Unknown Variant"

        variant_config = VARIANT_INSTRUCTIONS[variant_number]
        return variant_config['type']

    def get_css_framework(self, variant_number: int) -> str:
        """
        Get CSS framework for variant.

        Args:
            variant_number: Variant number (1-3)

        Returns:
            CSS framework name (tailwind, bootstrap, material)
        """
        if variant_number not in [1, 2, 3]:
            return "unknown"

        variant_config = VARIANT_INSTRUCTIONS[variant_number]
        return variant_config['css_framework']


def build_modernization_prompt(business: Business, variant_number: int) -> str:
    """
    Convenience function to build modernization prompt.

    Args:
        business: Business model with scraped data
        variant_number: Variant number (1-3)

    Returns:
        Complete prompt string
    """
    builder = ModernizationPromptBuilder(business)
    return builder.build_prompt(variant_number)
