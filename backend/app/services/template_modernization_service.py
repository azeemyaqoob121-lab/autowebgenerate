"""
Template Modernization Service
Generates modernized templates using scraped HTML and AI enhancement.
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

import logging
from typing import List, Optional
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models.business import Business
from app.models.template import Template
from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService
from app.services.modernization_prompt_builder import ModernizationPromptBuilder
from app.services.template_validator import TemplateValidator
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Configure OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class TemplateModernizationService:
    """
    Service for generating modernized templates from scraped HTML.

    Workflow:
    1. Check if business has scraped_html
    2. If not, trigger enhanced scraping first
    3. Build modernization prompts for 3 CSS framework variants
    4. Generate templates with OpenAI GPT-4 Turbo
    5. Validate and save templates to database
    """

    def __init__(self, db: Session):
        """
        Initialize modernization service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.scraper_service = EnhancedWebsiteScraperService(db)

    def generate_modernized_templates(
        self,
        business_id: str,
        force_rescrape: bool = False
    ) -> List[Template]:
        """
        Generate 3 modernized template variants for a business.

        Args:
            business_id: UUID of business
            force_rescrape: Force re-scraping even if scraped_html exists

        Returns:
            List of 3 Template instances (Tailwind, Bootstrap, Material variants)

        Raises:
            ValueError: If business not found or scraping fails
        """
        logger.info(f"[Modernization] Starting template generation for business {business_id}")

        # Load business
        business = self.db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError(f"Business {business_id} not found")

        # Check if scraping is needed
        if not business.scraped_html or force_rescrape:
            logger.info(f"[Modernization] Scraping required for {business.name}")
            success = self.scraper_service.scrape_complete_website(business_id)
            if not success:
                raise ValueError(f"Failed to scrape website for business {business.name}")

            # Reload business to get scraped data
            self.db.refresh(business)

        # Generate template using GPT-ENHANCED builder with WOW FACTOR prompts
        # This guarantees ALL components + GPT-4 modern design
        templates = []
        try:
            # Use GPT-ENHANCED BUILDER: Python builds structure, GPT-4 enhances with STUNNING design
            from app.services.gpt_enhanced_template_builder import build_gpt_enhanced_template

            logger.info(f"[Modernization] ═══════════════════════════════════════════════════════")
            logger.info(f"[Modernization] 🚀 STARTING GPT-ENHANCED TEMPLATE GENERATION")
            logger.info(f"[Modernization] ═══════════════════════════════════════════════════════")
            logger.info(f"[Modernization] Business: {business.name}")
            logger.info(f"[Modernization] Building GPT-enhanced template with ALL {business.component_count} components")
            logger.info(f"[Modernization] Including {len(business.image_urls or [])} images, {len(business.video_urls or [])} videos")
            logger.info(f"[Modernization] Target: STUNNING modern design with WOW factor!")
            logger.info(f"[Modernization] ═══════════════════════════════════════════════════════")

            template = build_gpt_enhanced_template(business)
            if template:
                # Save to database
                self.db.add(template)
                self.db.commit()
                templates.append(template)
                logger.info(f"[Modernization] ═══════════════════════════════════════════════════════")
                logger.info(f"[Modernization] ✅ SUCCESS - Generated GPT-enhanced template for {business.name}")
                logger.info(f"[Modernization] ═══════════════════════════════════════════════════════")
            else:
                logger.error(f"[Modernization] ❌ Failed to generate template")
        except Exception as e:
            logger.error(f"[Modernization] ❌ Failed to generate template: {str(e)}")
            import traceback
            traceback.print_exc()

        return templates

    def _generate_single_variant(
        self,
        business: Business,
        variant_number: int
    ) -> Optional[Template]:
        """
        Generate a single template variant.

        Args:
            business: Business model with scraped data
            variant_number: Variant number (1=Tailwind, 2=Bootstrap, 3=Material)

        Returns:
            Template instance or None if generation failed
        """
        if not openai_client:
            logger.error("[Modernization] OpenAI API key not configured")
            return None

        try:
            # Build prompt
            prompt_builder = ModernizationPromptBuilder(business)
            prompt = prompt_builder.build_prompt(variant_number)
            variant_name = prompt_builder.get_variant_name(variant_number)
            css_framework = prompt_builder.get_css_framework(variant_number)

            logger.info(f"[Modernization] Generating {variant_name} for {business.name}")

            # Call OpenAI GPT-4o with STRICT instructions
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code generator. You ONLY output HTML code. NEVER write explanations, commentary, or markdown. Your ENTIRE response must be valid HTML starting with <!DOCTYPE html> and ending with </html>. DO NOT include any text before or after the HTML."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nREMEMBER: Output ONLY the complete HTML document. Start with <!DOCTYPE html> immediately. No explanations!"
                    }
                ],
                temperature=0.7,
                max_tokens=16384
            )

            # Extract generated HTML
            generated_html = response.choices[0].message.content.strip()

            logger.info(f"[Modernization] OpenAI response length: {len(generated_html)} chars")
            logger.info(f"[Modernization] Response preview (first 500 chars): {generated_html[:500]}")

            # Clean HTML (remove markdown code blocks if present)
            generated_html = self._clean_generated_html(generated_html)

            logger.info(f"[Modernization] After cleaning: {len(generated_html)} chars")

            # Basic HTML structure validation
            is_valid = self._validate_html(generated_html)
            if not is_valid:
                logger.warning(f"[Modernization] Basic HTML validation failed for variant {variant_number}")
                logger.warning(f"[Modernization] Will attempt strict validation anyway")

            # STRICT VALIDATION: Ensure ALL components, images, videos are present
            logger.info(f"[Modernization] Running STRICT validation on generated HTML...")

            validator = TemplateValidator(business)
            validation_result = validator.validate_template(generated_html)

            if not validation_result.is_valid:
                logger.error(f"[Modernization] ❌ VALIDATION FAILED - Generated HTML is INCOMPLETE!")
                logger.error(f"[Modernization] Errors: {validation_result.errors}")
                logger.error(f"[Modernization] Missing components: {validation_result.missing_components}")
                logger.error(f"[Modernization] Missing images: {len(validation_result.missing_images)}")
                logger.error(f"[Modernization] Missing videos: {len(validation_result.missing_videos)}")
                logger.error(f"[Modernization] Variant {variant_number} ({variant_name}) rejected due to incomplete output")
                return None  # Reject template - don't save incomplete templates
            else:
                logger.info(f"[Modernization] ✅ VALIDATION PASSED - All components, images, videos present!")
                logger.info(f"[Modernization] Stats: {validation_result.stats}")

            # Log validation warnings even if valid
            if validation_result.warnings:
                for warning in validation_result.warnings:
                    logger.warning(f"[Modernization] {warning}")

            # Create Template model
            template = Template(
                business_id=business.id,
                variant_number=variant_number,
                html_content=generated_html,
                css_content="",  # Inline CSS in HTML
                js_content=None,  # No separate JS
                improvements_made={
                    "variant_name": variant_name,
                    "css_framework": css_framework,
                    "generation_method": "modernization",
                    "improvements": self._extract_improvements(business),
                    "component_count": business.component_count,
                    "colors_preserved": len(business.color_palette) if business.color_palette else 0,
                    "validation": {
                        "passed": validation_result.is_valid,
                        "stats": validation_result.stats,
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings,
                        "missing_components": validation_result.missing_components,
                        "missing_images_count": len(validation_result.missing_images),
                        "missing_videos_count": len(validation_result.missing_videos)
                    }
                },
                generated_at=datetime.utcnow()
            )

            # Save to database
            self.db.add(template)
            self.db.commit()

            logger.info(f"[Modernization] ✅ Created {variant_name} template (ID: {template.id})")

            return template

        except Exception as e:
            logger.error(f"[Modernization] Error generating variant {variant_number}: {str(e)}")
            return None

    def regenerate_templates(
        self,
        business_id: str,
        force_rescrape: bool = False
    ) -> List[Template]:
        """
        Regenerate templates with fresh AI generation.

        Uses different CSS frameworks than previous generation to ensure variety.

        Args:
            business_id: UUID of business
            force_rescrape: Force re-scraping before regeneration

        Returns:
            List of newly generated Template instances
        """
        logger.info(f"[Modernization] Regenerating templates for business {business_id}")

        # Delete old templates to make room for new ones
        business = self.db.query(Business).filter(Business.id == business_id).first()
        if business:
            old_templates = self.db.query(Template).filter(
                Template.business_id == business_id
            ).all()

            for template in old_templates:
                self.db.delete(template)

            self.db.commit()
            logger.info(f"[Modernization] Deleted {len(old_templates)} old templates")

        # Generate new templates
        return self.generate_modernized_templates(business_id, force_rescrape)

    def _clean_generated_html(self, html: str) -> str:
        """
        Extract ONLY the HTML document from GPT-4's response.

        Removes:
        - Explanatory text before/after HTML
        - Markdown code blocks (```html ... ```)
        - Any commentary from GPT-4

        Extracts the HTML document from <!DOCTYPE html> (or <html>) to </html>

        Args:
            html: Raw generated content from GPT-4

        Returns:
            Clean HTML document only
        """
        import re

        # First, remove markdown code blocks if present
        if "```" in html:
            # Remove opening ```html or ```
            html = re.sub(r'^```(?:html)?\s*\n', '', html, flags=re.MULTILINE)
            # Remove closing ```
            html = re.sub(r'\n```\s*$', '', html, flags=re.MULTILINE)

        # Find the HTML document boundaries
        # Look for <!DOCTYPE html> or <html (case insensitive)
        doctype_match = re.search(r'<!DOCTYPE\s+html[^>]*>', html, re.IGNORECASE)
        html_tag_match = re.search(r'<html[^>]*>', html, re.IGNORECASE)

        # Determine start position
        start_pos = None
        if doctype_match:
            start_pos = doctype_match.start()
        elif html_tag_match:
            start_pos = html_tag_match.start()

        # Find closing </html> tag
        end_match = re.search(r'</html\s*>', html, re.IGNORECASE)
        end_pos = end_match.end() if end_match else None

        # Extract HTML document only
        if start_pos is not None and end_pos is not None:
            html = html[start_pos:end_pos]
            logger.info(f"[Modernization] Extracted clean HTML document ({len(html)} chars)")
        else:
            logger.warning("[Modernization] Could not find HTML boundaries, using entire response")

        return html.strip()

    def _validate_html(self, html: str) -> bool:
        """
        Validate generated HTML.

        Checks:
        - Has DOCTYPE declaration
        - Has <html>, <head>, <body> tags
        - Is not empty
        - Reasonable length (> 500 chars)

        Args:
            html: HTML string to validate

        Returns:
            True if valid, False otherwise
        """
        if not html or len(html) < 500:
            logger.warning("[Modernization] HTML too short or empty")
            return False

        html_lower = html.lower()

        # Check for explanation-only responses (GPT-4 talking instead of generating HTML)
        explanation_phrases = [
            'given the constraints',
            'here is how',
            'here\'s how',
            'to approach',
            'you can use',
            'i would recommend',
            'following is',
            'below is',
        ]

        first_200 = html[:200].lower()
        for phrase in explanation_phrases:
            if phrase in first_200:
                logger.warning(f"[Modernization] Response appears to be explanation text, not HTML (found '{phrase}')")
                return False

        if '<!doctype' not in html_lower:
            logger.warning("[Modernization] Missing DOCTYPE declaration")
            return False

        if '<html' not in html_lower or '</html>' not in html_lower:
            logger.warning("[Modernization] Missing <html> tags")
            return False

        if '<body' not in html_lower or '</body>' not in html_lower:
            logger.warning("[Modernization] Missing <body> tags")
            return False

        # Check that HTML actually starts near the beginning (not after lots of explanation)
        doctype_pos = html_lower.find('<!doctype')
        if doctype_pos > 100:
            logger.warning(f"[Modernization] DOCTYPE found at position {doctype_pos} - likely has explanation before HTML")
            return False

        logger.info(f"[Modernization] HTML validation passed ({len(html)} chars)")
        return True

    def _extract_improvements(self, business: Business) -> str:
        """
        Extract list of improvements made from evaluation data.

        Args:
            business: Business model

        Returns:
            String listing improvements
        """
        improvements = []

        # Based on score
        score = business.score or 50
        if score < 70:
            improvements.append("Modernized outdated design with contemporary CSS frameworks")
            improvements.append("Improved mobile responsiveness with modern breakpoints")
            improvements.append("Enhanced visual hierarchy with proper spacing and typography")

        if score < 50:
            improvements.append("Completely redesigned navigation for better UX")
            improvements.append("Applied professional color schemes and modern styling")

        # Default improvements
        if not improvements:
            improvements.append("Applied modern CSS framework for professional appearance")
            improvements.append("Enhanced typography with web fonts")
            improvements.append("Improved component styling with shadows and animations")

        return " | ".join(improvements)


def generate_modernized_templates(db: Session, business_id: str) -> List[Template]:
    """
    Convenience function to generate modernized templates.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        List of generated Template instances
    """
    service = TemplateModernizationService(db)
    return service.generate_modernized_templates(business_id)
