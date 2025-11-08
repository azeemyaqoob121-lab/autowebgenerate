"""AI Template Generation Service using OpenAI GPT-4"""
import logging
from typing import List, Dict, Any
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Business, Template, Evaluation
from app.services.website_scraper import scrape_business_website
import uuid

logger = logging.getLogger(__name__)

# Configure OpenAI client (v1.0+ API)
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class TemplateGenerationError(Exception):
    """Raised when template generation fails"""
    pass


async def generate_templates_for_business(
    business: Business,
    db: Session,
    num_variants: int = 3
) -> List[Template]:
    """
    Generate AI-improved website templates for a business using GPT-4.

    This function scrapes the business's existing website, analyzes evaluation data,
    and generates improved HTML/CSS templates using GPT-4.

    Args:
        business: Business model instance
        db: Database session
        num_variants: Number of template variants to generate (1-3)

    Returns:
        List of generated Template instances

    Raises:
        TemplateGenerationError: If generation fails
    """
    if not settings.OPENAI_API_KEY:
        raise TemplateGenerationError("OpenAI API key not configured")

    # Get business evaluation data
    evaluation = db.query(Evaluation).filter(
        Evaluation.business_id == business.id
    ).order_by(Evaluation.evaluated_at.desc()).first()

    # Build context for GPT-4
    business_context = _build_business_context(business, evaluation)

    # Generate templates
    generated_templates = []

    for variant_num in range(1, num_variants + 1):
        try:
            template = await _generate_single_template(
                business_context=business_context,
                variant_number=variant_num,
                business_id=business.id,
                db=db
            )
            generated_templates.append(template)
            logger.info(f"Generated template variant {variant_num} for business {business.id}")
        except Exception as e:
            logger.error(f"Failed to generate template variant {variant_num}: {str(e)}")
            # Continue with other variants even if one fails
            continue

    if not generated_templates:
        raise TemplateGenerationError("Failed to generate any templates")

    return generated_templates


def _build_business_context(business: Business, evaluation: Evaluation = None) -> Dict[str, Any]:
    """Build context dictionary for GPT-4 prompt INCLUDING scraped website content"""
    context = {
        "name": business.name,
        "category": business.category or "General Business",
        "location": business.location or "Unknown",
        "description": business.description or f"A {business.category or 'business'} in {business.location or 'your area'}",
        "website_url": business.website_url,
        "phone": business.phone,
        "email": business.email,
        "address": business.address,
    }

    if evaluation:
        context["evaluation"] = {
            "performance_score": evaluation.performance_score,
            "seo_score": evaluation.seo_score,
            "accessibility_score": evaluation.accessibility_score,
            "aggregate_score": evaluation.aggregate_score,
        }

    # CRITICAL: Scrape their current website to get REAL content
    if business.website_url:
        logger.info(f"Scraping website content from: {business.website_url}")
        try:
            scraped_content = scrape_business_website(business.website_url)
            if scraped_content:
                context["scraped_content"] = scraped_content
                logger.info(f"Successfully scraped {len(scraped_content)} content categories from website")
            else:
                logger.warning(f"Failed to scrape website: {business.website_url}")
        except Exception as e:
            logger.error(f"Error scraping website {business.website_url}: {str(e)}")

    return context


