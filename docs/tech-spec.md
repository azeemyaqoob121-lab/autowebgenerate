# AutoWeb_Outreach_AI - Technical Specification

**Author:** azeem yaqoob
**Date:** 2025-11-06
**Project Level:** 1 (Coherent Feature Enhancement)
**Project Type:** Feature Enhancement
**Development Context:** Brownfield - Enhancing existing template generation service

---

## Source Tree Structure

```
AutoWeb_Outreach_AI/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── template_generator.py          # PRIMARY: Major enhancement
│   │   │   ├── premium_template_builder.py    # NEW: Premium HTML generator
│   │   │   ├── media_sourcing_service.py      # NEW: Unsplash/video integration
│   │   │   └── website_scraper.py             # MODIFY: Enhanced scraping
│   │   ├── prompts/
│   │   │   ├── premium_website_prompt.txt     # NEW: Elite designer prompt
│   │   │   └── niche_templates/               # NEW: Business-specific prompts
│   │   │       ├── restaurant_template.txt
│   │   │       ├── service_business_template.txt
│   │   │       ├── professional_services_template.txt
│   │   │       └── retail_template.txt
│   │   ├── models/
│   │   │   └── template.py                    # MODIFY: Add media_assets field
│   │   └── config.py                          # MODIFY: Add Unsplash API key
│   └── requirements.txt                        # ADD: pyunsplash==1.0.0rc1
├── docs/
│   ├── newwebsitebestversiontoseeoldwebsitewhichscraps.txt  # Source requirements
│   └── tech-spec.md                           # This document
└── tests/
    └── test_premium_templates.py              # NEW: Template quality tests
```

---

## Technical Approach

### Overview
Transform the existing basic template generation system into a **premium website generation engine** that produces $50,000+ quality websites. The approach involves:

1. **Enhanced Prompt Engineering**: Replace generic prompts with elite-level designer instructions
2. **Structured Template Generation**: Build templates programmatically with guaranteed elements
3. **Media Integration Layer**: Automatically source and integrate premium images/videos
4. **Business-Niche Specialization**: Different template strategies per business type
5. **Quality Assurance**: Validate generated HTML against premium standards checklist

### Architecture Decision
**Hybrid Approach: AI + Structured Generation**

Instead of relying solely on GPT-4 to generate complete HTML (which produces inconsistent results), we'll use:
- **GPT-4 for**: Content enhancement, copywriting, design decisions, color schemes
- **Python code for**: Structural HTML/CSS/JS generation, ensuring all mandatory features are present

This ensures **100% feature compliance** while maintaining AI creativity for content.

---

## Implementation Stack

### Core Technologies
- **Python**: 3.11.x (existing)
- **OpenAI API**: GPT-4 Turbo (gpt-4-0125-preview) - enhanced prompts
- **Template Engine**: Jinja2 3.1.2 - for programmatic HTML generation
- **Media APIs**:
  - Unsplash API (pyunsplash 1.0.0rc1) - for premium business images
  - Pexels API (fallback) - for video content
  - Font Awesome 6.5.1 CDN - for icons

### Data Processing
- **BeautifulSoup4** 4.12.x - enhanced website scraping
- **lxml** 4.9.x - HTML parsing and validation
- **Pillow** 10.1.x - image metadata and optimization

### Database
- **SQLAlchemy** (existing) - Add `media_assets` JSON field to `Template` model
- Store: image URLs, video URLs, selected color schemes, animation preferences

### Testing
- **pytest** 7.4.x - unit and integration tests
- **playwright** 1.40.x - visual regression testing for generated websites
- **HTML5 validator** - markup validation

---

## Technical Details

### 1. Premium Prompt System

**File**: `backend/app/prompts/premium_website_prompt.txt`

Create a master prompt that embodies the "elite designer" persona from the requirements document. Key sections:

```
Role: ELITE AWARD-WINNING web designer
Credentials: $100,000+ websites, Apple elegance, Stripe conversion optimization
Task: Generate COMPLETE HTML with inline CSS/JavaScript
Mandatory Features: [50+ specific requirements]
Output Format: Raw HTML starting with <!DOCTYPE html>, no markdown
Business Context: {{business_type}}, {{scraped_content}}, {{evaluation_data}}
```

**Niche-Specific Prompts**: `backend/app/prompts/niche_templates/`

