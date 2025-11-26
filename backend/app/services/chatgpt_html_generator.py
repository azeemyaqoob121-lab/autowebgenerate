"""
ChatGPT HTML Generator Service - MAXIMUM QUALITY MODE

Generates completely new modern HTML websites using ChatGPT.
Budget: UNLIMITED - Focus on PERFECT quality!

Strategy:
1. Generate 3 variants in parallel (different design styles)
2. Use AI to validate each variant (0-100 score)
3. Select best variant
4. Refine with additional GPT-4 call
5. Return PERFECT result
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from openai import AsyncOpenAI
from datetime import datetime

from app.config import settings
from app.models import Business

logger = logging.getLogger(__name__)


class ChatGPTHTMLGenerator:
    """
    Generates completely new modern HTML websites using ChatGPT.

    MAXIMUM QUALITY MODE:
    - Generates 3 variants in parallel
    - Uses AI to validate each variant
    - Selects best variant
    - Refines with additional GPT-4 call
    - Returns PERFECT result
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required for HTML generation")

        self.client = AsyncOpenAI(api_key=self.api_key)
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
        4. Refine best variant with additional GPT-4 call
        5. Final validation
        6. Return perfect HTML

        Args:
            business: Business model
            scraped_data: Complete scraped data with all assets

        Returns:
            Tuple of (perfect_html, generation_metadata)
        """

        logger.info(f"[MAXIMUM QUALITY] Starting generation for: {business.name}")
        logger.info(f"[MAXIMUM QUALITY] Budget: UNLIMITED - focusing on BEST quality!")

        # ====== STAGE 1: Generate 3 Variants in Parallel ======
        logger.info("[STAGE 1] Generating 3 variants in parallel...")

        design_styles = [
            "ultra-modern-gradient",      # Style 1: Vibrant gradients
            "professional-glassmorphism", # Style 2: Glassmorphism effects
            "creative-animation-heavy"    # Style 3: Heavy animations
        ]

        # Generate all 3 variants concurrently
        generation_tasks = [
            self._generate_variant(business, scraped_data, style)
            for style in design_styles
        ]

        variants = await asyncio.gather(*generation_tasks)

        logger.info(f"[STAGE 1] ✅ Generated 3 variants successfully")
        logger.info(f"[STAGE 1] Sizes: {[len(v) for v in variants]} characters")

        # ====== STAGE 2: AI Quality Validation ======
        logger.info("[STAGE 2] Using AI to validate each variant...")

        validation_tasks = [
            self._ai_validate_quality(html, business.name)
            for html in variants
        ]

        scores = await asyncio.gather(*validation_tasks)

        logger.info(f"[STAGE 2] ✅ Quality scores: {scores}")
        logger.info(f"[STAGE 2] Variant 1 (gradient): {scores[0]}/100")
        logger.info(f"[STAGE 2] Variant 2 (glass): {scores[1]}/100")
        logger.info(f"[STAGE 2] Variant 3 (animation): {scores[2]}/100")

        # ====== STAGE 3: Select Best Variant ======
        best_index = scores.index(max(scores))
        best_html = variants[best_index]
        best_score = scores[best_index]
        best_style = design_styles[best_index]

        logger.info(f"[STAGE 3] ✅ Best variant: {best_style} (score: {best_score}/100)")

        # If best score < 90, regenerate with ultra-strict prompt
        if best_score < 90:
            logger.warning(f"[STAGE 3] Score {best_score} < 90, regenerating with stricter prompt...")
            best_html = await self._generate_variant(
                business, scraped_data, "ultra-strict-maximum-quality"
            )
            best_score = await self._ai_validate_quality(best_html, business.name)
            logger.info(f"[STAGE 3] ✅ Regenerated score: {best_score}/100")

        # ====== STAGE 4: AI Refinement ======
        logger.info("[STAGE 4] Refining best variant to make it PERFECT...")

        refined_html = await self._ai_refine_website(
            html=best_html,
            business_name=business.name,
            scraped_data=scraped_data
        )

        logger.info(f"[STAGE 4] ✅ Refinement complete")

        # ====== STAGE 5: Final Validation ======
        logger.info("[STAGE 5] Final quality validation...")

        final_score = await self._ai_validate_quality(refined_html, business.name)

        logger.info(f"[STAGE 5] ✅ Final score: {final_score}/100")

        if final_score >= 95:
            logger.info("[STAGE 5] 🎉 PERFECT quality achieved!")
        elif final_score >= 90:
            logger.info("[STAGE 5] ✅ Excellent quality achieved!")
        else:
            logger.warning(f"[STAGE 5] ⚠️ Quality {final_score} below target, but proceeding")

        # ====== Return Results ======
        metadata = {
            "generation_method": "maximum_quality_multi_stage",
            "variants_generated": 3,
            "best_style": best_style,
            "best_variant_score": best_score,
            "final_score": final_score,
            "total_gpt4_calls": self.generation_stats["total_calls"],
            "total_tokens_used": self.generation_stats["total_tokens"],
            "estimated_cost": self.generation_stats["total_cost"],
            "quality_level": "PERFECT" if final_score >= 95 else "EXCELLENT" if final_score >= 90 else "GOOD"
        }

        logger.info(f"[COMPLETE] Generated PERFECT website!")
        logger.info(f"[COMPLETE] Total GPT-4 calls: {metadata['total_gpt4_calls']}")
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

        # Call ChatGPT with MAXIMUM tokens
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Best model
            messages=[
                {
                    "role": "system",
                    "content": "You are an ELITE web designer creating ultra-modern, professional websites from scratch. Generate ONLY complete HTML code - no explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,  # High creativity
            max_tokens=4096,  # Maximum for gpt-4-turbo-preview
            top_p=0.95
        )

        # Track usage
        self.generation_stats["total_calls"] += 1
        self.generation_stats["total_tokens"] += response.usage.total_tokens
        self.generation_stats["total_cost"] += (response.usage.total_tokens / 1000) * 0.01  # Rough estimate

        # Extract HTML
        html = response.choices[0].message.content

        # Clean HTML (remove markdown code blocks if present)
        html = self._clean_html_response(html)

        logger.info(f"[VARIANT] Generated {design_style}: {len(html)} chars, {response.usage.total_tokens} tokens")

        return html

    async def _ai_validate_quality(self, html: str, business_name: str) -> int:
        """Use GPT-4 to validate HTML quality (returns 0-100 score)"""

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

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a web design quality auditor. Return only valid JSON."},
                {"role": "user", "content": validation_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Low temperature for consistent scoring
            max_tokens=1000
        )

        # Track usage
        self.generation_stats["total_calls"] += 1
        self.generation_stats["total_tokens"] += response.usage.total_tokens
        self.generation_stats["total_cost"] += (response.usage.total_tokens / 1000) * 0.01

        # Parse score
        try:
            result = json.loads(response.choices[0].message.content)
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
        """Use GPT-4 to refine and perfect the HTML"""

        # Extract brand assets safely
        assets = scraped_data.get('assets', {})
        logos = assets.get('logos', [])
        colors = assets.get('colors', {})

        logo_path = logos[0].get('local_path', 'N/A') if logos else 'N/A'
        primary_color = colors.get('primary', '#667eea')
        secondary_color = colors.get('secondary', '#764ba2')

        refinement_prompt = f"""
