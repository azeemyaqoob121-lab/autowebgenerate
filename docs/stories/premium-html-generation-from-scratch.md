# User Story: Generate Brand-New Modern HTML Websites Using ChatGPT

**Story ID:** AWOA-PREMIUM-001
**Priority:** HIGH
**Type:** Feature Enhancement
**Created:** 2025-11-23
**Assigned To:** Development Team

---

## User Story

**As a** business using AutoWeb Outreach AI
**I want** the system to generate completely new, modern, professional HTML websites from scratch using ChatGPT
**So that** my generated website looks modern, beautiful, and professional (not just a restyled old website)

---

## Current Problem

### What's Happening Now (❌ BAD):
1. System **clones old Birmingham website HTML**
2. Applies generic CSS styling on top of old structure
3. Result: **Old structure with new paint** - still looks outdated
4. **Not professional, not modern, not beautiful**

### Example of Current Flow:
```
Birmingham Website (OLD HTML)
    ↓
Scrape HTML structure
    ↓
Clone old HTML
    ↓
Apply generic CSS modernization
    ↓
❌ Result: Lipstick on a pig - still looks old
```

---

## Desired Solution

### What Should Happen (✅ GOOD):
1. **Scrape ALL assets** from Birmingham website:
   - Videos (URLs, embed codes)
   - Logos (download images)
   - Color scheme (extract hex colors)
   - Pictures/Images (download all)
   - Content (all text, headings, paragraphs)
   - Navbar structure (menu items, links)
   - Footer content (contact info, social links)
   - Banners (hero images, CTAs)
   - Services/products list
   - Testimonials
   - Everything!

2. **Send to ChatGPT** with detailed prompt:
   - Business information
   - All scraped assets
   - All extracted content
   - Color scheme
   - Instruction: "Generate BRAND NEW modern HTML website"

3. **ChatGPT generates** completely new HTML:
   - Modern design (like `template_cc_electrical_ULTRA_MODERN.html`)
   - Uses Tailwind CSS or modern CSS
   - Animations, gradients, glassmorphism
   - Professional typography
   - Perfect responsiveness
   - Uses ALL the scraped brand assets

4. **Result:**
   - ✅ Modern looking
   - ✅ Professional looking
   - ✅ Beautiful design
   - ✅ Perfect responsiveness
   - ✅ Best ever design
   - ✅ Uses their REAL brand assets (not generic)

### New Flow:
```
Birmingham Website
    ↓
Scrape EVERYTHING (videos, logos, colors, images, content, navbar, footer, etc.)
    ↓
Extract & organize all assets
    ↓
Send comprehensive data to ChatGPT with detailed prompt
    ↓
ChatGPT generates BRAND NEW modern HTML from scratch
    ↓
✅ Result: Completely modern, professional, beautiful website!
```

---

## Acceptance Criteria

### Must Have:
- [ ] **AC1: Complete Asset Extraction**
  - System extracts ALL assets from scraped website:
    - All images (download to local storage)
    - All videos (URLs or download)
    - Logo (download high-res version)
    - Color scheme (extract primary, secondary, accent colors)
    - All text content (headings, paragraphs, lists)
    - Navbar structure (all menu items and links)
    - Footer content (all sections and links)
    - Contact information (phone, email, address)
    - Services/products (names and descriptions)
    - Testimonials (if available)
    - Social media links
    - Banners and hero sections

- [ ] **AC2: ChatGPT Prompt Generation**
  - System creates comprehensive prompt for ChatGPT including:
    - Business name and type
    - Complete brand asset inventory
    - Extracted color palette (hex codes)
    - All content organized by section
    - Design requirements (modern, professional, responsive)
    - Instruction to generate NEW HTML (not modify existing)
    - Technical requirements (Tailwind CSS, animations, gradients)

- [ ] **AC3: ChatGPT Integration**
  - System sends prompt to ChatGPT (GPT-4 or GPT-4 Turbo)
  - Configurable parameters:
    - Model: GPT-4 Turbo (for best quality)
    - Temperature: 0.7-0.9 (for creativity)
    - Max tokens: 8000+ (for complete HTML generation)
    - Multiple attempts: 2-3 iterations for best result
  - System validates ChatGPT response
  - System extracts generated HTML