Each business type gets specialized instructions:
- **Restaurants**: 15+ food images, menu animations, reservation CTAs
- **Service Businesses**: Before/after sliders, emergency call buttons, certifications
- **Professional Services**: Team profiles, case studies, trust badges
- **Retail**: Product galleries with zoom, reviews, shopping cart UI

### 2. Premium Template Builder Service

**File**: `backend/app/services/premium_template_builder.py`

**Class**: `PremiumTemplateBuilder`

**Purpose**: Programmatically construct HTML structure with guaranteed premium features.

**Key Methods**:

```python
class PremiumTemplateBuilder:
    def __init__(self, business_data: dict, media_assets: dict, scraped_content: dict):
        """Initialize with business context and sourced media"""

    def build_html_structure(self) -> str:
        """Generate complete HTML with all mandatory sections"""
        return self._build_doctype() + \
               self._build_head() + \
               self._build_body() + \
               self._build_scripts()

    def _build_head(self) -> str:
        """
        Generate <head> with:
        - Meta tags (SEO, viewport, OG tags)
        - Font Awesome 6.5.1 CDN
        - Google Fonts
        - Inline CSS with CSS variables, glassmorphism, animations
        """

    def _build_body(self) -> str:
        """
        Generate <body> with mandatory sections:
        - Loading overlay
        - Glassmorphism navbar (sticky)
        - Hero section (video background, particles, typewriter effect)
        - Services/products section (animated cards, hover effects)
        - About/team section (counter animations, parallax)
        - Testimonials carousel (auto-rotating, star ratings)
        - Gallery section (lightbox, lazy loading)
        - Contact section (working form validation, map)
        - Footer (schema.org LocalBusiness markup)
        """

    def _build_css(self) -> str:
        """
        Generate comprehensive CSS:
        - CSS variables for theme colors
        - 8+ @keyframes animations (fadeInUp, float, typing, slideIn, etc.)
        - Glassmorphism effects: backdrop-filter: blur(20px)
        - Responsive breakpoints: 320px, 768px, 1024px, 1440px
        - Mobile-first media queries
        - Professional hover states and transitions
        """

    def _build_scripts(self) -> str:
        """
        Generate JavaScript functionality:
        - Smooth scroll navigation
        - Intersection Observer for scroll animations
        - Mobile hamburger menu
        - Contact form validation
        - Testimonial carousel auto-rotation
        - Counter animations (for statistics)
        - Parallax effects
        - Lazy image loading
        """

    def inject_business_content(self, gpt_enhanced_content: dict) -> None:
        """Replace placeholders with GPT-4 enhanced business content"""

    def inject_media_assets(self) -> None:
        """Insert Unsplash images and Pexels videos into template"""

    def apply_niche_specialization(self, business_type: str) -> None:
        """Add business-type-specific features"""

    def validate_premium_standards(self) -> List[str]:
        """
        Check generated HTML against requirements checklist:
        - Glassmorphism navbar present
        - Minimum 12 images
        - 8+ animations defined
        - Mobile responsive meta tags
        - Schema.org markup
        - All sections present
        Returns list of missing features (empty = perfect)
        """
```

### 3. Media Sourcing Service

**File**: `backend/app/services/media_sourcing_service.py`

**Purpose**: Automatically fetch relevant, high-quality media from Unsplash and Pexels.

```python
class MediaSourcingService:
    def __init__(self, unsplash_key: str, pexels_key: str):
        """Initialize API clients"""

    async def get_business_images(
        self,
        business_type: str,
        business_name: str,
        count: int = 15
    ) -> List[ImageAsset]:
        """
        Fetch business-appropriate images from Unsplash

        Search strategy:
        - Restaurants: "fine dining", "food plating", "restaurant ambiance",
                      "chef cooking", "cocktails", "dessert presentation"
        - Service: "professional handyman", "renovation before after",
                  "tools equipment", "satisfied customer"
        - Professional: "office professional", "business meeting",
                       "corporate team", "modern workspace"
        - Retail: "boutique shopping", "product display", "retail interior"

        Returns high-res URLs (1920x1080 min) with attribution
        """

    async def get_hero_video(self, business_type: str) -> VideoAsset:
        """
        Fetch relevant hero background video from Pexels

        Criteria:
        - MP4 format, HD quality (1920x1080)
        - 10-30 seconds loop-friendly
        - Relevant to business type
        - Properly licensed for commercial use

        Returns video URL with attribution
        """

    def get_placeholder_images(self, count: int) -> List[str]:
        """
        Fallback: Generate Unsplash random image URLs if API fails
        Format: https://source.unsplash.com/1920x1080/?{keyword}
        """
```