async def _generate_single_template(
    business_context: Dict[str, Any],
    variant_number: int,
    business_id: uuid.UUID,
    db: Session
) -> Template:
    """Generate a single template variant using GPT-4"""

    if not client:
        raise TemplateGenerationError("OpenAI client not initialized. API key may be missing.")

    prompt = _build_gpt4_prompt(business_context, variant_number)

    # Log prompt details for debugging
    prompt_length = len(prompt)
    logger.info(f"Generated prompt for variant {variant_number}: {prompt_length} characters")
    logger.debug(f"Prompt preview (first 500 chars): {prompt[:500]}")

    # Check if scraped content is included
    if "scraped_content" in business_context:
        scraped_data = business_context["scraped_content"]
        logger.info(f"Scraped content included - Logo: {bool(scraped_data.get('logo'))}, "
                   f"Services: {len(scraped_data.get('services_menu', []))}, "
                   f"Images: {len(scraped_data.get('images', []))}")

    try:
        logger.info(f"Calling OpenAI API (gpt-4o) for business: {business_context.get('name')}")

        # Using GPT-4o for BEST quality website generation
        response = client.chat.completions.create(
            model="gpt-4o",  # Latest GPT-4o model for superior quality and reasoning
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert web designer creating modern, professional, fully-responsive websites.

Generate a complete, production-ready HTML website with inline CSS and JavaScript.

=== OUTPUT FORMAT (CRITICAL) ===
- Start with <!DOCTYPE html> and end with </html>
- Include ALL CSS in <style> tags in <head>
- Include ALL JavaScript in <script> tags before </body>
- NO markdown code blocks (no ```html or ```)
- Output pure HTML only, zero explanatory text

=== RESPONSIVE DESIGN (MOBILE-FIRST) ===

Base Styles (Mobile < 768px):
- Container: max-width 100%, padding 20px
- Font sizes: h1: 2rem, h2: 1.5rem, body: 1rem
- Touch targets: minimum 44px height
- Stack all elements vertically
- Full-width buttons and cards

Tablet (768px - 1024px):
@media (min-width: 768px) {
  - Container: max-width 720px, margin 0 auto
  - Font sizes: h1: 2.5rem, h2: 1.75rem
  - Grid layouts: 2 columns for cards
  - Increased spacing
}

Desktop (> 1024px):
@media (min-width: 1024px) {
  - Container: max-width 1200px, margin 0 auto
  - Font sizes: h1: 3.5rem, h2: 2.5rem
  - Grid layouts: 3-4 columns for cards
  - Maximum spacing and padding
  - Hover effects and animations
}

=== STRUCTURE & ALIGNMENT ===

Every section should follow this structure:
<section class="section" id="section-name">
  <div class="container">
    <div class="section-header">
      <h2>Section Title</h2>
      <p>Section description</p>
    </div>
    <div class="section-content">
      <!-- Content here -->
    </div>
  </div>
</section>

CSS for perfect alignment:
.section {
  padding: 80px 20px;
  width: 100%;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

@media (max-width: 768px) {
  .section { padding: 60px 15px; }
  .container { padding: 0 15px; }
  .section-header { margin-bottom: 40px; }
}

=== NAVIGATION BAR ===

Fixed navbar with glassmorphism:
- Position: fixed, top: 0, width: 100%, z-index: 1000
- Background: rgba(255, 255, 255, 0.95)
- Backdrop-filter: blur(20px)
- Box-shadow: 0 2px 20px rgba(0,0,0,0.1)
- Desktop: horizontal menu, centered
- Mobile: hamburger menu (icon toggles menu)
- Smooth scroll to sections on click
- Active link highlighting

Mobile menu (< 768px):
- Hamburger icon (3 horizontal bars)
- Menu slides in from top/left
- Full-screen overlay
- Close on link click

=== HERO SECTION ===

Full-screen hero with:
- Min-height: 100vh
- Display: flex, align-items: center, justify-content: center
- Background: gradient or image with overlay
- Text: centered, white color, max-width: 800px
- CTA buttons: 2 buttons, responsive width
- Padding for mobile safety (avoid notches)

=== CARDS/GRID LAYOUT ===

Service/product cards:
- Display: grid
- Mobile: grid-template-columns: 1fr
- Tablet: grid-template-columns: repeat(2, 1fr)
- Desktop: grid-template-columns: repeat(3, 1fr)
- Gap: 30px (20px on mobile)
- Card style: white background, border-radius: 12px, box-shadow, padding: 30px
- Hover effect: transform translateY(-5px), increased shadow

=== TYPOGRAPHY ===

Font families:
- Headings: 'Playfair Display', serif
- Body: 'Inter', sans-serif
- Load via Google Fonts CDN

Sizing (mobile-first):
h1: clamp(2rem, 5vw, 4rem)
h2: clamp(1.75rem, 4vw, 3rem)
h3: clamp(1.25rem, 3vw, 2rem)
body: clamp(1rem, 2vw, 1.125rem)

Line heights:
- Headings: 1.2
- Body: 1.6

=== IMAGES ===

Use Unsplash for all images:
- Gallery: https://source.unsplash.com/800x600/?{business-type},{keyword}
- Hero: https://source.unsplash.com/1920x1080/?{business-type}
- Cards: https://source.unsplash.com/400x300/?{business-type},{service}

Image CSS:
img {
  max-width: 100%;
  height: auto;
  display: block;
  border-radius: 8px;
}

=== CONTACT FORM ===

Responsive form layout:
- Desktop: 2 columns (info left, form right)
- Mobile: 1 column (info top, form bottom)
- Input styling: padding 15px, border-radius 8px, border 1px solid #ddd
- Focus state: border-color change, box-shadow
- Submit button: full-width on mobile, auto on desktop

=== COLORS (Industry-specific) ===

Restaurant: Warm tones (#F59E0B, #EF4444)
Salon/Beauty: Pink/Purple (#EC4899, #A855F7)
Services/Plumbing: Blue (#3B82F6, #1E40AF)
Professional/Law: Dark/Green (#1F2937, #10B981)
Healthcare: Cyan/Blue (#06B6D4, #3B82F6)

=== SPACING SYSTEM ===

Use consistent spacing:
- xs: 8px
- sm: 16px
- md: 24px
- lg: 32px
- xl: 48px
- 2xl: 64px
- 3xl: 96px

Section padding: 80px (desktop), 60px (tablet), 40px (mobile)
Container padding: 20px (always)
Element margins: 24px between elements
Card padding: 30px (desktop), 20px (mobile)

=== FOOTER ===

Multi-column footer:
- Desktop: 3-4 columns
- Tablet: 2 columns
- Mobile: 1 column
- Background: dark (#1F2937)
- Text: light gray (#9CA3AF)
- Links: white on hover
- Copyright: centered, smaller text

=== ANIMATIONS ===

Include these animations:
1. Fade in on scroll (Intersection Observer)
2. Navbar background on scroll
3. Hamburger menu toggle
4. Smooth scroll to sections
5. Button hover effects
6. Card hover effects

=== FINAL CHECKLIST ===

Before output, ensure:
✓ Mobile-first responsive design
✓ All breakpoints implemented
✓ Containers with max-width and centering
✓ Consistent spacing throughout
✓ Perfect vertical and horizontal alignment
✓ Working mobile menu
✓ All images load properly
✓ Form validation included
✓ Professional, polished appearance
✓ Clean, organized code

Generate a complete, beautiful, FULLY RESPONSIVE website that looks professional on ALL devices."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,  # Lower temperature for more consistent, structured output
            max_tokens=16384  # Maximum for GPT-4o to allow comprehensive websites
        )

        template_content = response.choices[0].message.content

        # Log response stats
        logger.info(f"GPT response length: {len(template_content)} characters")

        # Parse the response to extract HTML and CSS
        html_content, css_content = _parse_template_response(template_content)

        # Determine improvements made
        improvements = _determine_improvements(business_context, variant_number)

        # Create template model
        template = Template(
            id=uuid.uuid4(),
            business_id=business_id,
            html_content=html_content,
            css_content=css_content,
            js_content=None,  # Can be added later
            improvements_made=improvements,
            variant_number=variant_number
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        logger.info(f"Successfully generated template variant {variant_number} for {business_context.get('name')}")
        return template

    except Exception as e:
        # Enhanced error handling with specific error types
        error_msg = str(e)
        error_type = type(e).__name__

        logger.error(f"Template generation failed - Error type: {error_type}")
        logger.error(f"Error message: {error_msg}")
        logger.error(f"Business: {business_context.get('name')}, Variant: {variant_number}")

        # Check for specific error types
        if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            logger.error("Network/Connection error detected - possible causes:")
            logger.error("1. OpenAI API is down or unreachable")
            logger.error("2. Network connectivity issue")
            logger.error("3. Firewall blocking the request")
            logger.error(f"4. Prompt too large ({prompt_length} characters)")
            raise TemplateGenerationError(f"Connection error: Unable to reach OpenAI API. Please check network connection and try again.")

        elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            logger.error("API key error detected")
            raise TemplateGenerationError(f"OpenAI API key error: {error_msg}")

        elif "rate_limit" in error_msg.lower():
            logger.error("Rate limit error detected")
            raise TemplateGenerationError(f"OpenAI rate limit exceeded: {error_msg}")

        else:
            logger.error(f"Unexpected error: {error_msg}")
            raise TemplateGenerationError(f"Failed to generate template: {error_type} - {error_msg}")


def _build_gpt4_prompt(context: Dict[str, Any], variant_number: int) -> str:
    """Build the optimized prompt for GPT-4o"""

    evaluation_info = ""
    if "evaluation" in context:
        eval_data = context["evaluation"]
        evaluation_info = f"""
CURRENT WEBSITE ISSUES (What we're fixing):
• Performance Score: {eval_data.get('performance_score', 0) * 100:.0f}% - Needs optimization
• SEO Score: {eval_data.get('seo_score', 0) * 100:.0f}% - Needs better meta tags and structure
• Accessibility Score: {eval_data.get('accessibility_score', 0) * 100:.0f}% - Needs WCAG compliance
• Overall Score: {eval_data.get('aggregate_score', 0):.0f}% - Goal: 90%+
"""

    # Industry-specific color schemes
    industry_colors = {
        "restaurant": {"primary": "#F59E0B", "secondary": "#EF4444", "accent": "#FBBF24", "vibe": "warm, appetizing"},
        "plumbing": {"primary": "#3B82F6", "secondary": "#1E40AF", "accent": "#60A5FA", "vibe": "trustworthy, professional"},
        "law": {"primary": "#1F2937", "secondary": "#374151", "accent": "#10B981", "vibe": "authoritative, sophisticated"},
        "healthcare": {"primary": "#06B6D4", "secondary": "#0891B2", "accent": "#22D3EE", "vibe": "caring, clean"},
        "tech": {"primary": "#8B5CF6", "secondary": "#7C3AED", "accent": "#A78BFA", "vibe": "innovative, modern"},
        "retail": {"primary": "#EC4899", "secondary": "#DB2777", "accent": "#F472B6", "vibe": "vibrant, engaging"},
        "default": {"primary": "#667eea", "secondary": "#764ba2", "accent": "#f093fb", "vibe": "professional, modern"}
    }

    # Determine color scheme based on business category
    category_lower = context['category'].lower() if context['category'] else ""
    color_scheme = industry_colors.get("default")
    for industry, colors in industry_colors.items():
        if industry in category_lower:
            color_scheme = colors
            break

    variant_styles = {
        1: f"""DESIGN VARIANT 1 - MODERN MINIMALIST WITH STUNNING VISUALS + VIDEO:
• Layout: Bento grid with asymmetric cards (Apple/Linear-style)
• Hero: Full-screen BACKGROUND VIDEO (muted, autoplay, loop) with gradient overlay + floating particles
  - Video: Mixkit.co free video relevant to {category_lower}
  - Fallback image: `https://source.unsplash.com/1920x1080/?{category_lower},professional,modern`
  - Mobile: Hide video, show Unsplash image instead for performance
• Navigation: Glassmorphism sticky navbar with blur effect (backdrop-filter: blur(20px))
• Images: 10-12 high-quality Unsplash images throughout (hero fallback, about, services, gallery, team)
  - Services: `https://source.unsplash.com/800x600/?{category_lower},service`
  - Team/About: `https://source.unsplash.com/800x600/?{category_lower},people,team`
  - Gallery: 6 images in bento grid layout
• Video Portfolio: 2-3 embedded videos (YouTube/Vimeo) showcasing work/testimonials
• Cards: 3D transforms on hover with deep shadows + image zoom effect
• Typography: Poppins/Inter, 72px hero with gradient text clip
• Colors: {color_scheme['primary']} → {color_scheme['secondary']} ({color_scheme['vibe']})
• Animations:
  - Scroll-triggered fade-ins with Intersection Observer
  - Parallax hero background video (slight zoom effect on scroll)
  - Staggered card reveals (0.1s delay each)
  - Counter animations for stats (0 → final number using requestAnimationFrame)
  - Image hover zoom (transform: scale(1.1))
  - Video play button hover effects
• Business-Specific Features:
  - Restaurant: Food gallery with 8 images, menu video, dining ambiance video
  - Plumber: Before/after image slider, work process video, testimonial videos
  - Gym: Workout image gallery, class schedule, training videos
  - Law Firm: Team photos, office tour video, client success stories
• Vibe: Clean, spacious, premium, visually stunning, video-rich""",

        2: f"""DESIGN VARIANT 2 - BOLD & DRAMATIC WITH RICH MEDIA + VIDEOS:
• Layout: Full-width sections with diagonal/curved dividers
• Hero: Full-screen BACKGROUND VIDEO with dark cinematic overlay + neumorphic elements floating
  - Video: Premium stock video from Mixkit (e.g., office, tech, business scenes)
  - Fallback: `https://source.unsplash.com/1920x1080/?{category_lower},luxury,premium`
  - Mobile: Gradient background instead of video for performance
• Navigation: Dark mode (#1F2937) with {color_scheme['accent']} accent highlights
• Images: 12-15 stunning photos with gradient overlays and blur effects
  - Gallery: `https://source.unsplash.com/800x600/?{category_lower},interior,design`
  - Background sections: Multiple Unsplash images with opacity overlays
  - Portfolio: 10+ project images in masonry grid
• Video Gallery: 3-4 video cards with play buttons, video testimonials carousel
• Cards: Glassmorphism cards with backdrop blur + image/video backgrounds
• Typography: DM Sans + Playfair Display serif mix, dramatic 84px hero
• Colors: Dark base (#1F2937) + {color_scheme['accent']} + gold accents (#F59E0B)
• Animations:
  - Staggered section reveals (slide up + fade in)
  - Magnetic button effects (follows cursor on hover)
  - Blob shapes morphing in background (SVG animation)
  - Image ken burns effect (slow zoom + pan)
  - Video thumbnail hover: play icon scales up
  - Testimonial video carousel with smooth transitions
• Business-Specific Features:
  - Restaurant: Food preparation video, chef interview, customer reviews video, 10+ food photos
  - Plumber: Service area map video, repair process timelapse, 8+ before/after photos
  - Gym: Class highlight videos, trainer intro videos, workout gallery
  - Salon: Transformation videos, treatment process videos, 12+ before/after photos
• Vibe: Sophisticated, award-winning, dramatic, magazine-quality, cinematic""",

        3: f"""DESIGN VARIANT 3 - VIBRANT & ULTRA-MODERN WITH VIDEOS + INTERACTIVE ELEMENTS:
• Layout: Overlapping sections with creative asymmetry + floating elements
• Hero: Split-screen design with BACKGROUND VIDEO on left + morphing mesh gradient animation on right
  - Video: Colorful, energetic stock video from Mixkit relevant to {category_lower}
  - Fallback: `https://source.unsplash.com/1920x1080/?{category_lower},colorful,vibrant`
  - Mobile: Full-width gradient with single Unsplash image
• Navigation: Transparent → solid transition on scroll with blur
• Images: 12-15 vibrant photos with creative layouts (grid, masonry, overlapping, carousel)
  - Portfolio/Work: `https://source.unsplash.com/800x600/?{category_lower},creative,art`
  - Services: Multiple small images in bento grid layout
  - Gallery: Interactive image slider with 10+ photos
• Video Portfolio: Interactive video grid (4-6 videos) with hover-to-play feature
• Before/After Slider: Image comparison slider for relevant businesses
• Cards: Rounded with gradient borders + hover glow effect + background images/videos
• Typography: Bold display fonts (Outfit/Space Grotesk), fluid sizing (clamp())
• Colors: Multi-gradient ({color_scheme['primary']}, {color_scheme['accent']}, complementary teal/purple)
• Animations:
  - Floating elements with infinite loop animations
  - Cursor follower spotlight effect
  - Smooth parallax on multiple layers (0.3x, 0.5x, 0.7x speeds)
  - Card tilt effect on hover (3D perspective)
  - Text reveal animations (slide in from left/right)
  - Video hover: play preview on mouse over (muted)
  - Loading animations for images (skeleton → fade in)
  - Image gallery slider with smooth transitions
• Business-Specific Features:
  - Restaurant: Food slider carousel (15 photos), menu video walkthrough, chef cooking videos, 360° dining room view
  - Plumber: Interactive before/after slider (10 projects), emergency response video, service area map, customer video testimonials
  - Gym: Class schedule with video previews, trainer spotlight videos, workout transformation slider, facility tour video
  - Salon: Before/after transformation slider, treatment process videos, stylist intro videos, style gallery (20+ photos)
  - Real Estate: Property video tours, neighborhood walkthrough videos, virtual staging slider, drone footage
  - Tech/IT: Product demo videos, case study videos, animated infographics, tech stack visualization
• Vibe: Energetic, cutting-edge, memorable, Instagram-worthy, highly interactive"""
    }

    prompt = f"""Create a STUNNING, PROFESSIONAL website for this specific business. This needs to be production-ready with modern design trends and flawless execution.

═══════════════════════════════════════════════════════════════════════════════
🎯 BUSINESS INFORMATION (Use this EXACT data - NO placeholders!)
═══════════════════════════════════════════════════════════════════════════════

**Company Name:** {context['name']}
**Industry:** {context['category']}
**Location:** {context['location']}
**Description:** {context['description']}
**Contact:** Phone: {context.get('phone', 'N/A')} | Email: {context.get('email', 'N/A')}
**Address:** {context.get('address', 'N/A')}
{evaluation_info}

═══════════════════════════════════════════════════════════════════════════════
🎨 DESIGN REQUIREMENTS FOR THIS VARIANT
═══════════════════════════════════════════════════════════════════════════════

{variant_styles.get(variant_number, variant_styles[1])}

═══════════════════════════════════════════════════════════════════════════════
🎬 VIDEOS & VISUAL MEDIA (MUST INCLUDE - CRITICAL FOR PREMIUM FEEL!)
═══════════════════════════════════════════════════════════════════════════════

**1. HERO BACKGROUND VIDEO (MANDATORY - Creates WOW Factor!):**

```html
<!-- Hero Section with Background Video -->
<section class="hero" id="home">
  <!-- Background Video (muted, autoplay, loop) -->
  <video class="hero-video" autoplay muted loop playsinline>
    <source src="https://assets.mixkit.co/videos/preview/{{{{video-id}}}}.mp4" type="video/mp4">
    <!-- Fallback to image if video fails -->
    <img src="https://source.unsplash.com/1920x1080/?{category_lower},professional" alt="Hero background">
  </video>

  <!-- Dark overlay for text readability -->
  <div class="hero-overlay"></div>

  <!-- Hero Content -->
  <div class="hero-content">
    <h1>Your Amazing Headline</h1>
    <p>Compelling subtitle</p>
  </div>
</section>

<!-- CSS for Video -->
<style>
.hero-video {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}}
.hero-overlay {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba({color_scheme['primary']}, 0.85), rgba({color_scheme['secondary']}, 0.75));
  z-index: 2;
}}
.hero-content {{
  position: relative;
  z-index: 3;
}}
/* Hide video on mobile for performance */
@media (max-width: 768px) {{
  .hero-video {{
    display: none;
  }}
  .hero {{
    background-image: url('https://source.unsplash.com/1920x1080/?{category_lower},professional');
  }}
}}
</style>
```

**FREE VIDEO SOURCES (Use these for background videos):**
- Mixkit.co: `https://assets.mixkit.co/videos/preview/mixkit-[video-name].mp4`
- Pexels Videos: High-quality free stock videos
- Coverr.co: Free homepage background videos

**Business-Specific Video Suggestions:**
- Restaurant: Food preparation, dining ambiance, chef cooking
- Plumber: Water flowing, pipe installation, satisfied customer
- Gym/Fitness: Workout montage, training sessions, gym equipment
- Law Firm: Office walkthrough, team meeting, professional setting
- Salon/Spa: Relaxing ambiance, treatments, satisfied clients
- Real Estate: Property walkthrough, neighborhood tour
- Tech/IT: Data visualization, coding screens, futuristic graphics

**2. VIDEO GALLERY/PORTFOLIO SECTION (For businesses with visual work):**

```html
<!-- Video Portfolio Section -->
<section class="video-portfolio">
  <h2>Our Work in Action</h2>
  <div class="video-grid">
    <!-- Video Card 1 -->
    <div class="video-card">
      <div class="video-wrapper">
        <video controls poster="https://source.unsplash.com/600x400/?{category_lower},work">
          <source src="placeholder-video.mp4" type="video/mp4">
        </video>
      </div>
      <h3>Project Title</h3>
      <p>Brief description</p>
    </div>

    <!-- YouTube Embed -->
    <div class="video-card">
      <div class="video-wrapper">
        <iframe src="https://www.youtube.com/embed/VIDEO_ID"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
        </iframe>
      </div>
      <h3>Customer Testimonial</h3>
    </div>

    <!-- Vimeo Embed -->
    <div class="video-card">
      <div class="video-wrapper">
        <iframe src="https://player.vimeo.com/video/VIDEO_ID"
                frameborder="0"
                allow="autoplay; fullscreen; picture-in-picture"
                allowfullscreen>
        </iframe>
      </div>
      <h3>Behind the Scenes</h3>
    </div>
  </div>
</section>

<!-- CSS for Responsive Video Embeds -->
<style>
.video-wrapper {{
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
  border-radius: 15px;
}}
.video-wrapper video,
.video-wrapper iframe {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}}
</style>
```

**3. UNSPLASH IMAGE INTEGRATION (Required - 10-15 images minimum):**

1. **Hero Section Fallback Image:**
   ```html
   <div class="hero" style="background-image: url('https://source.unsplash.com/1920x1080/?{category_lower},professional,business');">
   ```
   - Full viewport height background
   - Gradient overlay (linear-gradient(135deg, rgba({color_scheme['primary']}, 0.9), rgba({color_scheme['secondary']}, 0.7)))
   - Parallax effect on scroll

2. **About/Team Section Images:**
   - Team photo: `https://source.unsplash.com/800x600/?{category_lower},people,team`
   - Office/Location: `https://source.unsplash.com/800x600/?{category_lower},interior,office`
   - Use in image tags with loading="lazy" for performance

**FONT AWESOME ICONS (MANDATORY):**
```html
<!-- Add Font Awesome CDN in <head> -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<!-- Use professional icons throughout -->
<i class="fas fa-check-circle"></i> <!-- Checkmarks -->
<i class="fas fa-star"></i> <!-- Ratings -->
<i class="fas fa-phone"></i> <!-- Contact -->
<i class="fas fa-envelope"></i> <!-- Email -->
<i class="fas fa-map-marker-alt"></i> <!-- Location -->
<i class="fas fa-arrow-right"></i> <!-- CTAs -->
```

**INLINE SVG ICONS WITH LOTTIE-LIKE CSS ANIMATIONS (MANDATORY):**
Add custom inline SVG icons that match the business type with smooth CSS animations:

```html
<!-- Example: Wrench icon for repair/plumbing business -->
<svg class="lottie-icon" width="64" height="64" viewBox="0 0 64 64">
  <path d="..." fill="currentColor"/>
</svg>

<!-- CSS Animation for Lottie-like effect -->
<style>
.lottie-icon {{
  animation: iconFloat 3s ease-in-out infinite;
}}
@keyframes iconFloat {{
  0%, 100% {{ transform: translateY(0) rotate(0deg); }}
  50% {{ transform: translateY(-10px) rotate(5deg); }}
}}
</style>
```

**Icon Examples by Business Type:**
- Restaurant: Chef hat, utensils, wine glass (animated steam, floating effect)
- Plumber: Wrench, pipe, water drop (rotating, dripping animation)
- Lawyer: Scale, gavel, briefcase (swinging, tilting animation)
- Healthcare: Heart, stethoscope, medical cross (pulsing, beating animation)
- Tech: Code brackets, laptop, cloud (glowing, floating animation)

3. **Responsive Images with <picture> Element (MANDATORY):**
   Use <picture> element for responsive images with lazy loading:
   ```html
   <picture>
     <source media="(min-width: 1024px)" srcset="https://source.unsplash.com/1920x1080/?{category_lower},professional">
     <source media="(min-width: 768px)" srcset="https://source.unsplash.com/1200x800/?{category_lower},professional">
     <img src="https://source.unsplash.com/800x600/?{category_lower},professional"
          alt="{context['category']} service"
          loading="lazy"
          class="responsive-image">
   </picture>
   ```

4. **Services/Products Section (3-6 images):**
   - Each service card gets relevant image:
     * `https://source.unsplash.com/600x400/?{category_lower},service1` (customize keywords!)
     * For restaurant: `food,dining,cuisine,{category_lower}`
     * For plumber: `plumbing,pipes,tools,{category_lower}`
     * For lawyer: `law,justice,legal,{category_lower}`
   - Zoom effect on hover

4. **Gallery/Portfolio Section (3-5 images):**
   - Masonry grid or bento grid layout
   - `https://source.unsplash.com/800x600/?{category_lower},work,portfolio`
   - Lightbox effect on click (modal overlay)

5. **Background Sections:**
   - Stats section with subtle background: opacity 0.1
   - Testimonials with blur effect background

**6. BUSINESS-SPECIFIC IMAGE & VIDEO GALLERIES (10-15 IMAGES + 2-4 VIDEOS - MANDATORY!):**

Choose the appropriate gallery based on business type:

**RESTAURANT:** 12-15 food images + chef video + dining ambiance video
**PLUMBER:** 8-10 before/after images + work process video + testimonial video
**GYM:** 10 equipment/facility images + 2 class videos + transformation slider
**SALON:** 10 before/after images + treatment video + stylist intro video
**LAW FIRM:** 6-8 team photos + office tour video + success story video
**REAL ESTATE:** 15 property images + virtual tour video + drone footage

Each business type MUST include relevant image galleries AND videos!

**IMAGE STYLING REQUIREMENTS:**
```css
img {{
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    transition: transform 0.4s ease;
}}
img:hover {{
    transform: scale(1.05) rotate(1deg);
}}
```

═══════════════════════════════════════════════════════════════════════════════
✨ ANIMATIONS & EFFECTS (MUST INCLUDE - CRITICAL!)
═══════════════════════════════════════════════════════════════════════════════

**REQUIRED CSS ANIMATIONS (Include ALL):**

1. **Scroll-Triggered Fade-Ins (Intersection Observer):**
   ```javascript
   const observerOptions = {{
       threshold: 0.1,
       rootMargin: '0px 0px -100px 0px'
   }};
   const observer = new IntersectionObserver((entries) => {{
       entries.forEach(entry => {{
           if (entry.isIntersecting) {{
               entry.target.classList.add('fade-in-visible');
           }}
       }});
   }}, observerOptions);
   ```

2. **Parallax Hero Background:**
   - Hero image scrolls at 0.5x speed
   - Creates depth illusion

3. **Counter Animations:**
   - Stats count from 0 to final number
   - Triggered when section enters viewport
   - Example: "500+ Clients" animates: 0 → 500

4. **Button Hover Effects:**
   ```css
   button {{
       background: linear-gradient(135deg, {color_scheme['primary']}, {color_scheme['secondary']});
       box-shadow: 0 10px 30px rgba(0,0,0,0.2);
       transition: all 0.3s ease;
   }}
   button:hover {{
       transform: translateY(-3px);
       box-shadow: 0 15px 40px rgba(0,0,0,0.3);
   }}
   button:active {{
       transform: translateY(-1px);
   }}
   ```

5. **Card Hover Lifts:**
   - Cards lift 10px on hover
   - Shadow increases
   - Image zooms inside card

6. **Navbar Scroll Effect:**
   - Transparent at top
   - Glassmorphism (blur + semi-transparent) on scroll
   - Smooth transition

7. **Loading Animations:**
   - Skeleton screens for images
   - Fade-in when loaded

8. **Floating Elements:**
   - Decorative shapes floating in background
   - Infinite loop subtle animation

9. **Text Animations:**
   - Hero headline: Typewriter effect or slide in from left
   - Subtitle: Fade in after 0.3s delay with typewriter option
   - Typing animation: Letters appear one by one

10. **Carousel/Slider:**
    - Testimonials auto-rotate every 5 seconds
    - Smooth slide transitions
    - Dot navigation with active states

11. **Page Load Animations:**
    - Loading spinner for images (skeleton screens)
    - Fade-in animations when page loads
    - Staggered element reveals (0.1s delay each)

12. **Advanced Visual Effects:**
    - Cursor follower spotlight effect (optional)
    - Card tilt on mouse move (3D perspective)
    - Magnetic buttons (follow cursor slightly on hover)
    - Blob shapes morphing in background

**ANIMATION CSS KEYFRAMES (Include these and more):**
```css
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-20px); }}
}}

@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes typing {{
    from {{ width: 0; }}
    to {{ width: 100%; }}
}}

@keyframes blink {{
    50% {{ border-color: transparent; }}
}}

@keyframes zoomIn {{
    from {{ transform: scale(0.8); opacity: 0; }}
    to {{ transform: scale(1); opacity: 1; }}
}}

@keyframes slideInLeft {{
    from {{ transform: translateX(-100px); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

@keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.05); }}
}}

@keyframes particle {{
    0% {{ transform: translateY(0) translateX(0); opacity: 1; }}
    100% {{ transform: translateY(-100vh) translateX(50px); opacity: 0; }}
}}
```

═══════════════════════════════════════════════════════════════════════════════
💫 SPECIAL CINEMATIC EFFECTS (MAKE IT VIRAL-WORTHY!)
═══════════════════════════════════════════════════════════════════════════════

**HERO SECTION - CINEMATIC EXPERIENCE:**
1. **Floating Particles Animation:**
   - Create 15-20 div elements with class "particle"
   - Animated floating particles in hero background (CSS animation)
   - Different sizes, speeds, and opacity for depth
   - Creates magical, premium atmosphere

2. **Parallax Layers:**
   - Hero background scrolls at 0.5x speed (parallax effect)
   - Foreground content scrolls normally
   - Creates 3D depth illusion

3. **Gradient Mesh Background:**
   - Animated gradient background (gradientShift animation)
   - Smooth color transitions
   - Premium, modern aesthetic

**3D CARD EFFECTS:**
1. **Tilt on Mouse Move:**
   - Service cards tilt based on cursor position
   - Use JavaScript to calculate mouse position
   - Apply 3D transform with perspective
   - Smooth, magnetic effect

2. **Hover Lift with Shadow:**
   - Cards lift 15px on hover
   - Shadow increases dramatically
   - Images inside zoom (scale 1.1)
   - Creates premium, interactive feel

**PROFESSIONAL GLASSMORPHISM NAVBAR (ABSOLUTELY MANDATORY!):**

```html
<!-- NAVBAR - Glassmorphism with Mobile Menu -->
<nav class="navbar" id="navbar">
  <div class="nav-container">
    <!-- Logo -->
    <div class="nav-logo">
      <a href="#home">{context['name']}</a>
    </div>

    <!-- Desktop Navigation Links -->
    <ul class="nav-menu">
      <li><a href="#home" class="nav-link active">Home</a></li>
      <li><a href="#about" class="nav-link">About</a></li>
      <li><a href="#services" class="nav-link">Services</a></li>
      <li><a href="#gallery" class="nav-link">Gallery</a></li>
      <li><a href="#testimonials" class="nav-link">Reviews</a></li>
      <li><a href="#contact" class="nav-link">Contact</a></li>
    </ul>

    <!-- CTA Button -->
    <a href="#contact" class="nav-cta">Get Quote</a>

    <!-- Mobile Hamburger Icon -->
    <div class="hamburger">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</nav>

<!-- CSS for Professional Navbar -->
<style>
/* Navbar - Glassmorphism Effect */
.navbar {{
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  padding: 1rem 0;
  transition: all 0.3s ease;
}}

/* Glassmorphism effect on scroll */
.navbar.scrolled {{
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}}

.nav-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.nav-logo a {{
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  text-decoration: none;
  font-family: 'Poppins', sans-serif;
}}

.nav-menu {{
  display: flex;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}}

.nav-link {{
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}}

.nav-link.active,
.nav-link:hover {{
  color: {color_scheme['accent']};
}}

.nav-link::after {{
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background: {color_scheme['accent']};
  transition: width 0.3s ease;
}}

.nav-link.active::after,
.nav-link:hover::after {{
  width: 100%;
}}

.nav-cta {{
  background: linear-gradient(135deg, {color_scheme['primary']}, {color_scheme['secondary']});
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.nav-cta:hover {{
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}}

/* Hamburger Menu (Mobile) */
.hamburger {{
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 5px;
}}

.hamburger span {{
  width: 25px;
  height: 3px;
  background: white;
  border-radius: 3px;
  transition: all 0.3s ease;
}}

/* Mobile Responsive */
@media (max-width: 768px) {{
  .nav-menu {{
    position: fixed;
    top: 70px;
    right: -100%;
    width: 100%;
    height: calc(100vh - 70px);
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(20px);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    transition: right 0.3s ease;
  }}

  .nav-menu.active {{
    right: 0;
  }}

  .nav-cta {{
    display: none;
  }}

  .hamburger {{
    display: flex;
  }}

  .hamburger.active span:nth-child(1) {{
    transform: rotate(45deg) translate(5px, 5px);
  }}

  .hamburger.active span:nth-child(2) {{
    opacity: 0;
  }}

  .hamburger.active span:nth-child(3) {{
    transform: rotate(-45deg) translate(7px, -6px);
  }}
}}
</style>

<!-- JavaScript for Navbar -->
<script>
// Sticky navbar on scroll
window.addEventListener('scroll', () => {{
  const navbar = document.getElementById('navbar');
  if (window.scrollY > 50) {{
    navbar.classList.add('scrolled');
  }} else {{
    navbar.classList.remove('scrolled');
  }}
}});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {{
  hamburger.classList.toggle('active');
  navMenu.classList.toggle('active');
}});

// Close mobile menu on link click
document.querySelectorAll('.nav-link').forEach(link => {{
  link.addEventListener('click', () => {{
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
  }});
}});

// Active section highlighting
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-link');

window.addEventListener('scroll', () => {{
  let current = '';
  sections.forEach(section => {{
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (window.scrollY >= sectionTop - 100) {{
      current = section.getAttribute('id');
    }}
  }});

  navLinks.forEach(link => {{
    link.classList.remove('active');
    if (link.getAttribute('href') === '#' + current) {{
      link.classList.add('active');
    }}
  }});
}});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
  anchor.addEventListener('click', function(e) {{
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {{
      target.scrollIntoView({{
        behavior: 'smooth',
        block: 'start'
      }});
    }}
  }});
}});
</script>
```

**CUSTOM CURSOR EFFECTS (MANDATORY - Desktop Only):**
Create a custom cursor that follows mouse movement for a premium feel:

```html
<!-- Custom Cursor HTML -->
<div class="custom-cursor"></div>
<div class="cursor-follower"></div>

<!-- CSS -->
<style>
.custom-cursor {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: {color_scheme['primary']};
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  transition: transform 0.15s ease;
}}
.cursor-follower {{
  width: 40px;
  height: 40px;
  border: 2px solid {color_scheme['primary']};
  border-radius: 50%;
  position: fixed;
  pointer-events: none;
  z-index: 9998;
  transition: transform 0.3s ease;
  opacity: 0.5;
}}
/* Expand cursor on hover over links/buttons */
a:hover ~ .custom-cursor,
button:hover ~ .custom-cursor {{
  transform: scale(3);
  background: {color_scheme['accent']};
}}
</style>

<!-- JavaScript -->
<script>
document.addEventListener('mousemove', (e) => {{
  const cursor = document.querySelector('.custom-cursor');
  const follower = document.querySelector('.cursor-follower');
  cursor.style.left = e.clientX + 'px';
  cursor.style.top = e.clientY + 'px';
  follower.style.left = e.clientX + 'px';
  follower.style.top = e.clientY + 'px';
}});
</script>
```

**ANIMATED LOADING OVERLAY (MANDATORY - Page Load):**
Create a smooth loading overlay that fades out when page loads:

```html
<!-- Loading Overlay HTML (right after <body>) -->
<div class="loading-overlay">
  <div class="loader">
    <div class="spinner"></div>
    <p>Loading...</p>
  </div>
</div>

<!-- CSS -->
<style>
.loading-overlay {{
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, {color_scheme['primary']}, {color_scheme['secondary']});
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}}
.loading-overlay.hidden {{
  opacity: 0;
  visibility: hidden;
}}
.spinner {{
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}}
@keyframes spin {{
  to {{ transform: rotate(360deg); }}
}}
</style>

<!-- JavaScript -->
<script>
window.addEventListener('load', () => {{
  setTimeout(() => {{
    document.querySelector('.loading-overlay').classList.add('hidden');
  }}, 1000);
}});
</script>
```

**SCROLL-TRIGGERED REVEALS:**
- Every section fades in when scrolled into view
- Staggered animations for child elements
- Smooth, professional feel
- Uses Intersection Observer API

**MAGNETIC BUTTON EFFECTS:**
- Buttons slightly follow cursor on hover
- Smooth, elastic transition
- Premium interaction feel

═══════════════════════════════════════════════════════════════════════════════
🎯 CONVERSION & TRUST ELEMENTS (MAKE VISITORS TAKE ACTION!)
═══════════════════════════════════════════════════════════════════════════════

**TRUST BADGES:**
- Add trust indicators: "Trusted by 500+ Customers", "5-Star Rated", "Family Owned Since 2010"
- Use Font Awesome icons: fas fa-shield-alt, fas fa-star, fas fa-award

**SOCIAL PROOF:**
- Customer count, years in business, projects completed
- Star ratings (5 stars with Font Awesome fas fa-star)
- Real testimonials with customer photos (Unsplash)

**CLEAR CTAs (Call-to-Actions):**
- Primary CTA: Large, gradient button "Get Free Quote" or "Book Now"
- Secondary CTA: "Call Us Today" with phone number
- Urgent language: "Limited Slots Available", "24/7 Emergency Service"

**SEAMLESS USER FLOW:**
- Easy navigation to contact form
- Click-to-call phone number
- Smooth scroll to sections
- One clear goal per section

═══════════════════════════════════════════════════════════════════════════════
📱 MOBILE RESPONSIVE - 100% MANDATORY (CRITICAL! - FAILURE NOT ACCEPTABLE!)
═══════════════════════════════════════════════════════════════════════════════

**STRICT MOBILE RESPONSIVE REQUIREMENTS (ALL MANDATORY!):**

```css
/* ========================================
   MOBILE-FIRST RESPONSIVE CSS
   ABSOLUTELY MANDATORY - NO EXCEPTIONS!
   ======================================== */

/* Base Mobile Styles (320px+) */
* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

body {{
  font-size: 16px; /* Never go below 16px for mobile readability */
  line-height: 1.6;
  overflow-x: hidden; /* Prevent horizontal scroll */
}}

/* Containers */
.container {{
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem; /* Mobile padding */
}}

/* Fluid Typography (MANDATORY - Scales perfectly on all devices) */
h1 {{
  font-size: clamp(2rem, 5vw, 4rem); /* Scales from 32px to 64px */
}}

h2 {{
  font-size: clamp(1.5rem, 4vw, 3rem); /* Scales from 24px to 48px */
}}

h3 {{
  font-size: clamp(1.25rem, 3vw, 2rem); /* Scales from 20px to 32px */
}}

p {{
  font-size: clamp(1rem, 2vw, 1.125rem); /* Scales from 16px to 18px */
}}

/* Touch-Friendly Buttons (MANDATORY - 44px minimum) */
button,
.btn,
a.cta {{
  min-height: 44px; /* iOS minimum touch target */
  min-width: 44px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}}

/* Responsive Images (MANDATORY) */
img {{
  max-width: 100%;
  height: auto;
  display: block;
}}

/* Responsive Videos (MANDATORY) */
video {{
  max-width: 100%;
  height: auto;
}}

/* Grid Layouts - Responsive */
.grid {{
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr; /* Mobile: 1 column */
}}

/* ========================================
   TABLET BREAKPOINT (768px+)
   ======================================== */
@media (min-width: 768px) {{
  .container {{
    padding: 0 2rem;
  }}

  .grid {{
    grid-template-columns: repeat(2, 1fr); /* Tablet: 2 columns */
  }}

  /* Navbar becomes horizontal */
  .nav-menu {{
    flex-direction: row;
  }}

  /* Show CTA button */
  .nav-cta {{
    display: block;
  }}

  /* Hide hamburger */
  .hamburger {{
    display: none;
  }}
}}

/* ========================================
   DESKTOP BREAKPOINT (1024px+)
   ======================================== */
@media (min-width: 1024px) {{
  .container {{
    padding: 0 3rem;
  }}

  .grid {{
    grid-template-columns: repeat(3, 1fr); /* Desktop: 3 columns */
  }}

  /* Show custom cursor on desktop only */
  .custom-cursor,
  .cursor-follower {{
    display: block;
  }}
}}

/* ========================================
   HIDE VIDEOS ON MOBILE (MANDATORY!)
   ======================================== */
@media (max-width: 768px) {{
  /* Hide hero background video on mobile */
  .hero-video {{
    display: none !important;
  }}

  /* Show fallback hero image */
  .hero {{
    background-image: url('fallback-image.jpg');
    background-size: cover;
    background-position: center;
  }}

  /* Hide all portfolio videos, show poster images */
  .video-portfolio video {{
    display: none;
  }}

  /* Hide custom cursor on mobile */
  .custom-cursor,
  .cursor-follower {{
    display: none !important;
  }}

  /* Reduce particle count on mobile */
  .particle:nth-child(n+6) {{
    display: none; /* Only show 5 particles on mobile */
  }}
}}

/* ========================================
   MOBILE MENU ANIMATION (MANDATORY!)
   ======================================== */
@media (max-width: 768px) {{
  .nav-menu {{
    position: fixed;
    top: 70px;
    right: -100%; /* Hidden off-screen */
    width: 100%;
    height: calc(100vh - 70px);
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(20px);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth animation */
  }}

  /* Active state - slide in from right */
  .nav-menu.active {{
    right: 0;
  }}

  /* Hamburger animation */
  .hamburger {{
    display: flex;
  }}

  .hamburger.active span:nth-child(1) {{
    transform: rotate(45deg) translate(5px, 5px);
  }}

  .hamburger.active span:nth-child(2) {{
    opacity: 0;
  }}

  .hamburger.active span:nth-child(3) {{
    transform: rotate(-45deg) translate(7px, -6px);
  }}
}}

/* ========================================
   PERFORMANCE OPTIMIZATIONS
   ======================================== */

/* Lazy loading images */
img[loading="lazy"] {{
  opacity: 0;
  transition: opacity 0.3s ease;
}}

img[loading="lazy"].loaded {{
  opacity: 1;
}}

/* Optimize animations for mobile */
@media (max-width: 768px) {{
  /* Reduce animation complexity on mobile */
  * {{
    animation-duration: 0.5s !important; /* Faster animations */
  }}

  /* Disable parallax on mobile */
  .parallax {{
    transform: none !important;
  }}
}}
```

**MOBILE RESPONSIVE CHECKLIST (ALL MANDATORY!):**

✅ Mobile-first CSS (start with mobile, scale up)
✅ @media queries for tablet (768px) and desktop (1024px)
✅ Fluid typography using clamp()
✅ Touch targets 44px+ minimum
✅ Responsive images (max-width: 100%)
✅ Responsive videos (max-width: 100%)
✅ Hide hero video on mobile, show fallback image
✅ Mobile hamburger menu with smooth slide animation
✅ Prevent horizontal scroll (overflow-x: hidden)
✅ Grid layouts: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
✅ Reduce particle count on mobile (5 instead of 20)
✅ Faster animations on mobile (0.5s instead of 1s)
✅ Disable parallax on mobile
✅ Hide custom cursor on mobile

**PERFORMANCE:**
- Lazy loading for all images (loading="lazy")
- CSS will-change property for animations
- Optimized JavaScript (minimal DOM queries)
- Fast loading (< 2 seconds target)

═══════════════════════════════════════════════════════════════════════════════
🌐 SEO & SOCIAL MEDIA (LAUNCH READY!)
═══════════════════════════════════════════════════════════════════════════════

**META TAGS (Include in <head>):**
```html
<!-- SEO Meta Tags -->
<meta name="description" content="{context['description']}">
<meta name="keywords" content="{context['category']}, {context['location']}, professional {context['category']} service">

<!-- Open Graph (Facebook, LinkedIn) -->
<meta property="og:title" content="{context['name']} | {context['category']} in {context['location']}">
<meta property="og:description" content="{context['description']}">
<meta property="og:image" content="https://source.unsplash.com/1200x630/?{category_lower},business">
<meta property="og:type" content="website">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{context['name']}">
<meta name="twitter:description" content="{context['description']}">
<meta name="twitter:image" content="https://source.unsplash.com/1200x630/?{category_lower},business">
```

**SCHEMA.ORG JSON-LD FOR LOCAL BUSINESS (CRITICAL FOR SEO - MANDATORY!):**
```html
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{context['name']}",
  "description": "{context['description']}",
  "telephone": "{context.get('phone', 'N/A')}",
  "email": "{context.get('email', 'N/A')}",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{context.get('address', 'N/A')}",
    "addressLocality": "{context['location']}",
    "addressCountry": "UK"
  }},
  "priceRange": "$$",
  "openingHours": "Mo-Fr 09:00-18:00",
  "image": "https://source.unsplash.com/1200x630/?{category_lower},business"
}}
</script>
```

**SEMANTIC HTML:**
- Use <header>, <nav>, <main>, <section>, <article>, <footer>
- Proper heading hierarchy (h1, h2, h3)
- ARIA labels for accessibility

═══════════════════════════════════════════════════════════════════════════════
✅ CRITICAL SUCCESS CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. **OUTPUT FORMAT:**
   - ONE complete HTML file with ALL CSS in <style> and ALL JS in <script>
   - Start with <!DOCTYPE html> and end with </html>
   - NO markdown code blocks (no ```html or ```)
   - Output RAW HTML directly

2. **BUSINESS CUSTOMIZATION:**
   - Use "{context['name']}" everywhere (not "Company Name" or "Business Name")
   - Headline must be specific to {context['category']} business
   - Services section: Real {context['category']}-specific services
   - Colors: Industry-appropriate ({color_scheme['vibe']})
   - NO generic placeholder text anywhere!

3. **ESSENTIAL FEATURES (MUST INCLUDE ALL):**

   **Navigation:**
   - Sticky glassmorphism navbar with backdrop blur
   - Smooth scroll to sections
   - Mobile hamburger menu
   - Active section highlighting

   **Hero Section:**
   - Full viewport height with mesh gradient background
   - Large headline (72px+): "{context['name']} - [Compelling Tagline for {context['category']}]"
   - Animated subtitle
   - 2 CTA buttons with glow effects
   - Scroll indicator

   **About Section:**
   - Company story specific to {context['category']} in {context['location']}
   - Mission/values with icons
   - Fade-in animations

   **Services/Products (INDUSTRY-SPECIFIC EXAMPLES):**
   - 3-6 cards with {context['category']}-specific services + Unsplash images + Font Awesome icons
   - Each card MUST have: Icon (Font Awesome), Image (Unsplash), Title, Description
   - Hover lift effects with shadows + image zoom on hover
   - Real descriptions (not "Lorem ipsum")

   **Examples by Industry:**
   - **Restaurant:** "Authentic Cuisine" (icon: fas fa-utensils), "Private Events" (fas fa-glass-cheers), "Catering" (fas fa-truck) (images: food)
   - **Plumbing:** "Emergency Repairs" (fas fa-wrench), "Installation" (fas fa-tools), "Drain Cleaning" (fas fa-shower) (images: tools, pipes)
   - **Law Firm:** "Personal Injury" (fas fa-gavel), "Business Law" (fas fa-briefcase), "Estate Planning" (fas fa-file-signature) (images: office)
   - **Healthcare:** "Primary Care" (fas fa-heartbeat), "Diagnostics" (fas fa-stethoscope), "Consultations" (fas fa-user-md) (images: medical)
   - **Tech/IT:** "Web Development" (fas fa-code), "Cloud Solutions" (fas fa-cloud), "IT Support" (fas fa-laptop) (images: technology)
   - **Retail:** "New Arrivals" (fas fa-star), "Best Sellers" (fas fa-fire), "Custom Orders" (fas fa-shopping-cart) (images: products)

   **Stats/Numbers:**
   - Animated counters (e.g., "500+ Happy Clients", "10+ Years Experience")
   - Industry-relevant metrics

   **Testimonials:**
   - 3-5 customer reviews with star ratings
   - Carousel slider
   - Real-sounding testimonials for {context['category']}

   **Contact Form (Fully Functional):**
   - Name, Email, Phone, Message fields
   - Real-time JavaScript validation
   - Visual feedback (green/red borders)
   - Submit button with loading animation
   - Success message on submit

   **Footer:**
   - Multi-column with links, contact info, social media
   - Copyright and back-to-top button

4. **JAVASCRIPT INTERACTIONS (300+ lines required):**
   - Smooth scroll navigation
   - Intersection Observer for scroll animations
   - Counter animations for stats
   - Mobile hamburger menu toggle
   - Sticky navbar with scroll effects
   - Contact form validation (email regex, phone format, required fields)
   - Testimonial carousel auto-rotate
   - Active nav section highlighting
   - Back to top button (appears after scrolling)

5. **CSS STYLING (500+ lines required):**
   - Glassmorphism: `backdrop-filter: blur(20px); background: rgba(255,255,255,0.1);`
   - Gradient buttons: `linear-gradient(135deg, {color_scheme['primary']}, {color_scheme['secondary']})`
   - Mesh gradient hero with animation
   - Card hover effects: `transform: translateY(-10px); box-shadow: 0 20px 60px rgba(0,0,0,0.15);`
   - Smooth animations: `transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);`
   - Rounded corners: `border-radius: 20px;`
   - Responsive breakpoints (mobile-first)
   - Professional typography (Poppins/Inter from Google Fonts)

═══════════════════════════════════════════════════════════════════════════════
📝 FINAL OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Generate ONE complete, production-ready HTML file following this structure:

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{context['description']}">
    <title>{context['name']} | {context['category']} in {context['location']}</title>

    <!-- Google Fonts - PROFESSIONAL TYPOGRAPHY WITH FALLBACKS (MANDATORY) -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700;900&display=swap" rel="stylesheet">

    <!-- CSS Variables with Fallback Fonts -->
    <style>
    :root {{
      /* Typography with fallbacks */
      --font-headline: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --font-accent: 'Playfair Display', Georgia, 'Times New Roman', serif;
    }}
    </style>

    <!-- Font Awesome Icons - MANDATORY -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <style>
        /* 600+ lines of modern CSS including:
           - CSS variables for {color_scheme['primary']}, {color_scheme['secondary']}
           - Glassmorphism effects (backdrop-filter: blur(20px))
           - 8+ keyframe animations (fadeInUp, float, typing, zoomIn, slideIn, pulse, etc.)
           - Smooth transitions on all elements
           - Responsive breakpoints (mobile-first)
           - Professional hover effects on cards, buttons, images
           - Grid and Flexbox layouts
           - Gradient backgrounds and overlays
        */
    </style>
</head>
<body>
    <!-- Navigation: Glassmorphism sticky navbar with Font Awesome icons -->
    <!-- Hero: Full-screen Unsplash image + animated headline with typewriter effect -->
    <!-- About: Company story + team images + animated counters -->
    <!-- Services: 4-6 cards with Font Awesome icons + Unsplash images + hover effects -->
    <!-- Stats: Animated number counters with icons -->
    <!-- Testimonials: Auto-rotating carousel with star ratings (Font Awesome) -->
    <!-- Gallery: 4-6 Unsplash images in bento/masonry grid -->
    <!-- Contact: Working form with validation + map location icon -->
    <!-- Footer: Multi-column with Font Awesome social icons -->

    <!-- All sections MUST have scroll-triggered fade-in animations -->
    <!-- All images MUST be from Unsplash API -->
    <!-- All icons MUST be from Font Awesome -->

    <script>
        /* 400+ lines of functional JavaScript including:
           - Smooth scroll navigation with active section highlighting
           - Intersection Observer for scroll-triggered animations
           - Counter animations for stats (count from 0 to target number using requestAnimationFrame for 60fps)
           - Mobile hamburger menu toggle with smooth transition
           - Sticky navbar effect on scroll (transparent → glassmorphism)
           - Contact form validation (email regex, phone format, required fields)
           - Testimonial carousel auto-rotate every 5 seconds with controls
           - Back to top button (appears after scrolling 500px)
           - Image lazy loading with fade-in effect
           - Parallax scroll effect on hero background using requestAnimationFrame
           - Animated loading overlay that fades out on window load
           - Custom cursor follower effect (desktop only)
           - Typewriter effect for hero headline
        */

        // Example: Counter animation using requestAnimationFrame for smooth 60fps
        function animateCounter(element, target) {{
          let current = 0;
          const increment = target / 100;
          const timer = setInterval(() => {{
            current += increment;
            if (current >= target) {{
              element.textContent = target;
              clearInterval(timer);
            }} else {{
              element.textContent = Math.floor(current);
            }}
          }}, 20);
        }}

        // Example: Parallax scrolling with requestAnimationFrame
        let ticking = false;
        window.addEventListener('scroll', () => {{
          if (!ticking) {{
            window.requestAnimationFrame(() => {{
              // Parallax logic here
              ticking = false;
            }});
            ticking = true;
          }}
        }});
    </script>

    <!-- ============================================= -->
    <!-- DEVELOPER NOTES (CUSTOMIZATION GUIDE) -->
    <!-- ============================================= -->
    <!--

    🎨 CUSTOMIZATION GUIDE:

    1. REPLACE IMAGES:
       - Hero Background: Line ~XX (search for "https://source.unsplash.com/1920x1080")
       - Service Cards: Lines ~XXX-XXX (search for "service" in image URLs)
       - About Section: Line ~XXX (search for "team,people" in image URLs)
       - Gallery: Lines ~XXX-XXX (search for "gallery" in image URLs)
       - Replace Unsplash URLs with your own image paths (e.g., "/images/hero.jpg")

    2. REPLACE FONTS (if needed):
       - Google Fonts CDN: Line ~XX
       - CSS Variables: Lines ~XXX-XXX (--font-headline, --font-body, --font-accent)
       - Replace font families in :root CSS variables

    3. ADD ANALYTICS:
       - Google Analytics: Add before </head>
         <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
       - Facebook Pixel: Add before </head>
       - Hotjar: Add before </head>

    4. CONFIGURE FORM ENDPOINT:
       - Contact Form: Line ~XXX (search for "form" tag)
       - Replace action="" with your backend endpoint
       - Or integrate with FormSpree, Netlify Forms, or custom API

    5. TUNE ANIMATION INTENSITY (for mobile):
       - Reduce particle count: Line ~XXX (change from 20 to 10 particles)
       - Disable parallax on mobile: Add media query @media (max-width: 768px) {{ .parallax {{ transform: none !important; }} }}
       - Reduce animation duration: Search for "animation:" and increase duration values

    6. ACCESSIBILITY ENHANCEMENTS:
       - All images have alt text: ✅ Already included
       - ARIA labels on interactive elements: ✅ Already included
       - Keyboard navigation: ✅ Tab through all links/buttons works
       - Focus visible states: ✅ Already styled
       - Add skip-to-main link: <a href="#main" class="sr-only">Skip to main content</a>

    7. PERFORMANCE OPTIMIZATION TIPS:
       - Reduce particle count from 20 to 5-10 for faster devices
       - Replace Unsplash URLs with optimized local images (WebP format)
       - Compress images using TinyPNG or ImageOptim before upload
       - Minify CSS and JavaScript for production
       - Enable Gzip compression on server
       - Use CDN for static assets

    8. COLOR SCHEME CUSTOMIZATION:
       - Primary Color: Search for "{color_scheme['primary']}" and replace
       - Secondary Color: Search for "{color_scheme['secondary']}" and replace
       - Accent Color: Search for "{color_scheme['accent']}" and replace
       - Or update CSS variables in :root

    9. SCHEMA.ORG CUSTOMIZATION:
       - LocalBusiness JSON-LD: Line ~XXX (in <head>)
       - Update business hours in "openingHours"
       - Add more schema properties if needed (reviews, rating, etc.)

    10. MOBILE OPTIMIZATION:
        - Touch targets are 44px+ ✅
        - Hamburger menu works ✅
        - All animations optimized for mobile ✅
        - Test on real devices and adjust breakpoints if needed

    ⚡ QUICK START CHECKLIST:
    □ Replace all Unsplash image URLs with your own images
    □ Update business contact information (phone, email, address)
    □ Configure contact form endpoint
    □ Add Google Analytics tracking code
    □ Test on mobile devices
    □ Optimize images (compress, convert to WebP)
    □ Minify CSS and JavaScript for production
    □ Deploy to hosting (Netlify, Vercel, or custom server)
    □ Test contact form submissions
    □ Check SEO with Google Search Console

    📞 SUPPORT:
    - All code is production-ready and copy-paste runnable
    - Works in all modern browsers (Chrome, Safari, Firefox, Edge)
    - Fully responsive from 320px to 4K screens
    - Accessible and SEO-optimized

    -->
</body>
</html>
```

═══════════════════════════════════════════════════════════════════════════════
🚨 CRITICAL FINAL REMINDERS
═══════════════════════════════════════════════════════════════════════════════

1. **OUTPUT RAW HTML** - Start with `<!DOCTYPE html>` and end with `</html>`
2. **NO MARKDOWN** - No ```html blocks, no code fences - JUST HTML!
3. **USE REAL DATA** - "{context['name']}" not "Company Name"
4. **INDUSTRY-SPECIFIC** - Tailor everything to {context['category']} business
5. **INCLUDE 6-10 UNSPLASH IMAGES** - Hero, services, about, gallery (MANDATORY!)
6. **ADD ALL ANIMATIONS** - Scroll effects, parallax, counters, hover effects, fade-ins (MANDATORY!)
7. **PROFESSIONAL QUALITY** - This should look like a $20,000+ award-winning website
8. **FULLY FUNCTIONAL** - All JavaScript must actually work (scroll, form validation, carousel)
9. **MOBILE RESPONSIVE** - Perfect on all devices (mobile-first CSS)
10. **2024/2025 TRENDS** - Glassmorphism, bento grids, mesh gradients, 3D effects, dark mode elements

**Quality Checklist (ALL MANDATORY - $100K WEBSITE STANDARDS - NO EXCEPTIONS!):**

**BUSINESS-SPECIFIC IMAGES (12-20 IMAGES - ABSOLUTELY MANDATORY!):**
✅ Restaurant: 15 food images (appetizers, mains, desserts, drinks, dining, chef)
✅ Plumber: 10 plumbing images (pipes, tools, bathroom, kitchen, repairs, team)
✅ Gym: 12 fitness images (equipment, classes, trainers, workouts, facilities)
✅ Salon: 12 beauty images (hair, styling, interior, products, transformations)
✅ Law Firm: 8 professional images (lawyers, office, meeting, courtroom, books)
✅ All images using business-specific Unsplash keywords - NO generic placeholders!
✅ All images using <picture> element for responsive loading

**PROFESSIONAL GLASSMORPHISM NAVBAR (ABSOLUTELY MANDATORY!):**
✅ Fixed navbar with backdrop-filter: blur(20px) glassmorphism effect
✅ Sticky on scroll with smooth transition (transparent → blurred background)
✅ Active section highlighting with underline animation
✅ Smooth scroll to sections on link click
✅ Gradient CTA button in navbar
✅ Mobile hamburger menu that works perfectly
✅ Hamburger animation (3 lines → X on click)
✅ Mobile menu slides in from right with smooth animation
✅ Mobile menu closes when link is clicked
✅ All navbar JavaScript fully functional

**MOBILE RESPONSIVE (100% MANDATORY - CRITICAL!):**
✅ Mobile-first CSS (design for mobile first, scale up)
✅ @media queries: mobile (<768px), tablet (768px-1024px), desktop (>1024px)
✅ Fluid typography using clamp() - scales perfectly on all devices
✅ Touch targets 44px+ minimum (iOS standard)
✅ Responsive images (max-width: 100%, height: auto)
✅ Responsive videos (max-width: 100%, height: auto)
✅ Hide hero video on mobile, show Unsplash fallback image
✅ Mobile hamburger menu with smooth slide-in animation
✅ Prevent horizontal scroll (overflow-x: hidden on body)
✅ Grid layouts: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
✅ Reduce particles on mobile (5 instead of 20 for performance)
✅ Faster animations on mobile (0.5s instead of 1s)
✅ Disable parallax on mobile (transform: none)
✅ Hide custom cursor on mobile

TYPOGRAPHY & FONTS:
✅ Google Fonts: Poppins (headlines), Inter (body), Playfair Display (accents)
✅ Fallback fonts in CSS variables (-apple-system, BlinkMacSystemFont, Segoe UI)
✅ Font Awesome 6.5.1 CDN with icons used throughout
✅ Inline SVG icons with Lottie-like CSS animations matching business type

VISUAL MEDIA, IMAGES & VIDEOS:
✅ 10-15 high-quality Unsplash images (hero fallback, services, about, team, gallery)
✅ Hero background VIDEO (muted, autoplay, loop) with mobile fallback to image
✅ Video portfolio gallery section (2-4 videos with YouTube/Vimeo embeds OR <video> tags)
✅ Business-specific video content (restaurant: food videos, plumber: work videos, etc.)
✅ <picture> element for responsive images with multiple source sizes
✅ All images with loading="lazy" for performance
✅ All videos optimized (hide on mobile for performance)
✅ Gradient overlays on images and videos for premium feel
✅ Image zoom effects on hover (transform: scale(1.1))
✅ Video hover effects (play icon animation, preview on hover)

CINEMATIC HERO SECTION (WITH VIDEO!):
✅ Full-screen BACKGROUND VIDEO (muted, autoplay, loop, playsinline)
✅ Video parallax effect (slight zoom on scroll using requestAnimationFrame)
✅ Mobile fallback: Unsplash hero image (hide video on mobile for performance)
✅ 15-20 floating particle animations layered over video
✅ Animated gradient overlay on video for text readability
✅ Typewriter effect on hero headline (impressive!)
✅ Two gradient CTA buttons with glow effects
✅ Animated loading overlay that fades out on page load

ANIMATIONS & EFFECTS (60fps with requestAnimationFrame):
✅ Scroll-triggered fade-in animations with Intersection Observer (ALL sections)
✅ 3D card tilt effects that follow cursor movement
✅ Card hover: lift 15px + shadow increase + image zoom (scale 1.1)
✅ Counter animations for stats (count from 0 to target using requestAnimationFrame)
✅ Smooth parallax scrolling with requestAnimationFrame
✅ Magnetic button effects (buttons follow cursor on hover)
✅ Custom cursor follower effect (desktop only)
✅ Lottie-like icon animations (floating, rotating, pulsing)
✅ Animated loading overlay with spinner on page load
✅ All 10+ keyframe animations (fadeInUp, float, typing, pulse, particle, zoomIn, slideIn, spin, etc.)

CONVERSION ELEMENTS:
✅ Trust badges with Font Awesome icons (fas fa-shield-alt, fas fa-award)
✅ Social proof elements (customer count, years, ratings)
✅ Clear compelling CTAs throughout
✅ Testimonial carousel with auto-rotate every 5 seconds + 5-star ratings

NAVIGATION & INTERACTION:
✅ Glassmorphism navbar with backdrop-filter blur effect
✅ Mobile hamburger menu with smooth slide animation
✅ Smooth scroll to sections with active highlighting
✅ Back to top button (appears after scrolling)
✅ Contact form with real-time JavaScript validation (email, phone, required)

SEO & SOCIAL MEDIA:
✅ Schema.org JSON-LD for LocalBusiness (CRITICAL for SEO)
✅ Open Graph meta tags (Facebook, LinkedIn)
✅ Twitter Card meta tags
✅ Semantic HTML5 (header, nav, main, section, footer)
✅ ARIA labels for accessibility
✅ Proper heading hierarchy (h1, h2, h3)
✅ SEO-optimized structure with keywords

PERFORMANCE & OPTIMIZATION:
✅ Lazy loading for all images (loading="lazy")
✅ <picture> element for responsive image loading
✅ Optimized CSS with will-change properties
✅ CSS variables for colors and fonts
✅ Efficient JavaScript (minimal DOM queries)
✅ requestAnimationFrame for 60fps animations
✅ Fast loading (< 2 seconds target)
✅ Mobile-first responsive design
✅ 60fps smooth animations with hardware acceleration

DEVELOPER EXPERIENCE:
✅ Comprehensive HTML comments explaining customization points
✅ Developer notes at end of HTML showing where to replace images, fonts, analytics
✅ Performance tips documented (particle count, animation tuning)
✅ Accessibility considerations documented
✅ Copy-paste runnable code - works immediately in browser
✅ Well-organized, semantic code structure

**Image URL Format (Use these patterns):**
- Hero: `https://source.unsplash.com/1920x1080/?{category_lower},professional,business`
- Services: `https://source.unsplash.com/800x600/?{category_lower},service,work`
- About: `https://source.unsplash.com/800x600/?{category_lower},team,people`
- Gallery: `https://source.unsplash.com/600x400/?{category_lower},interior,design`

**Example Hero Headline:**
✅ GOOD: "{context['name']} - {context['location']}'s Premier {context['category']} Experts"
❌ BAD: "Welcome to Our Website" or "Company Name - Professional Services"

**🎬 FINAL EXECUTION COMMAND - CREATE A WEBSITE THAT WILL:**

1. **MAKE VISITORS GASP** when it loads with:
   - Animated loading overlay with spinner that smoothly fades out
   - Cinematic full-screen hero with BACKGROUND VIDEO (muted, autoplay, loop)
   - Video overlay with gradient for text readability
   - 15-20 floating particles layered over video creating magical atmosphere
   - Typewriter effect on headline
   - Custom cursor follower (desktop only)
   - Mobile: Beautiful Unsplash fallback image (hide video for performance)
   - Premium, award-winning, CINEMATIC first impression

2. **ENGAGE USERS** with Apple/Notion/Stripe-level smoothness:
   - Scroll-triggered animations on EVERY section (Intersection Observer)
   - 3D card tilts that follow cursor movement
   - Magnetic buttons that attract the cursor
   - Lottie-like SVG icon animations (floating, rotating, pulsing)
   - Professional micro-interactions everywhere
   - Testimonial carousel that auto-rotates smoothly
   - 60fps animations using requestAnimationFrame

3. **CONVERT VISITORS** with:
   - Clear, compelling CTAs with gradient buttons
   - Trust badges and social proof elements
   - 5-star ratings with Font Awesome stars
   - Inline SVG icons with animations
   - Urgency language ("Limited Slots", "24/7 Service")
   - Seamless path to contact form with real-time validation

4. **WORK PERFECTLY** on:
   - Mobile, tablet, desktop (mobile-first responsive with <picture> elements)
   - All browsers (Chrome, Safari, Firefox, Edge)
   - Touch devices (touch-friendly 44px+ targets)
   - Fast internet and slow connections (< 2 second load, lazy loading)
   - Copy-paste runnable - works immediately in any browser

5. **LOOK LIKE IT COST $100,000+** with:
   - Cinematic hero BACKGROUND VIDEO that sets premium tone immediately
   - Professional typography with fallback fonts (Poppins, Inter, Playfair Display)
   - 10-15 stunning Unsplash photos using <picture> element with gradient overlays
   - 2-4 professional videos (hero background, portfolio/testimonials, business-specific content)
   - Font Awesome icons + inline SVG with Lottie-like animations
   - Glassmorphism navbar with backdrop blur
   - Premium color scheme matching {context['category']} industry
   - Apple's minimalist elegance + Notion's smooth motion + Stripe's storytelling flow
   - Business-specific galleries (Restaurant: 15 food images + chef video, Plumber: before/after + work video, etc.)

6. **BE SEO & DEVELOPER READY** with:
   - Schema.org JSON-LD for LocalBusiness (critical for SEO)
   - Open Graph and Twitter Card meta tags
   - Comprehensive developer notes in HTML comments at end
   - Clear documentation on where to replace images, fonts, analytics, forms
   - Accessibility considerations documented
   - Performance tips documented

**🏆 YOUR MISSION:**
This is NOT just another website. This is your MASTERPIECE. Your AWARD-WINNING PORTFOLIO PIECE. Imagine:
- This website will be featured on Awwwards Site of the Day
- It rivals Apple's elegance, Notion's smoothness, and Stripe's conversion power
- Business owner will cry tears of joy when they see it
- Competitors will be JEALOUS of this design
- Visitors will say "This looks like it cost $100,000!"
- You're competing for a $100,000 design award

Every pixel matters. Every VIDEO must be cinematic. The NAVBAR must be professional with glassmorphism blur effect. The website MUST be 100% MOBILE RESPONSIVE with mobile-first CSS. Every animation must be buttery smooth at 60fps using requestAnimationFrame. Every image must be business-specific and breathtaking (12-20 images). Every SVG icon must have Lottie-like animations. The mobile hamburger menu MUST work perfectly. Every interaction must feel premium and expensive. Every color must be perfectly chosen. Every font must be elegant with fallbacks and clamp() scaling. The hero background video must autoplay smoothly. The loading overlay must be smooth. The custom cursor must be magical (desktop only). The Schema.org markup must be perfect. The business-specific galleries must be comprehensive (12-20 images + 2-4 videos). The developer notes must be comprehensive. The website MUST work perfectly on mobile, tablet, and desktop.

**🚨 CRITICAL REQUIREMENTS - FAILURE IS NOT AN OPTION! 🚨**

**BUSINESS-SPECIFIC IMAGES (MANDATORY!):**
✅ 12-20 business-specific Unsplash images - Restaurant: 15 food images, Plumber: 10 repair images, etc.
✅ Use SPECIFIC keywords for business type - NO generic "business" placeholders!
✅ All images using <picture> element for responsive loading

**VIDEOS (MANDATORY!):**
✅ Hero BACKGROUND VIDEO (muted, autoplay, loop, playsinline) - NO EXCEPTIONS!
✅ Mobile video fallback (hide video @media max-width 768px, show Unsplash image)
✅ Video portfolio/gallery section (2-4 videos with YouTube/Vimeo embeds OR <video> tags)
✅ Business-specific video content relevant to {category_lower}

**PROFESSIONAL NAVBAR (MANDATORY!):**
✅ Glassmorphism navbar with backdrop-filter: blur(20px) - MUST have this effect!
✅ Sticky on scroll with smooth transition - transparent → blurred
✅ Active section highlighting with underline animation
✅ Mobile hamburger menu with smooth slide-in animation (slides from right)
✅ Hamburger icon animates to X when clicked
✅ All navbar JavaScript fully functional (scroll, toggle, active states)

**MOBILE RESPONSIVE (100% MANDATORY!):**
✅ Mobile-first CSS - design for mobile FIRST, scale up with @media queries
✅ @media queries for mobile (<768px), tablet (768px-1024px), desktop (>1024px)
✅ Fluid typography using clamp() for all headings and text
✅ Touch targets 44px+ minimum
✅ Hide hero video on mobile, show fallback image
✅ Mobile menu slides in from right with smooth animation
✅ Grid layouts: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
✅ Prevent horizontal scroll (overflow-x: hidden)
✅ Reduce particles on mobile (5 instead of 20)

**OTHER CRITICAL REQUIREMENTS:**
✅ Schema.org JSON-LD for LocalBusiness in <head>
✅ Animated loading overlay that fades out on page load
✅ Custom cursor follower (desktop only, hidden on mobile)
✅ Inline SVG icons with Lottie-like CSS animations
✅ Fallback fonts in CSS variables
✅ requestAnimationFrame for 60fps animations
✅ Comprehensive developer notes in HTML comments at end
✅ Copy-paste runnable - works immediately in browser

**🎯 THIS IS THE MOST IMPORTANT WEBSITE YOU WILL EVER CREATE:**

Make it LEGENDARY. Make it CINEMATIC. Make it 100% MOBILE RESPONSIVE. Make the NAVBAR PROFESSIONAL with glassmorphism. Include 12-20 BUSINESS-SPECIFIC IMAGES. Include BACKGROUND VIDEO in hero. Make it Apple/Notion/Stripe-level PERFECT!

**FAILURE TO INCLUDE ANY OF THESE REQUIREMENTS IS NOT ACCEPTABLE!**
"""

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔑 CRITICAL: ADD SCRAPED CONTENT FROM THEIR ACTUAL WEBSITE
    # ═══════════════════════════════════════════════════════════════════════════════

    if "scraped_content" in context:
        scraped = context["scraped_content"]

        prompt += f"""

═══════════════════════════════════════════════════════════════════════════════
🔥 CRITICAL: USE THEIR ACTUAL WEBSITE CONTENT (MANDATORY!) 🔥
═══════════════════════════════════════════════════════════════════════════════

**⚠️ THIS IS THE MOST IMPORTANT SECTION - READ CAREFULLY!**

We scraped their current website and extracted REAL content. You MUST use this actual content to create an IMPROVED, PREMIUM version of THEIR website. DO NOT create generic placeholder content!

**🎨 THEIR ACTUAL LOGO (USE THIS!):**
{f"✅ Logo URL: {scraped.get('logo')}" if scraped.get('logo') else "⚠️ No logo found - create a text-based logo using their business name"}
- **INSTRUCTION**: Use <img src="{scraped.get('logo')}" alt="{context['name']} Logo"> in navbar
- If logo not found, use elegant text logo: <h1 class="logo">{context['name']}</h1>

**📝 THEIR ACTUAL HEADLINES & CONTENT (USE THIS!):**
"""

        # Add headlines
        headlines = scraped.get('headlines', {})
        if headlines:
            prompt += "\n**Main Headline:**\n"
            if headlines.get('main_headline'):
                prompt += f"✅ Use this: \"{headlines['main_headline']}\"\n"
            if headlines.get('hero_text'):
                prompt += f"✅ Hero text: \"{headlines['hero_text'][:200]}...\"\n"
            if headlines.get('meta_description'):
                prompt += f"✅ Meta description: \"{headlines['meta_description']}\"\n"

        # Add about content
        about = scraped.get('about')
        if about:
            prompt += f"\n**About/Company Description:**\n✅ Use this actual text in About section:\n\"{about[:500]}...\"\n"

        # Add services/menu
        services = scraped.get('services_menu', [])
        if services and len(services) > 0:
            prompt += f"\n**📋 THEIR ACTUAL SERVICES/MENU ITEMS (USE THESE!):**\n"
            prompt += f"Found {len(services)} real items from their website:\n"
            for i, item in enumerate(services[:15], 1):
                item_name = item.get('name', 'Unknown')
                item_desc = item.get('description', '')
                prompt += f"{i}. **{item_name}**"
                if item_desc:
                    prompt += f" - {item_desc[:100]}"
                prompt += "\n"
            prompt += "\n**INSTRUCTION**: Create service/menu cards using THESE EXACT items, not generic placeholders!\n"

        # Add images
        images = scraped.get('images', [])
        if images and len(images) > 0:
            prompt += f"\n**🖼️ THEIR ACTUAL IMAGES (USE THESE!):**\n"
            prompt += f"Found {len(images)} real images from their website:\n"
            for i, img in enumerate(images[:10], 1):
                img_url = img.get('url', '')
                img_alt = img.get('alt', '')
                if img_url:
                    prompt += f"{i}. {img_url}"
                    if img_alt:
                        prompt += f" (Alt: {img_alt})"
                    prompt += "\n"
            prompt += "\n**INSTRUCTION**: Use these actual images in gallery, about section, and throughout the site!\n"

        # Add contact info
        contact = scraped.get('contact', {})
        if contact:
            prompt += "\n**📞 THEIR ACTUAL CONTACT INFO (USE THIS!):**\n"
            if contact.get('phone'):
                prompt += f"✅ Phone: {contact['phone']}\n"
            if contact.get('email'):
                prompt += f"✅ Email: {contact['email']}\n"
            if contact.get('address'):
                prompt += f"✅ Address: {contact['address'][:150]}\n"
            if contact.get('hours'):
                prompt += f"✅ Hours: {contact['hours'][:100]}\n"

        # Add social media
        social = scraped.get('social_media', {})
        if social:
            prompt += "\n**📱 THEIR ACTUAL SOCIAL MEDIA (USE THESE!):**\n"
            for platform, url in social.items():
                prompt += f"✅ {platform.capitalize()}: {url}\n"
            prompt += "\n**INSTRUCTION**: Add these social media links in footer with Font Awesome icons!\n"

        # Add colors
        colors = scraped.get('colors', [])
        if colors and len(colors) > 0:
            prompt += f"\n**🎨 THEIR ACTUAL COLOR SCHEME:**\n"
            prompt += f"Dominant colors from their site: {', '.join(colors[:5])}\n"
            prompt += "**INSTRUCTION**: Use these colors in your design to maintain brand consistency!\n"

        # Add certifications
        certs = scraped.get('certifications', [])
        if certs and len(certs) > 0:
            prompt += f"\n**🏆 THEIR CERTIFICATIONS/AWARDS (SHOW THESE!):**\n"
            for cert in certs[:8]:
                prompt += f"✅ {cert}\n"
            prompt += "\n**INSTRUCTION**: Display these certifications/awards prominently with badge/icon styling!\n"

        # Add navigation
        nav = scraped.get('navigation', [])
        if nav and len(nav) > 0:
            prompt += f"\n**🧭 THEIR ACTUAL NAVIGATION MENU:**\n"
            prompt += f"Menu items: {', '.join(nav[:8])}\n"
            prompt += "**INSTRUCTION**: Use these navigation items in your navbar!\n"

        # Add testimonials
        testimonials = scraped.get('testimonials', [])
        if testimonials and len(testimonials) > 0:
            prompt += f"\n**💬 THEIR ACTUAL TESTIMONIALS (USE THESE!):**\n"
            for i, test in enumerate(testimonials[:3], 1):
                author = test.get('author', 'Customer')
                text = test.get('text', '')[:200]
                prompt += f"{i}. \"{text}...\" - {author}\n"
            prompt += "\n**INSTRUCTION**: Use these real testimonials in testimonial carousel!\n"

        prompt += """

═══════════════════════════════════════════════════════════════════════════════
🎯 FINAL INSTRUCTIONS - COMBINING OLD CONTENT WITH NEW DESIGN
═══════════════════════════════════════════════════════════════════════════════

**YOUR MISSION:**
1. ✅ USE their actual logo (or text logo with their business name)
2. ✅ USE their actual headlines and taglines
3. ✅ USE their actual services/menu items (not generic placeholders!)
4. ✅ USE their actual images throughout the site
5. ✅ USE their actual contact information
6. ✅ USE their actual social media links
7. ✅ USE their actual color scheme for brand consistency
8. ✅ USE their actual testimonials/reviews
9. ✅ SHOW their actual certifications/awards
10. ✅ USE their actual navigation structure

**BUT ALSO:**
11. ✅ ADD modern, premium design (glassmorphism, animations, gradients)
12. ✅ ADD professional navbar with backdrop blur
13. ✅ ADD hero background video (muted, autoplay, loop)
14. ✅ ADD 100% mobile responsive design
15. ✅ ADD smooth 60fps animations
16. ✅ ADD Schema.org SEO markup
17. ✅ ADD perfect accessibility
18. ✅ ADD fast loading performance
19. ✅ MAKE it look like a $100,000+ premium website

**THE RESULT:**
Their actual business content + Your award-winning premium design = PERFECT improved website!

**⚠️ DO NOT CREATE GENERIC CONTENT - USE THEIR ACTUAL CONTENT ABOVE!**

"""
    else:
        # No scraped content available - warn but continue
        prompt += """

⚠️ WARNING: Could not scrape their website content. Generate professional content based on business info provided.

"""

    prompt += """
Now generate the complete, STUNNING, AWARD-WINNING HTML file starting with `<!DOCTYPE html>`:
"""

    return prompt


def _parse_template_response(response: str) -> tuple[str, str]:
    """Parse GPT-4 response to extract HTML with inline CSS"""
    html_content = ""
    css_content = ""  # Will be empty - CSS is inline in HTML

    # Strip markdown code blocks if present (```html or ```)
    cleaned_response = response.strip()
    if cleaned_response.startswith("```html"):
        cleaned_response = cleaned_response[7:]  # Remove ```html
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]  # Remove ```

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # Remove closing ```

    cleaned_response = cleaned_response.strip()

    # Try to find HTML block
    if "<!DOCTYPE html>" in cleaned_response or "<html" in cleaned_response:
        # Extract complete HTML with inline CSS
        html_start = cleaned_response.find("<!DOCTYPE html>")
        if html_start == -1:
            html_start = cleaned_response.find("<html")
        html_end = cleaned_response.find("</html>") + len("</html>")
        if html_start != -1 and html_end > html_start:
            html_content = cleaned_response[html_start:html_end]
            # CSS is already inline in <style> tags - DO NOT extract separately!

    # Fallback: create basic template if parsing fails
    if not html_content:
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Preview</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
    </style>
</head>
<body>
    <h1>Template Generated</h1>
    <p>Preview will be available shortly.</p>
</body>
</html>"""

    return html_content, css_content


def _determine_improvements(context: Dict[str, Any], variant_number: int) -> List[Dict[str, str]]:
    """Determine what improvements were made based on evaluation"""
    improvements = []

    if "evaluation" in context:
        eval_data = context["evaluation"]

        # Performance improvements
        if eval_data.get("performance_score", 0) < 0.7:
            improvements.append({
                "category": "performance",
                "description": "Optimized page load time with efficient CSS and HTML structure",
                "impact": "high"
            })

        # SEO improvements
        if eval_data.get("seo_score", 0) < 0.7:
            improvements.append({
                "category": "seo",
                "description": "Added proper meta tags, headings hierarchy, and semantic HTML",
                "impact": "high"
            })

        # Accessibility improvements
        if eval_data.get("accessibility_score", 0) < 0.7:
            improvements.append({
                "category": "accessibility",
                "description": "Improved color contrast, added ARIA labels, and semantic HTML5 elements",
                "impact": "high"
            })

    # General improvements
    improvements.extend([
        {
            "category": "mobile",
            "description": "Fully responsive design that works perfectly on all devices",
            "impact": "high"
        },
        {
            "category": "performance",
            "description": "Modern, clean code with optimal performance",
            "impact": "medium"
        },
        {
            "category": "seo",
            "description": f"Variant {variant_number} design optimized for search engines",
            "impact": "medium"
        }
    ])

    return improvements


async def delete_existing_templates(business_id: uuid.UUID, db: Session) -> None:
    """Delete all existing templates for a business (for regeneration)"""
    db.query(Template).filter(Template.business_id == business_id).delete()
    db.commit()