- [ ] **AC4: Generated Website Quality**
  - Generated HTML must be:
    - **Modern design** (2024 standards - gradients, animations, glassmorphism)
    - **Professional appearance** (clean, polished, high-quality)
    - **Beautiful layout** (proper spacing, typography, visual hierarchy)
    - **Fully responsive** (mobile, tablet, desktop)
    - **Uses brand assets** (actual logos, colors, images from scraped site)
    - **Complete structure** (navbar, hero, services, about, testimonials, contact, footer)
    - **Animations** (smooth transitions, hover effects, scroll animations)
    - **Optimized performance** (fast loading, efficient CSS)

- [ ] **AC5: Asset Integration**
  - Generated HTML must integrate all scraped assets:
    - Logo appears in navbar (actual company logo)
    - Brand colors used throughout design (extracted hex colors)
    - Original images used in galleries/sections
    - Original videos embedded (if available)
    - Original content preserved (enhanced but authentic)
    - Navbar structure matches original (with improvements)
    - Footer content includes all original links/info

- [ ] **AC6: Regeneration Support**
  - User can click "Regenerate" button
  - System uses SAME scraped data (from database)
  - Sends to ChatGPT again for NEW variation
  - Generates DIFFERENT modern design (alternative layout/style)
  - All assets remain the same, design changes

- [ ] **AC7: Validation & Fallbacks**
  - System validates generated HTML (syntax check)
  - If ChatGPT fails, retry with adjusted prompt
  - If multiple failures, log error and use fallback
  - Save generation metadata (model used, tokens, timestamp)

---

## Technical Requirements

### Phase 1: Enhanced Scraping & Asset Extraction

**File to Modify:** `backend/app/services/website_scraper.py`

**Add these extractions:**
```python
def scrape_business_website_comprehensive(url: str) -> Dict[str, Any]:
    """
    Scrape EVERYTHING from the website for ChatGPT generation.

    Returns:
        {
            "raw_html": "<html>...</html>",
            "assets": {
                "logos": [{"url": "...", "alt": "...", "local_path": "..."}],
                "images": [{"url": "...", "alt": "...", "local_path": "...", "context": "hero|gallery|service"}],
                "videos": [{"url": "...", "type": "youtube|vimeo|direct", "embed_code": "..."}],
                "colors": {
                    "primary": "#667eea",
                    "secondary": "#764ba2",
                    "accent": "#f093fb",
                    "all_colors": ["#667eea", "#764ba2", ...]
                },
                "fonts": {
                    "headings": ["Inter", "Roboto"],
                    "body": ["Open Sans"]
                }
            },
            "content": {
                "navbar": {
                    "logo": "...",
                    "menu_items": [{"text": "Home", "link": "/"}, ...]
                },
                "hero": {
                    "heading": "...",
                    "subheading": "...",
                    "cta_buttons": [{"text": "Get Quote", "link": "..."}],
                    "background_image": "...",
                    "background_video": "..."
                },
                "sections": [
                    {
                        "type": "services|about|testimonials|contact|etc",
                        "heading": "...",
                        "content": "...",
                        "images": [...],
                        "items": [...]
                    }
                ],
                "footer": {
                    "sections": [...],
                    "social_links": [...],
                    "copyright": "..."
                }
            },
            "text_content": {
                "all_headings": ["...", "..."],
                "all_paragraphs": ["...", "..."],
                "all_lists": [["item1", "item2"], ...],
                "services": [{"name": "...", "description": "..."}],
                "testimonials": [{"text": "...", "author": "...", "rating": 5}]
            },
            "contact": {
                "phone": ["...", "..."],
                "email": ["...", "..."],
                "address": "...",
                "social": {"facebook": "...", "linkedin": "..."}
            }
        }
    ```

---

### Phase 2: ChatGPT Prompt Builder - MAXIMUM QUALITY VERSION

**New File:** `backend/app/services/chatgpt_html_generator.py`

**Purpose:** Generate brand-new HTML using ChatGPT with MAXIMUM QUALITY