### 4. Enhanced Template Generator Integration

**File**: `backend/app/services/template_generator.py` (MAJOR MODIFICATIONS)

**Current Function**: `generate_templates_for_business()`

**Enhancements**:

```python
async def generate_templates_for_business(
    business: Business,
    db: Session,
    num_variants: int = 3
) -> List[Template]:
    """Enhanced to use premium template generation"""

    # Step 1: Enhanced scraping (get more content, images, colors)
    scraped_data = await scrape_business_website_enhanced(business.website_url)

    # Step 2: Determine business niche
    business_type = _classify_business_type(business, scraped_data)

    # Step 3: Source premium media
    media_service = MediaSourcingService(
        settings.UNSPLASH_API_KEY,
        settings.PEXELS_API_KEY
    )
    media_assets = await media_service.get_business_images(business_type, business.name, count=15)
    hero_video = await media_service.get_hero_video(business_type)

    # Step 4: Build structured HTML template
    builder = PremiumTemplateBuilder(
        business_data={
            "name": business.name,
            "description": business.description,
            "services": scraped_data.get("services", []),
            "contact": scraped_data.get("contact", {}),
            "testimonials": scraped_data.get("testimonials", []),
        },
        media_assets={
            "images": media_assets,
            "hero_video": hero_video,
        },
        scraped_content=scraped_data
    )

    # Step 5: Apply niche specialization
    builder.apply_niche_specialization(business_type)

    # Step 6: Use GPT-4 to enhance content (NOT generate HTML)
    enhanced_content = await _enhance_business_content_with_gpt4(
        business=business,
        scraped_data=scraped_data,
        business_type=business_type,
        template_structure=builder.get_content_placeholders()
    )

    # Step 7: Inject enhanced content into structured template
    builder.inject_business_content(enhanced_content)
    builder.inject_media_assets()

    # Step 8: Generate final HTML
    final_html = builder.build_html_structure()

    # Step 9: Validate against premium standards
    validation_errors = builder.validate_premium_standards()
    if validation_errors:
        logger.warning(f"Template quality issues: {validation_errors}")
        # Attempt to fix or regenerate missing features
        final_html = builder.fix_validation_errors(validation_errors)

    # Step 10: Save to database
    template = Template(
        business_id=business.id,
        html_content=final_html,
        css_content="",  # Inline in HTML
        js_content="",   # Inline in HTML
        media_assets={"images": [img.url for img in media_assets], "video": hero_video.url},
        generated_at=datetime.utcnow()
    )

    db.add(template)
    db.commit()

    return [template]


async def _enhance_business_content_with_gpt4(
    business: Business,
    scraped_data: dict,
    business_type: str,
    template_structure: dict
) -> dict:
    """
    Use GPT-4 to enhance content quality WITHOUT generating HTML

    Returns enhanced:
    - Headline (with power words)
    - Value propositions
    - Service descriptions (professional copywriting)
    - Call-to-action text
    - About section narrative
    - Testimonial formatting
    - Meta descriptions for SEO
    """

    prompt = f"""You are an expert copywriter enhancing website content.

Business: {business.name}
Type: {business_type}
Current Content: {scraped_data}

Enhance the following content sections with professional, conversion-optimized copy:

1. Hero Headline: Create a powerful, benefit-focused headline (max 10 words)
2. Hero Subheadline: Supporting statement (max 20 words)
3. Value Propositions: 3 compelling reasons to choose this business
4. Service Descriptions: Professional descriptions for each service
5. About Section: Engaging company story (150 words)
6. CTAs: 3 variations of call-to-action button text
7. Meta Description: SEO-optimized description (155 characters)

Return as JSON with keys: headline, subheadline, value_props, services, about, ctas, meta_description"""

    response = await client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def _classify_business_type(business: Business, scraped_data: dict) -> str:
    """
    Classify business into niche categories:
    - restaurant
    - service_business (plumber, electrician, etc.)
    - professional_services (lawyer, consultant, etc.)
    - retail
    - healthcare
    - fitness
    - default

    Use business description, scraped keywords, and simple classification logic
    """
    keywords = {
        "restaurant": ["restaurant", "cafe", "dining", "food", "menu", "chef"],
        "service_business": ["plumber", "electrician", "hvac", "repair", "contractor"],
        "professional_services": ["lawyer", "attorney", "consultant", "accountant", "advisor"],
        "retail": ["shop", "store", "boutique", "retail", "products"],
    }

    text = f"{business.name} {business.description} {scraped_data.get('text', '')}".lower()

    for biz_type, keywords_list in keywords.items():
        if any(kw in text for kw in keywords_list):
            return biz_type

    return "default"
```

