"""
Gemini HTML Generator Service - MAXIMUM QUALITY MODE

Generates completely new modern HTML websites using Google Gemini.
Budget: UNLIMITED - Focus on PERFECT quality!

Strategy:
1. Generate 3 variants in parallel (different design styles)
2. Use AI to validate each variant (0-100 score)
3. Select best variant
4. Refine with additional Gemini call
5. Return PERFECT result
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
import google.generativeai as genai
from datetime import datetime

from app.config import settings
from app.models import Business

logger = logging.getLogger(__name__)


class GeminiHTMLGenerator:
    """
    Generates completely new modern HTML websites using Google Gemini.

    MAXIMUM QUALITY MODE:
    - Generates 3 variants in parallel
    - Uses AI to validate each variant
    - Selects best variant
    - Refines with additional Gemini call
    - Returns PERFECT result
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Gemini API key"""
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required for HTML generation")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')
        self.model = genai.GenerativeModel(self.model_name)

        self.generation_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

    async def generate_modern_html_maximum_quality(
        self,
        business: Business,
        scraped_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate brand new modern HTML from scratch - MAXIMUM QUALITY.

        MULTI-STAGE PROCESS:
        1. Generate 3 variants in parallel (different styles)
        2. Use AI to validate each variant (0-100 score)
        3. Select best variant
        4. Refine best variant with additional Gemini call
        5. Final validation
        6. Return perfect HTML

        Args:
            business: Business model
            scraped_data: Complete scraped data with all assets

        Returns:
            Tuple of (perfect_html, generation_metadata)
        """

        logger.info(f"[GEMINI MAXIMUM QUALITY] Starting generation for: {business.name}")
        logger.info(f"[GEMINI] Budget: UNLIMITED - focusing on BEST quality!")
        logger.info(f"[GEMINI] Using model: {self.model_name}")

        # ====== STAGE 1: Generate 1 High-Quality Website ======
        logger.info("[STAGE 1] Generating 1 professional modern website...")

        # Generate single best variant
        html = await self._generate_variant(business, scraped_data, "professional-modern")

        variants = [html]

        logger.info(f"[STAGE 1] Generated website successfully ({len(html)} characters)")

        # Use the single generated website
        best_html = html
        best_style = "professional-modern"

        # ====== STAGE 2: AI Refinement ======
        logger.info("[STAGE 2] Refining website to make it PERFECT...")

        refined_html = await self._ai_refine_website(
            html=best_html,
            business_name=business.name,
            scraped_data=scraped_data
        )

        logger.info(f"[STAGE 2] Refinement complete")

        # ====== Return Results ======
        metadata = {
            "generation_method": "gemini_single_variant",
            "model": self.model_name,
            "variants_generated": 1,
            "style": best_style,
            "total_gemini_calls": self.generation_stats["total_calls"],
            "total_tokens_used": self.generation_stats["total_tokens"],
            "estimated_cost": self.generation_stats["total_cost"]
        }

        logger.info(f"[COMPLETE] Generated PERFECT website with Gemini!")
        logger.info(f"[COMPLETE] Total Gemini calls: {metadata['total_gemini_calls']}")
        logger.info(f"[COMPLETE] Total tokens: {metadata['total_tokens_used']}")
        logger.info(f"[COMPLETE] Estimated cost: ${metadata['estimated_cost']:.2f}")

        return refined_html, metadata

    async def _generate_variant(
        self,
        business: Business,
        scraped_data: Dict[str, Any],
        design_style: str
    ) -> str:
        """Generate a single variant with specific design style"""

        # Build comprehensive prompt
        prompt = self._build_comprehensive_prompt(
            business=business,
            scraped_data=scraped_data,
            design_style=design_style
        )

        # Configure generation settings
        generation_config = {
            "temperature": 0.9,  # High creativity
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 32768,  # Gemini 2.5 Pro supports up to 65K tokens!
        }

        try:
            # Call Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )

            # Track usage
            self.generation_stats["total_calls"] += 1
            if hasattr(response, 'usage_metadata'):
                total_tokens = response.usage_metadata.total_token_count
                self.generation_stats["total_tokens"] += total_tokens
                # Gemini is cheaper: ~$0.00125 per 1K tokens for Pro
                self.generation_stats["total_cost"] += (total_tokens / 1000) * 0.00125

            # Extract HTML
            html = response.text

            # Clean HTML (remove markdown code blocks if present)
            html = self._clean_html_response(html)

            logger.info(f"[VARIANT] Generated {design_style}: {len(html)} chars")

            return html

        except Exception as e:
            logger.error(f"[GEMINI ERROR] Failed to generate variant: {e}")
            raise

    async def _ai_validate_quality(self, html: str, business_name: str) -> int:
        """Use Gemini to validate HTML quality (returns 0-100 score)"""

        validation_prompt = f"""
You are a senior web design quality auditor. Score this website HTML from 0-100.

Business Name: {business_name}

HTML to validate:
{html[:8000]}

Scoring criteria (20 points each):
1. Modern Design (gradients, animations, glassmorphism) - 0-20
2. Professional Appearance (clean, polished, high-quality) - 0-20
3. Responsiveness (mobile-first, proper breakpoints) - 0-20
4. Brand Asset Usage (uses logos, colors, images properly) - 0-20
5. Code Quality (valid HTML, semantic markup, performance) - 0-20

Return ONLY a JSON object:
{{
  "modern_design": 0-20,
  "professional": 0-20,
  "responsiveness": 0-20,
  "brand_assets": 0-20,
  "code_quality": 0-20,
  "total_score": 0-100,
  "issues": ["list", "of", "issues"],
  "strengths": ["list", "of", "strengths"]
}}
"""

        generation_config = {
            "temperature": 0.3,  # Low temperature for consistent scoring
            "max_output_tokens": 1000,
        }

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                validation_prompt,
                generation_config=generation_config
            )

            # Track usage
            self.generation_stats["total_calls"] += 1
            if hasattr(response, 'usage_metadata'):
                total_tokens = response.usage_metadata.total_token_count
                self.generation_stats["total_tokens"] += total_tokens
                self.generation_stats["total_cost"] += (total_tokens / 1000) * 0.00125

            # Parse score
            result_text = response.text
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            score = result.get("total_score", 0)
            logger.info(f"[VALIDATION] Score: {score}/100 - Issues: {result.get('issues', [])}")
            return score
        except Exception as e:
            logger.error(f"[VALIDATION] Failed to parse score: {e}")
            return 50  # Default mid-score if parsing fails

    async def _ai_refine_website(
        self,
        html: str,
        business_name: str,
        scraped_data: Dict[str, Any]
    ) -> str:
        """Use Gemini to refine and perfect the HTML"""

        # Extract brand assets safely (same structure as main prompt)
        logo = scraped_data.get('logo', '')
        logos = [logo] if logo else []
        images = scraped_data.get('images', [])
        videos = scraped_data.get('videos', [])
        colors = scraped_data.get('colors', [])

        logo_path = logos[0] if logos else 'N/A'
        primary_color = colors[0] if colors else '#667eea'
        secondary_color = colors[1] if len(colors) > 1 else '#764ba2'

        # Extract ACTUAL image and video URLs from scraped data (same as generation)
        actual_image_urls = []
        for img in images:
            if isinstance(img, dict):
                url = img.get('url') or img.get('src')
                if url:
                    actual_image_urls.append(url)
            elif isinstance(img, str):
                actual_image_urls.append(img)

        actual_video_urls = []
        for vid in videos:
            if isinstance(vid, dict):
                url = vid.get('url') or vid.get('src')
                if url:
                    actual_video_urls.append(url)
            elif isinstance(vid, str):
                actual_video_urls.append(vid)

        # Build refinement prompt that avoids triggering safety filters
        # Create URL mapping (without full HTML tags to avoid safety filter)
        url_mapping = {}
        for i, url in enumerate(actual_image_urls[:20]):
            url_mapping[f"IMAGE_{i+1}"] = url

        # Format URL list as simple mapping (safer for safety filter)
        url_list_text = '\n'.join([f"{key}: Replace with {url}" for key, url in url_mapping.items()])

        refinement_prompt = f"""
CRITICAL TASK: Fix ALL <img> tags in the HTML below to use the actual website image URLs.

Current HTML:
{html}

IMAGE URL REPLACEMENTS NEEDED:
{url_list_text if url_mapping else 'No images to replace'}

INSTRUCTIONS FOR IMAGE TAGS:
1. Find ALL <img> tags in the HTML (should already exist from generation stage)
2. For each <img> tag, replace src="placeholder..." with src="[ACTUAL_URL]" from the list above
3. Ensure EVERY <img> tag has: class="w-full h-auto rounded-lg shadow-lg object-cover" loading="lazy"
4. Keep alt text descriptive
5. Keep images in their CURRENT sections (don't move them)

BRAND LOGO:
- Replace logo src with: {logo_path}
- Use class="h-12 w-auto"

ABSOLUTE REQUIREMENTS:
- HTML should ALREADY have <img> tags from Stage 1 (with placeholder src)
- Your job is to UPDATE the src attributes ONLY
- DO NOT create new text elements like "Property Placeholder 1"
- DO NOT use "https://images.unsplash.com" or "https://via.placeholder.com"
- Ensure ALL <img> tags have the correct src from the mapping above
- Add modern styling: smooth animations, hover effects, glassmorphism, gradients
- Ensure responsive design with Tailwind CSS

EXAMPLE:
BEFORE: <img src="placeholder-1.jpg" alt="Business" class="w-full">
AFTER: <img src="{actual_image_urls[0] if actual_image_urls else 'placeholder.jpg'}" alt="{business_name}" class="w-full h-auto rounded-lg shadow-lg object-cover" loading="lazy">

CRITICAL: Return ONLY complete, valid HTML with ALL closing tags:
- Must start with <!DOCTYPE html>
- Must have opening <html> and closing </html>
- Must have complete <head></head> section
- Must have complete <body></body> section
- ALL tags must be properly closed
- Return the ENTIRE HTML document, not a partial fragment

Return ONLY complete HTML from <!DOCTYPE html> to </html>. No explanations.
"""

        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 32768,  # Gemini 2.5 supports large outputs for perfection!
        }

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                refinement_prompt,
                generation_config=generation_config
            )

            # Track usage
            self.generation_stats["total_calls"] += 1
            if hasattr(response, 'usage_metadata'):
                total_tokens = response.usage_metadata.total_token_count
                self.generation_stats["total_tokens"] += total_tokens
                self.generation_stats["total_cost"] += (total_tokens / 1000) * 0.00125

            refined_html = response.text
            refined_html = self._clean_html_response(refined_html)

            logger.info(f"[REFINEMENT] Refined HTML: {len(refined_html)} chars")

            return refined_html

        except Exception as e:
            logger.error(f"[REFINEMENT ERROR] {e}")
            return html  # Return original if refinement fails

    def _clean_html_response(self, html: str) -> str:
        """Remove markdown code blocks, explanatory text, validate and clean response"""
        # Remove ```html and ``` markers
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        if html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]

        html = html.strip()

        # IMPORTANT: Remove any intro text before HTML
        # Find the actual HTML start (<!DOCTYPE or <html)
        html_lower = html.lower()
        doctype_pos = html_lower.find('<!doctype')
        html_tag_pos = html_lower.find('<html')

        # Use whichever comes first (or exists)
        start_pos = -1
        if doctype_pos >= 0 and html_tag_pos >= 0:
            start_pos = min(doctype_pos, html_tag_pos)
        elif doctype_pos >= 0:
            start_pos = doctype_pos
        elif html_tag_pos >= 0:
            start_pos = html_tag_pos

        if start_pos > 0:
            # Remove everything before the HTML
            logger.warning(f"[CLEANING] Removing {start_pos} chars of intro text before HTML")
            html = html[start_pos:]

        # Validate HTML structure
        if not self._validate_html_structure(html):
            logger.error("[GEMINI] Generated HTML is incomplete or invalid!")
            logger.error(f"[GEMINI] HTML length: {len(html)}")
            logger.error(f"[GEMINI] HTML start: {html[:200]}")
            logger.error(f"[GEMINI] HTML end: {html[-200:]}")
            raise ValueError("Gemini generated incomplete or invalid HTML")

        return html

    def _validate_html_structure(self, html: str) -> bool:
        """Validate that HTML has complete structure"""
        if not html or len(html) < 200:
            return False

        html_lower = html.lower()

        # Check for essential HTML tags
        has_doctype_or_html = '<!doctype' in html_lower or '<html' in html_lower
        has_head = '<head' in html_lower and '</head>' in html_lower
        has_body = '<body' in html_lower and '</body>' in html_lower
        has_closing_html = '</html>' in html_lower

        # HTML must have all these elements
        if not (has_doctype_or_html and has_head and has_body and has_closing_html):
            logger.warning(f"[VALIDATION] Missing elements - doctype/html: {has_doctype_or_html}, head: {has_head}, body: {has_body}, closing html: {has_closing_html}")
            return False

        return True

    def _build_comprehensive_prompt(
        self,
        business: Business,
        scraped_data: Dict[str, Any],
        design_style: str
    ) -> str:
        """
        Build ultra-detailed prompt for Gemini.

        Includes:
        - Business information
        - All scraped assets (logos, images, videos)
        - Complete content (text, headings, sections)
        - Brand colors (exact hex codes)
        - Design requirements (modern, responsive, animations)
        - Technical requirements (Tailwind CSS, HTML5)
        - Quality requirements (professional, beautiful)
        """

        # Extract data safely with defaults
        logo = scraped_data.get('logo', '')
        logos = [logo] if logo else []
        images = scraped_data.get('images', [])
        videos = scraped_data.get('videos', [])
        colors = scraped_data.get('colors', [])
        contact = scraped_data.get('contact', {})

        # Extract content
        headlines_dict = scraped_data.get('headlines', {})
        about = scraped_data.get('about', '')
        services_menu = scraped_data.get('services_menu', [])
        navigation = scraped_data.get('navigation', [])
        page_structure = scraped_data.get('page_structure', [])
        testimonials = scraped_data.get('testimonials', [])

        # Use services_menu as services, navigation as navbar
        services = services_menu
        navbar = {'links': navigation}
        headline_text = headlines_dict.get('main_headline') or headlines_dict.get('page_title') or headlines_dict.get('hero_text', '')
        hero = {'headline': headline_text, 'about': about}
        sections = page_structure
        footer = {'contact': contact}

        # Extract ACTUAL image and video URLs from scraped data
        actual_image_urls = []
        for img in images:
            if isinstance(img, dict):
                url = img.get('url') or img.get('src')
                if url:
                    actual_image_urls.append(url)
            elif isinstance(img, str):
                actual_image_urls.append(img)

        actual_video_urls = []
        for vid in videos:
            if isinstance(vid, dict):
                url = vid.get('url') or vid.get('src')
                if url:
                    actual_video_urls.append(url)
            elif isinstance(vid, str):
                actual_video_urls.append(vid)

        # Get the original scraped HTML to preserve structure
        original_html = scraped_data.get('original_html', '')

        # Build prompt to MODERNIZE existing HTML (not create from scratch)
        services_list = [s.get('name', s) if isinstance(s, dict) else s for s in services[:4]]
        navbar_links = navbar.get('links', ['Home', 'Services', 'About', 'Contact'])[:4]

        # Get page sections to understand structure
        # Extract section types from dict (sections is a list of dicts with 'type', 'heading', etc.)
        sections_info = ', '.join([s.get('type', 'section') if isinstance(s, dict) else str(s) for s in sections[:8]]) if sections else 'Standard sections'

        prompt = f"""MODERNIZE this existing website for {business.name} while PRESERVING its original structure.

Original Website Structure to Preserve:
- Page Sections: {sections_info}
- Navigation Links: {', '.join(navbar_links)}
- Services: {', '.join(services_list)}
- Number of Images: {len(actual_image_urls)} (keep in same sections as original)
- Number of Videos: {len(actual_video_urls)} (keep in same sections as original)

Brand Assets:
- Colors: {colors[0] if colors else '#6366f1'}, {colors[1] if len(colors)>1 else '#8b5cf6'}, {colors[2] if len(colors)>2 else '#f59e0b'}

CRITICAL REQUIREMENTS:
1. PRESERVE the same section structure as the original website (navbar, hero, about, services, contact, footer - whatever sections the original had)
2. Keep images in the SAME sections where they appeared originally (not in a generic "Gallery")
3. For images, use proper HTML <img> tags with placeholder src like: <img src="placeholder-1.jpg" alt="{business.name}" class="w-full h-auto rounded-lg">
4. DO NOT write text descriptions like "Property Placeholder 1" or "Image 1" - use actual <img> tags
5. Keep the same navbar structure and links
6. Keep the same footer structure
7. Keep videos in the SAME sections where they appeared originally
8. For videos, use <video> or <iframe> tags with placeholder src
9. BUT modernize with: Tailwind CSS, glassmorphism, gradients, smooth animations, responsive design
10. Use semantic HTML5, accessible markup

ABSOLUTE REQUIREMENTS FOR IMAGES:
- ALWAYS use <img src="placeholder.jpg" alt="..." class="..."> tags
- NEVER use text like "Property Placeholder 1" or div elements with text
- Images will be replaced with actual URLs in the refinement stage
- Use Tailwind classes for styling: w-full, h-auto, rounded-lg, shadow-lg, object-cover

IMPORTANT: This is a MODERNIZATION, not a redesign from scratch. The content structure must stay similar to the original.

CRITICAL OUTPUT REQUIREMENTS:
- Must start with <!DOCTYPE html>
- Must have opening <html> and closing </html>
- Must have complete <head></head> section with all meta tags, title, and Tailwind CDN
- Must have complete <body></body> section
- ALL tags must be properly closed (no missing closing tags!)
- Return the ENTIRE HTML document (complete from start to end)

Return ONLY complete, valid HTML from <!DOCTYPE html> to </html>. No explanations or markdown code blocks.
"""

        return prompt