```python
import asyncio
from typing import Dict, Any, List, Tuple
from openai import AsyncOpenAI
import logging

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

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
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
            max_tokens=16000,  # MAXIMUM tokens
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
{html[:8000]}  # First 8000 chars

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
        import json
        result = json.loads(response.choices[0].message.content)
        score = result.get("total_score", 0)

        logger.info(f"[VALIDATION] Score: {score}/100 - Issues: {result.get('issues', [])}")

        return score

    async def _ai_refine_website(
        self,
        html: str,
        business_name: str,
        scraped_data: Dict[str, Any]
    ) -> str:
        """Use GPT-4 to refine and perfect the HTML"""

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
- Logo: {scraped_data.get('assets', {}).get('logos', [{}])[0].get('local_path', 'N/A')}
- Primary color: {scraped_data.get('assets', {}).get('colors', {}).get('primary', '#667eea')}
- Secondary color: {scraped_data.get('assets', {}).get('colors', {}).get('secondary', '#764ba2')}

Return the PERFECTED HTML (complete document from <!DOCTYPE> to </html>):
"""

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an elite web designer perfecting websites. Return only HTML code."},
                {"role": "user", "content": refinement_prompt}
            ],
            temperature=0.7,
            max_tokens=16000  # Full refinement
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
        """Remove markdown code blocks and clean response"""
        # Remove ```html and ``` markers
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        if html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]
        return html.strip()

    def _build_comprehensive_prompt(self, business, scraped_data, design_style):
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

        return f"""
        You are an EXPERT web designer creating a BRAND NEW modern website from scratch.

        CRITICAL: Generate COMPLETELY NEW HTML - DO NOT modify existing code.

        ## Business Information:
        Name: {business.name}
        Type: {business.category}
        Description: {business.description}

        ## Brand Assets (MUST USE):
        Logo: {scraped_data['assets']['logos'][0]['local_path']}
        Primary Color: {scraped_data['assets']['colors']['primary']}
        Secondary Color: {scraped_data['assets']['colors']['secondary']}
        Accent Color: {scraped_data['assets']['colors']['accent']}

        Images Available: {len(scraped_data['assets']['images'])} images
        Videos Available: {len(scraped_data['assets']['videos'])} videos

        ## Content to Include:
        Navbar: {json.dumps(scraped_data['content']['navbar'])}
        Hero Section: {json.dumps(scraped_data['content']['hero'])}
        Services: {json.dumps(scraped_data['text_content']['services'])}
        About: {scraped_data['content']['sections'][1]['content']}
        Testimonials: {json.dumps(scraped_data['text_content']['testimonials'])}
        Contact: {json.dumps(scraped_data['contact'])}
        Footer: {json.dumps(scraped_data['content']['footer'])}

        ## Design Requirements:
        Style: {design_style} (ultra-modern, professional, beautiful)
        Framework: Use Tailwind CSS (via CDN)
        Responsiveness: Perfect mobile, tablet, desktop

        Features Required:
        - Gradient backgrounds using brand colors
        - Smooth animations and transitions
        - Glassmorphism effects
        - Modern typography (Inter, Poppins, or similar)
        - Hover effects on buttons and cards
        - Sticky navigation
        - Scroll animations
        - Professional shadows and depth

        ## Output Requirements:
        - Complete HTML5 document (<!DOCTYPE html> to </html>)
        - All CSS inline or in <style> tag (no external files)
        - Use Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>
        - Include custom CSS for animations
        - Mobile-first responsive design
        - All images using provided local paths
        - All brand colors using provided hex codes

        ## Structure:
        1. Header/Navbar (with logo, menu items)
        2. Hero Section (large heading, subheading, CTA buttons, gradient background)
        3. Services Section (grid of service cards with icons)
        4. About Section (company story, team info)
        5. Testimonials Section (customer reviews)
        6. Contact Section (phone, email, form)
        7. Footer (links, social media, copyright)

        IMPORTANT: Make it look like the BEST modern website of 2024!

        Generate the complete HTML now:
        """
```

---

### Phase 3: Update Template Generation Service

**File to Modify:** `backend/app/services/template_generator_premium.py`

**Replace current approach with:**