### 5. Database Schema Update

**File**: `backend/app/models/template.py`

Add new field to store media asset URLs:

```python
from sqlalchemy import Column, JSON

class Template(Base):
    __tablename__ = "templates"

    # ... existing fields ...

    media_assets = Column(JSON, nullable=True)  # NEW: Store image/video URLs

    # Structure:
    # {
    #   "images": ["https://images.unsplash.com/...", ...],
    #   "video": "https://videos.pexels.com/...",
    #   "attribution": [{"source": "Unsplash", "photographer": "...", "url": "..."}]
    # }
```

**Migration**: Create Alembic migration to add column:

```bash
alembic revision -m "add_media_assets_to_templates"
alembic upgrade head
```

### 6. Configuration Updates

**File**: `backend/app/config.py`

Add new environment variables:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Media sourcing API keys
    UNSPLASH_API_KEY: str = ""
    PEXELS_API_KEY: str = ""

    # Template generation settings
    PREMIUM_TEMPLATE_MODE: bool = True
    DEFAULT_IMAGE_COUNT: int = 15
    ENABLE_VIDEO_BACKGROUNDS: bool = True

    class Config:
        env_file = ".env"
```

**File**: `backend/.env` (add):

```
UNSPLASH_API_KEY=your_unsplash_access_key
PEXELS_API_KEY=your_pexels_api_key
PREMIUM_TEMPLATE_MODE=true
```

---

## Development Setup

### Prerequisites
- Python 3.11+ (existing)
- PostgreSQL (existing)
- Unsplash API account (FREE tier: 50 requests/hour)
- Pexels API account (FREE tier: 200 requests/hour)

### Installation Steps

1. **Install new dependencies**:
```bash
cd backend
pip install pyunsplash==1.0.0rc1 pexels-api==1.0.1 jinja2==3.1.2 playwright==1.40.0
```

2. **Update requirements.txt**:
```bash
pip freeze > requirements.txt
```

3. **Set up API keys**:
- Sign up at https://unsplash.com/developers
- Get Access Key, add to `.env`
- Sign up at https://www.pexels.com/api/
- Get API Key, add to `.env`

4. **Run database migration**:
```bash
alembic revision --autogenerate -m "add_media_assets_to_templates"
alembic upgrade head
```

5. **Install Playwright browsers** (for testing):
```bash
playwright install
```

### Development Workflow

1. **Create new service files** (premium_template_builder.py, media_sourcing_service.py)
2. **Update template_generator.py** with new logic
3. **Test media sourcing** independently
4. **Test template generation** with sample business
5. **Validate HTML output** against checklist
6. **Run visual regression tests**
7. **Optimize performance** (caching, lazy loading)

---

## Implementation Guide

### Phase 1: Foundation (Days 1-2)

**Tasks**:
1. Create `premium_template_builder.py` skeleton
2. Implement `_build_head()` with all CDN links, CSS variables
3. Implement `_build_css()` with glassmorphism, animations
4. Create basic HTML structure for all sections

**Acceptance Criteria**:
- Generated HTML validates (HTML5 validator)
- CSS contains 8+ keyframe animations
- Glassmorphism effects render correctly
- Mobile-responsive breakpoints work

### Phase 2: Media Integration (Days 3-4)

**Tasks**:
1. Create `media_sourcing_service.py`
2. Integrate Unsplash API with search logic
3. Integrate Pexels API for videos
4. Implement fallback placeholder images
5. Add attribution handling

**Acceptance Criteria**:
- Successfully fetch 15 relevant images per business
- Fetch appropriate hero video
- Handle API rate limits gracefully
- Store attributions in database

### Phase 3: Content Enhancement (Days 5-6)

**Tasks**:
1. Create niche-specific prompt templates
2. Implement `_enhance_business_content_with_gpt4()`
3. Add business type classification logic
4. Implement content injection into HTML

**Acceptance Criteria**:
- GPT-4 returns JSON-formatted enhanced content
- Headlines are compelling and benefit-focused
- Service descriptions are professional
- Content matches business niche

### Phase 4: Template Assembly (Days 7-8)

**Tasks**:
1. Update `template_generator.py` main function
2. Integrate all services (builder, media, enhancement)
3. Implement validation logic
4. Add error handling and logging

**Acceptance Criteria**:
- Complete workflow generates valid HTML
- All mandatory features present
- Template passes validation checklist
- Handles errors gracefully (API failures, missing data)

### Phase 5: Niche Specialization (Days 9-10)

**Tasks**:
1. Implement restaurant-specific features
2. Implement service business features (before/after sliders)
3. Implement professional services features (team profiles)
4. Implement retail features (product galleries)

**Acceptance Criteria**:
- Each business type gets specialized UI elements
- Restaurant templates have menu animations
- Service templates have emergency call buttons
- Professional templates have case studies

### Phase 6: Testing & Optimization (Days 11-12)

**Tasks**:
1. Create `test_premium_templates.py` test suite
2. Implement visual regression tests with Playwright
3. Test with 5+ real business websites
4. Optimize performance (image lazy loading, caching)
5. Fix any validation failures

**Acceptance Criteria**:
- All tests pass
- Generated sites load in < 2 seconds
- Mobile responsiveness perfect on 320px, 768px, 1440px
- No console errors in browser
- 100% feature compliance with requirements document

---

## Testing Approach

### Unit Tests

**File**: `tests/test_premium_template_builder.py`

```python
def test_build_html_structure():
    """Test complete HTML generation"""