You are an ELITE web designer perfecting an already-good website.

Business: {business_name}

Current HTML (GOOD, but make it PERFECT):
{html}

Your task: Improve this to make it ABSOLUTELY PERFECT.

Improvements to make:
1. **Animations**: Make smoother, more impressive (fade-ins, scroll animations, parallax)
2. **Typography**: Perfect font sizes, weights, spacing, hierarchy
3. **Visual Depth**: Enhance shadows, gradients, layering
4. **Responsiveness**: Perfect on mobile, tablet, desktop
5. **Micro-interactions**: Add subtle hover effects, transitions
6. **Polish**: Make it look like a $20,000 professional website
7. **Performance**: Optimize CSS, remove redundancy

Brand assets to ensure are used:
- Logo: {logo_path}
- Primary color: {primary_color}
- Secondary color: {secondary_color}

Return the PERFECTED HTML (complete document from <!DOCTYPE> to </html>):
"""

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an elite web designer perfecting websites. Return only HTML code."},
                {"role": "user", "content": refinement_prompt}
            ],
            temperature=0.7,
            max_tokens=4096  # Maximum allowed for gpt-4-turbo-preview
        )

        # Track usage
        self.generation_stats["total_calls"] += 1
        self.generation_stats["total_tokens"] += response.usage.total_tokens
        self.generation_stats["total_cost"] += (response.usage.total_tokens / 1000) * 0.01

        refined_html = response.choices[0].message.content
        refined_html = self._clean_html_response(refined_html)

        logger.info(f"[REFINEMENT] Refined HTML: {len(refined_html)} chars")

        return refined_html

    def _clean_html_response(self, html: str) -> str:
        """Remove markdown code blocks, validate and clean response"""
        # Remove ```html and ``` markers
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        if html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]

        html = html.strip()

        # Validate HTML structure
        if not self._validate_html_structure(html):
            logger.error("[CHATGPT] Generated HTML is incomplete or invalid!")
            logger.error(f"[CHATGPT] HTML length: {len(html)}")
            logger.error(f"[CHATGPT] HTML start: {html[:200]}")
            logger.error(f"[CHATGPT] HTML end: {html[-200:]}")
            raise ValueError("ChatGPT generated incomplete or invalid HTML")

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
        Build ultra-detailed prompt for ChatGPT.

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
        # Handle actual scraper data structure (not nested under assets/content)
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
        # Headlines is a dict with keys: page_title, main_headline, meta_description, hero_text
        headline_text = headlines_dict.get('main_headline') or headlines_dict.get('page_title') or headlines_dict.get('hero_text', '')
        hero = {'headline': headline_text, 'about': about}
        sections = page_structure
        footer = {'contact': contact}

        # Build ultra-detailed prompt for PERFECT results
        prompt = f"""