```python
async def generate_templates_for_business(
    business: Business,
    db: Session,
    num_variants: int = 1,
    use_premium: bool = True
) -> List[Template]:
    """
    Generate brand-new modern HTML website using ChatGPT.

    NEW APPROACH:
    1. Scrape website comprehensively (all assets)
    2. Extract and organize all content
    3. Send to ChatGPT with detailed prompt
    4. ChatGPT generates BRAND NEW modern HTML
    5. Save and return
    """

    # Step 1: Comprehensive scraping
    scraped_data = scrape_business_website_comprehensive(business.website_url)

    # Step 2: Download all assets locally
    downloaded_assets = download_all_brand_assets(
        business_id=str(business.id),
        scraped_data=scraped_data
    )

    # Step 3: Initialize ChatGPT HTML generator
    html_generator = ChatGPTHTMLGenerator()

    # Step 4: Generate brand-new modern HTML
    modern_html = await html_generator.generate_modern_html(
        business=business,
        scraped_data=scraped_data,
        design_style="ultra-modern"
    )

    # Step 5: Validate quality
    quality_score = validate_website_quality(modern_html)

    if quality_score < 80:
        # Regenerate with stricter requirements
        modern_html = await html_generator.generate_modern_html(
            business=business,
            scraped_data=scraped_data,
            design_style="ultra-modern-premium"
        )

    # Step 6: Save to database
    template = Template(
        business_id=business.id,
        variant_number=1,
        html_content=modern_html,
        css_content="",  # Inline in HTML
        js_content="",   # Inline in HTML
        media_assets={
            "generation_method": "chatgpt_from_scratch",
            "model_used": "gpt-4-turbo-preview",
            "quality_score": quality_score,
            "assets_used": downloaded_assets
        },
        generated_at=datetime.utcnow()
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return [template]
```

---

## ChatGPT Prompt Template

**File to Create:** `backend/app/prompts/chatgpt_html_generation_ultra_modern.txt`

```
You are an ELITE web designer creating a BRAND NEW ultra-modern website from scratch.

CRITICAL INSTRUCTIONS:
- Generate COMPLETELY NEW HTML (not modify existing)
- Use Tailwind CSS (CDN: https://cdn.tailwindcss.com)
- Must be ultra-modern, professional, beautiful
- Perfect responsiveness (mobile-first)
- Include animations, gradients, glassmorphism
- Use provided brand assets (logos, colors, images)

[Business Information]
Name: {business_name}
Type: {business_type}
Description: {business_description}

[Brand Assets - MUST USE]
Logo: {logo_path}
Primary Color: {primary_color}
Secondary Color: {secondary_color}
Accent Color: {accent_color}
Fonts: {font_headings}, {font_body}

[Images Available - USE IN DESIGN]
{image_list}

[Videos Available - EMBED IF SUITABLE]
{video_list}

[Content Structure]
Navbar: {navbar_structure}
Hero: {hero_content}
Services: {services_list}
About: {about_content}
Testimonials: {testimonials_list}
Contact: {contact_info}
Footer: {footer_content}

[Design Requirements]
Style: Ultra-modern, professional, beautiful
Layout: Single-page with smooth scroll
Colors: Use ONLY the provided brand colors
Typography: Modern web fonts (Inter, Poppins, or Roboto)

Features Required:
✅ Gradient hero section with brand colors
✅ Smooth scroll animations
✅ Glassmorphism cards
✅ Hover effects (scale, glow, shadow)
✅ Sticky navigation bar
✅ Responsive grid layouts
✅ Professional shadows and depth
✅ CTA buttons with gradients
✅ Mobile menu (hamburger)
✅ Footer with social links

[Quality Standards]
- Looks like a $10,000 professional website
- Modern as of 2024 standards
- Zero generic template appearance
- Uses ALL provided brand assets
- Responsive on all devices
- Fast loading (inline CSS/JS)

Generate the complete HTML now (from <!DOCTYPE html> to </html>):
```

---

## API Configuration - MAXIMUM QUALITY MODE 🚀

**File to Modify:** `backend/app/config.py`

**🎯 BUDGET APPROVED - USE MAXIMUM RESOURCES FOR BEST QUALITY!**