def test_css_contains_animations():
    """Verify 8+ keyframe animations present"""

def test_glassmorphism_css():
    """Verify backdrop-filter: blur(20px) in navbar"""

def test_mobile_responsive_breakpoints():
    """Verify @media queries for 320px, 768px, 1024px"""

def test_schema_org_markup():
    """Verify LocalBusiness structured data in footer"""
```

**File**: `tests/test_media_sourcing.py`

```python
def test_unsplash_image_fetching():
    """Test fetching 15 images for restaurant business"""

def test_pexels_video_fetching():
    """Test fetching hero video"""

def test_api_rate_limit_handling():
    """Test graceful degradation when APIs fail"""

def test_placeholder_fallback():
    """Test fallback to placeholder images"""
```

**File**: `tests/test_template_generator.py`

```python
def test_generate_premium_template():
    """Test end-to-end template generation"""

def test_business_type_classification():
    """Test business type detection logic"""

def test_validation_checklist():
    """Test template validation against requirements"""
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_workflow_restaurant():
    """Test complete workflow for restaurant business"""
    business = create_test_business(type="restaurant")
    templates = await generate_templates_for_business(business, db)

    assert len(templates) > 0
    html = templates[0].html_content

    # Validate mandatory features
    assert '<!DOCTYPE html>' in html
    assert 'backdrop-filter: blur(20px)' in html
    assert '@keyframes' in html
    assert html.count('@keyframes') >= 8
    assert 'Font Awesome' in html or 'fontawesome' in html
    assert len(templates[0].media_assets['images']) >= 12
    assert templates[0].media_assets['video']
```

### Visual Regression Tests

**File**: `tests/test_visual_regression.py`

```python
from playwright.sync_api import sync_playwright