You are an ELITE web designer (10+ years experience) creating a STUNNING modern website from scratch.

## BUSINESS INFORMATION:
Business Name: **{business.name}**
Industry: {business.category or 'Professional Services'}
Description: {business.description or 'Modern professional business'}

## BRAND ASSETS TO USE:
Logo URL: {logos[0] if logos else 'Use text logo'}
Brand Colors (USE THESE EXACT COLORS):
  - Primary: {colors[0] if len(colors) > 0 else '#6366f1'}
  - Secondary: {colors[1] if len(colors) > 1 else '#8b5cf6'}
  - Accent: {colors[2] if len(colors) > 2 else '#ec4899'}
  - Additional: {', '.join(colors[3:6]) if len(colors) > 3 else 'Modern gradients'}

Images Available: {len(images)} high-quality images
Videos Available: {len(videos)} videos

## ACTUAL BUSINESS CONTENT (USE THIS):
Navigation Menu: {json.dumps(navbar.get('links', ['Home', 'Services', 'About', 'Contact'])[:6])}
Main Headline: {hero.get('headline', business.name) or business.name}
About Text: {hero.get('about', business.description)[:500] if hero.get('about') else business.description}
Services/Offerings: {json.dumps([s.get('name', s) for s in services[:6]])}
Customer Reviews: {json.dumps([t.get('text', '')[:200] for t in testimonials[:3]]) if testimonials else 'Professional service, highly recommended!'}
Contact Info: {json.dumps(contact)}

## DESIGN STYLE: {design_style.upper()}
Create an ULTRA-MODERN, PROFESSIONAL website with PERFECT alignment and spacing.

## CRITICAL REQUIREMENTS (MUST FOLLOW):