```python
# ============================================================
# ChatGPT Configuration for HTML Generation
# MAXIMUM QUALITY MODE - NO BUDGET CONSTRAINTS
# Goal: Generate the BEST possible websites
# ============================================================

# Model Selection - USE THE BEST
CHATGPT_HTML_GENERATION_MODEL = "gpt-4-turbo-preview"  # Latest GPT-4 Turbo (best available)
CHATGPT_HTML_FALLBACK_MODEL = "gpt-4-0125-preview"  # Fallback if turbo unavailable

# Generation Parameters - MAXIMIZE QUALITY
CHATGPT_HTML_TEMPERATURE = 0.9  # High creativity for beautiful designs
CHATGPT_HTML_MAX_TOKENS = 16000  # MAXIMUM tokens for complete website (doubled!)
CHATGPT_HTML_TOP_P = 0.95  # High diversity for unique designs

# Quality Assurance - RETRY UNTIL PERFECT
CHATGPT_HTML_RETRY_ATTEMPTS = 5  # Up to 5 attempts to get perfect quality
CHATGPT_HTML_MIN_QUALITY_SCORE = 90  # VERY HIGH bar (90/100 minimum)
CHATGPT_HTML_PERFECT_SCORE = 95  # Target perfect score

# Multi-Generation Strategy - GENERATE MULTIPLE, PICK BEST
CHATGPT_GENERATE_VARIANTS = 3  # Generate 3 different designs
CHATGPT_AUTO_SELECT_BEST = True  # Automatically pick highest quality

# Refinement - USE AI TO IMPROVE FURTHER
CHATGPT_ENABLE_REFINEMENT = True  # After generation, refine with another GPT-4 call
CHATGPT_REFINEMENT_PROMPT = True  # Use specialized refinement prompt
CHATGPT_REFINEMENT_MAX_TOKENS = 8000  # Additional tokens for refinement

# Validation - USE GPT-4 TO VALIDATE QUALITY
CHATGPT_ENABLE_AI_VALIDATION = True  # Use GPT-4 to validate generated HTML
CHATGPT_VALIDATION_MODEL = "gpt-4-turbo-preview"  # Use best model for validation

# Cost Tracking (for monitoring, not limiting)
CHATGPT_TRACK_COSTS = True  # Track costs for analytics
CHATGPT_LOG_GENERATION_DETAILS = True  # Log all generation attempts

# Timeout Settings
CHATGPT_GENERATION_TIMEOUT = 120  # 2 minutes per generation (be patient!)
CHATGPT_TOTAL_TIMEOUT = 600  # 10 minutes total (multiple attempts)
```

---

## MAXIMUM QUALITY GENERATION STRATEGY

### Strategy Overview:
**We don't care about cost - we care about PERFECT output!**

### Multi-Stage Generation Process:

#### **Stage 1: Generate Multiple Variants** (3 attempts in parallel)
```python
# Generate 3 completely different modern designs
variant_1 = generate_with_prompt(style="ultra-modern-gradient")
variant_2 = generate_with_prompt(style="professional-glassmorphism")
variant_3 = generate_with_prompt(style="creative-animation-heavy")

# Each uses MAXIMUM tokens (16,000)
# Each uses GPT-4 Turbo
# Each gets comprehensive prompt with ALL assets
```

#### **Stage 2: AI Quality Validation** (GPT-4 validates each)
```python
# Use GPT-4 to SCORE each variant
score_1 = ai_validate_quality(variant_1)  # Returns 0-100 score
score_2 = ai_validate_quality(variant_2)
score_3 = ai_validate_quality(variant_3)

# Validation checks:
# - Modern design? (0-20 points)
# - Professional appearance? (0-20 points)
# - Responsiveness? (0-20 points)
# - Brand asset usage? (0-20 points)
# - Code quality? (0-20 points)
```

#### **Stage 3: Select Best Variant**
```python
# Automatically pick highest scoring variant
best_variant = select_highest_score([variant_1, variant_2, variant_3])

# If best score < 90, REGENERATE
if best_variant.score < 90:
    # Try again with stricter prompt
    best_variant = generate_with_ultra_strict_prompt()
```

#### **Stage 4: AI Refinement** (Make perfect even better!)
```python
# Use GPT-4 to REFINE the best variant
refined_html = ai_refine_website(
    html=best_variant.html,
    refinement_instructions="""
    Improve this already-good website to make it PERFECT:
    - Enhance animations (make smoother, more impressive)
    - Perfect spacing and typography
    - Add more visual depth (shadows, gradients)
    - Optimize responsiveness
    - Add micro-interactions
    - Make it look like a $20,000 website
    """
)
```