def test_mobile_responsiveness():
    """Test template renders correctly on mobile"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 375, "height": 667})
        page.set_content(generated_html)
        screenshot = page.screenshot()
        # Compare with baseline

def test_desktop_responsiveness():
    """Test template renders correctly on desktop"""
    # Similar to mobile test but 1920x1080
```

### Manual Testing Checklist

1. **Visual Inspection**:
   - [ ] Glassmorphism navbar looks premium
   - [ ] Hero video plays and loops
   - [ ] Animations trigger on scroll
   - [ ] All images load correctly
   - [ ] Mobile menu works smoothly

2. **Functionality**:
   - [ ] Contact form validates
   - [ ] Smooth scroll navigation works
   - [ ] Testimonial carousel auto-rotates
   - [ ] Hover effects work on desktop
   - [ ] Touch targets are 44px+ on mobile

3. **Performance**:
   - [ ] Page loads in < 2 seconds
   - [ ] Animations run at 60fps
   - [ ] Images lazy load
   - [ ] No console errors

4. **Cross-Browser**:
   - [ ] Chrome
   - [ ] Firefox
   - [ ] Safari
   - [ ] Edge

---

## Deployment Strategy

### Development Environment
- Test with sample businesses
- Use Unsplash/Pexels development API keys
- Local PostgreSQL database

### Staging Environment
1. Deploy updated backend code
2. Run database migration: `alembic upgrade head`
3. Set production API keys in environment variables
4. Test with 3-5 real client businesses
5. Validate generated templates meet quality standards

### Production Deployment

**Pre-deployment Checklist**:
- [ ] All tests passing
- [ ] Database migration tested
- [ ] API keys configured
- [ ] Rate limiting implemented for Unsplash/Pexels
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Performance benchmarks met

**Deployment Steps**:

1. **Database Migration**:
```bash
# Backup database first
pg_dump autoweb_db > backup_pre_premium_templates.sql

# Run migration
alembic upgrade head
```

2. **Deploy Backend Code**:
```bash
git pull origin main
pip install -r requirements.txt
systemctl restart autoweb-backend
```

3. **Verify Deployment**:
```bash
curl http://localhost:8000/api/health
# Test template generation endpoint
curl -X POST http://localhost:8000/api/businesses/1/generate-templates
```

4. **Monitor**:
- Watch logs for errors: `tail -f logs/app.log`
- Monitor API usage (Unsplash/Pexels dashboards)
- Check template generation success rate

### Rollback Plan

If issues arise:

1. **Quick Rollback**:
```bash
git checkout <previous-commit>
pip install -r requirements.txt
alembic downgrade -1  # Revert migration
systemctl restart autoweb-backend
```

2. **Database Restoration** (if needed):
```bash
psql autoweb_db < backup_pre_premium_templates.sql
```

### Post-Deployment Validation

1. Generate templates for 5 test businesses
2. Manually inspect generated HTML
3. Verify all mandatory features present
4. Check mobile responsiveness
5. Test on multiple browsers
6. Monitor error rates for 24 hours

### Performance Monitoring

- Track template generation time (target: < 30 seconds per template)
- Monitor API rate limits (Unsplash: 50/hour, Pexels: 200/hour)
- Implement caching for frequently used images
- Set up alerts for generation failures

### Scaling Considerations

- **Image Caching**: Cache popular Unsplash images locally
- **Background Processing**: Move template generation to Celery queue
- **CDN Integration**: Serve generated templates from CDN
- **Database Optimization**: Index `business_id` in templates table

---

## Success Metrics

### Technical Metrics
- ✅ 100% of generated templates pass validation checklist
- ✅ Template generation completes in < 30 seconds
- ✅ 0 critical errors in production logs
- ✅ 95%+ uptime for generation service

### Quality Metrics
- ✅ All templates have 12+ professional images
- ✅ All templates have working animations
- ✅ All templates are mobile-responsive
- ✅ All templates have glassmorphism navbar
- ✅ All templates include hero video

### Business Metrics
- ✅ Client satisfaction increase (qualitative feedback)
- ✅ Reduction in template revision requests
- ✅ Increase in conversion rates for client websites
- ✅ Premium pricing justification (templates look $50,000+)

---

## Risk Mitigation

### Risk 1: API Rate Limits
**Mitigation**:
- Implement request caching
- Use fallback placeholder images
- Queue generation requests during off-peak hours

### Risk 2: GPT-4 Inconsistent Output
**Mitigation**:
- Use structured template builder (hybrid approach)
- Validate all generated content
- Implement retry logic with different prompts

### Risk 3: Performance Degradation
**Mitigation**:
- Lazy load images
- Optimize CSS/JS (minification)
- Use CDN for static assets
- Implement template caching

### Risk 4: Business Content Too Generic
**Mitigation**:
- Enhanced scraping to get more specific content
- Business owner questionnaire for unique details
- Manual content review option

---

## Next Steps After Implementation

1. **User Acceptance Testing**: Have azeem test with real client businesses
2. **Client Feedback Loop**: Gather feedback from 3-5 clients on new templates
3. **Iteration**: Refine based on feedback
4. **Documentation**: Create user guide for template customization
5. **Training**: Train team on new features and capabilities

---

**End of Technical Specification**