### 1. TECHNICAL SETUP:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business.name} - Professional {business.category or 'Services'}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
</head>
```

### 2. LAYOUT STRUCTURE (EXACT ORDER):
1. **HEADER/NAVBAR** - Sticky, glassmorphism, backdrop-blur
   - Logo on left
   - Navigation links center/right
   - CTA button on far right
   - Shadow on scroll

2. **HERO SECTION** - Full viewport height, gradient background
   - Large headline (text-5xl to text-7xl)
   - Compelling subheadline (text-xl)
   - 2 CTA buttons (primary + secondary)
   - Hero image/illustration on right (for desktop)
   - Background gradient using brand colors

3. **FEATURES/BENEFITS** - 3-column grid on desktop, 1-col mobile
   - Icons for each feature
   - Short heading + description
   - Hover effects (lift, glow)

4. **SERVICES SECTION** - 2 or 3-column grid
   - Service cards with icons
   - Service name + description
   - "Learn More" links
   - Gradient borders or shadows

5. **ABOUT SECTION** - 2-column layout
   - Company story/mission (left column)
   - Image or stats (right column)
   - Professional, trust-building tone

6. **TESTIMONIALS** - Carousel or 3-column grid
   - Customer quote
   - Customer name + role/company
   - Star ratings (5 stars)
   - Subtle card backgrounds

7. **CTA SECTION** - Full-width, gradient background
   - Bold call-to-action
   - Large CTA button
   - Urgency/value proposition

8. **CONTACT SECTION** - 2-column layout
   - Contact form (left): Name, Email, Message fields
   - Contact info (right): Phone, Email, Address
   - Modern form styling with focus states

9. **FOOTER** - Dark background (#1f2937 or darker)
   - Company info + logo
   - Quick links
   - Social media icons
   - Copyright notice

### 3. STYLING REQUIREMENTS (BE SPECIFIC):

**Colors:**
- Use provided brand colors for gradients, buttons, accents
- Gradient backgrounds: `bg-gradient-to-r from-[{colors[0] if colors else '#6366f1'}] to-[{colors[1] if len(colors) > 1 else '#8b5cf6'}]`
- Dark sections: bg-gray-900, bg-gray-800
- Light sections: bg-white, bg-gray-50

**Typography:**
- Font family: 'Inter', sans-serif (already loaded)
- Headings: font-bold, text-4xl to text-6xl, tracking-tight
- Body text: text-gray-600, leading-relaxed
- Line heights: Use leading-tight for headings, leading-relaxed for body

**Spacing:**
- Section padding: py-20 lg:py-32 (large vertical space)
- Container: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
- Grid gaps: gap-8 lg:gap-12
- Perfect whitespace everywhere

**Effects:**
- Smooth transitions: transition-all duration-300 ease-in-out
- Hover effects: hover:scale-105, hover:shadow-2xl
- Glassmorphism: backdrop-blur-lg bg-white/80
- Shadows: shadow-xl, shadow-2xl for depth
- Rounded corners: rounded-2xl, rounded-3xl

**Buttons:**
- Primary: bg-[brand-color] text-white px-8 py-4 rounded-full font-semibold hover:scale-105 shadow-lg
- Secondary: border-2 border-[brand-color] text-[brand-color] px-8 py-4 rounded-full hover:bg-[brand-color] hover:text-white

**Cards:**
- Background: bg-white
- Border: border border-gray-200 or gradient border
- Shadow: shadow-lg hover:shadow-2xl
- Padding: p-8
- Rounded: rounded-2xl
- Hover lift: hover:-translate-y-2

### 4. RESPONSIVENESS (MANDATORY):
- Mobile-first approach
- Breakpoints: sm:, md:, lg:, xl:
- Grid columns: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
- Hide/show elements: hidden lg:block
- Text sizes: text-4xl lg:text-6xl
- Padding adjustments: py-12 lg:py-20

### 5. ANIMATIONS (INCLUDE THIS <style> TAG):
```css
<style>
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes float {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-20px); }}
}}
.animate-fadeInUp {{
    animation: fadeInUp 0.8s ease-out forwards;
}}
.animate-float {{
    animation: float 3s ease-in-out infinite;
}}
.gradient-text {{
    background: linear-gradient(135deg, {colors[0] if colors else '#6366f1'}, {colors[1] if len(colors) > 1 else '#8b5cf6'});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
</style>
```

### 6. QUALITY CHECKLIST (ENSURE ALL):
✅ PERFECT alignment (everything lines up pixel-perfect)
✅ Consistent spacing (use Tailwind spacing scale)
✅ Professional typography hierarchy
✅ Smooth hover/transition effects
✅ Mobile responsive (test all breakpoints)
✅ Fast loading (inline CSS, optimized)
✅ Brand colors used throughout
✅ Actual business content (not lorem ipsum)
✅ Call-to-action buttons prominent
✅ Trust signals (testimonials, stats)

### 7. FINAL NOTES:
- Make it look like a $20,000 professional website
- Better than 99% of websites online
- Modern 2024 design trends (gradients, glassmorphism, smooth animations)
- ZERO layout issues - everything perfectly aligned
- Professional, polished, premium quality

Generate the COMPLETE, PERFECT HTML now (<!DOCTYPE html> to </html>):
"""

        return prompt