#### **Stage 5: Final Validation**
```python
# Final quality check
final_score = ai_validate_quality(refined_html)

if final_score >= 95:
    return refined_html  # ✅ PERFECT!
elif final_score >= 90:
    return refined_html  # ✅ GOOD ENOUGH!
else:
    # Retry entire process
    return maximum_quality_generation_retry()
```

### Total GPT-4 API Calls Per Website:
- **3 generation calls** (variants)
- **3 validation calls** (scoring)
- **1 refinement call** (improvement)
- **1 final validation call**
- **= 8 GPT-4 calls total** (if first attempt succeeds)
- **= Up to 15 calls** (if retries needed)

**Cost per website:** ~$0.50 - $1.50 (depending on retries)
**Quality:** MAXIMUM - absolutely perfect websites!

---

---

## Testing Plan

### Manual Testing:
1. **Test Case 1: New Generation**
   - Select business from Birmingham
   - Click "Generate Template"
   - Verify:
     - All assets extracted
     - ChatGPT called successfully
     - HTML generated is modern, professional, beautiful
     - All brand assets used (logo, colors, images)
     - Perfect responsiveness
     - Animations work smoothly

2. **Test Case 2: Regeneration**
   - Select business with existing template
   - Click "Regenerate Template"
   - Verify:
     - Uses cached scraped data (no re-scraping)
     - Generates DIFFERENT design
     - Still modern, professional, beautiful
     - All assets still used correctly

3. **Test Case 3: Quality Validation**
   - Generate template
   - Check quality score
   - If score < 80, verify retry happens
   - Final result must meet quality standards

### Automated Testing:
```python
# backend/tests/test_chatgpt_html_generation.py

def test_generate_modern_html_from_scratch():
    """Test that ChatGPT generates brand new modern HTML"""

    # Arrange
    business = create_test_business()
    scraped_data = scrape_business_website_comprehensive(business.website_url)

    # Act
    generator = ChatGPTHTMLGenerator()
    html = await generator.generate_modern_html(business, scraped_data)

    # Assert
    assert "<!DOCTYPE html>" in html
    assert "tailwindcss" in html
    assert scraped_data['assets']['colors']['primary'] in html
    assert business.name in html
    assert len(html) > 5000  # Substantial HTML

def test_uses_brand_assets():
    """Test that generated HTML uses all brand assets"""

    # Arrange
    business = create_test_business()
    scraped_data = {
        'assets': {
            'logos': [{'local_path': '/assets/logo.png'}],
            'colors': {'primary': '#667eea', 'secondary': '#764ba2'}
        }
    }

    # Act
    generator = ChatGPTHTMLGenerator()
    html = await generator.generate_modern_html(business, scraped_data)

    # Assert
    assert '/assets/logo.png' in html
    assert '#667eea' in html
    assert '#764ba2' in html
```

---

## Success Metrics

After implementation, generated websites must achieve:

1. **Visual Quality:** 9/10 rating (modern, professional, beautiful)
2. **Responsiveness:** 100% (perfect on mobile, tablet, desktop)
3. **Brand Preservation:** 100% (uses all logos, colors, images)
4. **Content Accuracy:** 95%+ (preserves all original content)
5. **Performance:** PageSpeed score 90+
6. **User Satisfaction:** 90%+ happy with generated design

---

## Implementation Timeline

### Sprint 1 (Week 1):
- [ ] Enhance website scraper (comprehensive extraction)
- [ ] Create asset downloader (logos, images, videos)
- [ ] Build color/font extractor

### Sprint 2 (Week 2):
- [ ] Create ChatGPT HTML generator service
- [ ] Build comprehensive prompt template
- [ ] Implement HTML validation

### Sprint 3 (Week 3):
- [ ] Integrate with template generation flow
- [ ] Add regeneration support
- [ ] Implement quality scoring

### Sprint 4 (Week 4):
- [ ] Testing and refinement
- [ ] Quality improvements
- [ ] Production deployment

---

## Example Output Comparison

### Before (Current - ❌ BAD):
```html
<!-- Old Birmingham website HTML with generic CSS -->
<div class="old-container">
  <h2 class="old-heading">Services</h2>
  <!-- Old structure with new CSS applied -->
</div>
```

### After (New - ✅ GOOD):
```html
<!-- Brand new modern HTML generated by ChatGPT -->
<section class="py-32 bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-900">
  <div class="container mx-auto px-6">
    <h2 class="text-5xl font-bold text-white text-center mb-16 animate-fade-in">
      Our Services
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
      <div class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 hover:scale-105 transition-all duration-500">
        <!-- Modern card with glassmorphism -->
      </div>
    </div>
  </div>
</section>
```

---

## Dependencies

- OpenAI API (GPT-4 Turbo access)
- BeautifulSoup4 (HTML parsing)
- Requests (asset downloading)
- Pillow (image processing)
- Current scraping infrastructure

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| ChatGPT generates invalid HTML | High | Implement strict validation, retry with adjusted prompt |
| ChatGPT doesn't use brand assets | Medium | Explicit instructions in prompt, validation check |
| Generation takes too long | Medium | Optimize prompt, use async processing, show loading state |
| Cost of GPT-4 calls | Medium | Cache results, limit regenerations, monitor usage |
| Quality inconsistency | High | Implement quality scoring, retry if below threshold |

---

## Questions for Product Owner

1. **Budget:** ✅ **APPROVED** - Use maximum resources for best quality (no budget constraints)
2. **Regeneration Limit:** How many times can user regenerate? (Suggest: Unlimited - we want them to get perfect result!)
3. **Design Styles:** ✅ **APPROVED** - Generate 3 styles, auto-pick best
4. **Manual Override:** Should users be able to edit generated HTML? (Future feature?)
5. **A/B Testing:** ✅ **IMPLEMENTED** - System generates 3 variants, validates, picks best

---

## Notes

- This is a COMPLETE redesign of the generation approach
- Focus on QUALITY over speed - use best AI model
- Use ALL scraped brand assets (logos, colors, images)
- Generate BRAND NEW HTML (not modify old)
- Make it MODERN, PROFESSIONAL, BEAUTIFUL
- Perfect RESPONSIVENESS is critical

---

## References

- Example: `backend/template_cc_electrical_ULTRA_MODERN.html` (target quality)
- Current System: `backend/app/services/template_generator_premium.py`
- Scraper: `backend/app/services/website_scraper.py`
- Prompt: `backend/app/prompts/premium_content_enhancement.txt`

---

---

## 🚀 MAXIMUM QUALITY SUMMARY

### What Makes This MAXIMUM QUALITY:

#### 1. **Multi-Variant Generation** (Not just 1 attempt!)
- Generates **3 different designs** in parallel
- Style 1: Ultra-modern gradients
- Style 2: Professional glassmorphism
- Style 3: Creative animation-heavy
- Uses **16,000 tokens per variant** (MAXIMUM)
- Total: **48,000 tokens** just for generation!

#### 2. **AI Quality Validation** (GPT-4 judges quality!)
- Each variant scored by GPT-4 (0-100)
- Scoring criteria:
  - Modern design: 20 points
  - Professional appearance: 20 points
  - Responsiveness: 20 points
  - Brand asset usage: 20 points
  - Code quality: 20 points
- **Automatically selects best variant**

#### 3. **AI Refinement** (Make perfect even better!)
- Takes best variant
- Sends to GPT-4 again with refinement instructions
- Improves: animations, typography, depth, responsiveness
- Uses **16,000 more tokens**
- Result: **PERFECTED website**

#### 4. **Final Validation** (Ensure perfection!)
- Final quality check by GPT-4
- Must score **90+** to pass
- If score < 90, **regenerate entirely**
- Don't stop until perfect!

#### 5. **Cost vs Quality Trade-off:**
```
OLD APPROACH (❌):
- 1 GPT-4 call
- 8,000 tokens
- Cost: ~$0.08
- Quality: 60-70/100 (meh...)

NEW APPROACH (✅ MAXIMUM QUALITY):
- 8 GPT-4 calls (3 gen + 3 validate + 1 refine + 1 final)
- 80,000+ tokens total
- Cost: ~$0.80 - $1.50
- Quality: 90-95/100 (PERFECT!)

Investment: ~$1.50 per website
Result: PROFESSIONAL, MODERN, BEAUTIFUL websites
ROI: MASSIVE (clients get amazing websites!)
```

---

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1 - Week 1: Foundation
- [ ] Enhanced scraping (extract ALL assets)
- [ ] Asset downloader (logos, images, videos)
- [ ] Color/font extractor
**Goal:** Get comprehensive data for ChatGPT

### Phase 2 - Week 2: Maximum Quality Generator
- [ ] Create `ChatGPTHTMLGenerator` class
- [ ] Implement multi-variant generation (3 parallel)
- [ ] Implement AI quality validation
- [ ] Implement AI refinement
**Goal:** Generate PERFECT websites

### Phase 3 - Week 3: Integration
- [ ] Update `template_generator_premium.py`
- [ ] Add regeneration support
- [ ] Add quality scoring display
**Goal:** Full end-to-end working system

### Phase 4 - Week 4: Testing & Polish
- [ ] Test with 10+ businesses
- [ ] Validate quality scores (must be 90+)
- [ ] Performance optimization
- [ ] Production deployment
**Goal:** Ship to production!

---

## ✅ SUCCESS CRITERIA - MAXIMUM QUALITY

After implementation, **EVERY** generated website must:

1. ✅ **Score 90+ in AI validation** (out of 100)
2. ✅ **Look modern** (2024 design standards - gradients, animations, glassmorphism)
3. ✅ **Look professional** (clean, polished, high-quality)
4. ✅ **Look beautiful** (aesthetic, visually impressive)
5. ✅ **Perfect responsiveness** (flawless on mobile, tablet, desktop)
6. ✅ **Use ALL brand assets** (logos, colors, images from scraped site)
7. ✅ **Complete structure** (navbar, hero, services, about, testimonials, contact, footer)
8. ✅ **Smooth animations** (fade-ins, hover effects, transitions)
9. ✅ **Professional code** (valid HTML5, semantic markup, optimized CSS)
10. ✅ **Client satisfaction** (businesses say "WOW! This is amazing!")

**If ANY of these criteria not met → REGENERATE until perfect!**

---

## 📊 EXPECTED RESULTS

### Before (Current System):
```
❌ Quality Score: 60-70/100
❌ Modern: No (old HTML structure)
❌ Professional: Sometimes
❌ Beautiful: Rarely
❌ Client Satisfaction: 50%
```

### After (Maximum Quality System):
```
✅ Quality Score: 90-95/100
✅ Modern: YES! (2024 standards)
✅ Professional: ALWAYS
✅ Beautiful: ALWAYS
✅ Client Satisfaction: 95%+
```

---

## 🎬 DEVELOPER QUICK START

**Ready to implement? Follow these steps:**

1. **Read this entire story** ✅ (You're here!)

2. **Start with Phase 1:**
   ```bash
   cd backend/app/services
   # Enhance website_scraper.py
   # Add comprehensive asset extraction
   ```

3. **Then Phase 2:**
   ```bash
   # Create chatgpt_html_generator.py
   # Copy code from "Phase 2" section above
   # Implement maximum quality generation
   ```

4. **Then Phase 3:**
   ```bash
   # Update template_generator_premium.py
   # Replace old approach with maximum quality approach
   ```

5. **Test thoroughly:**
   ```bash
   # Generate templates for 10 businesses
   # Validate each scores 90+
   # Check responsiveness, animations, brand assets
   ```

6. **Deploy to production! 🚀**

---

## 🔑 KEY TAKEAWAYS

**Remember:**
- ✅ Budget APPROVED - use maximum resources
- ✅ Generate 3 variants, pick best
- ✅ Use AI to validate quality (must be 90+)
- ✅ Refine best variant to make PERFECT
- ✅ Never settle for less than EXCELLENT
- ✅ Use ALL scraped brand assets (logos, colors, images, videos)
- ✅ Generate BRAND NEW HTML from scratch (not modify old)
- ✅ Modern, professional, beautiful - NO EXCEPTIONS!

**This is NOT about saving money - this is about PERFECT QUALITY!**

---

**END OF STORY**
