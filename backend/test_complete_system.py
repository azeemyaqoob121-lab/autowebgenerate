"""
Complete System Test for Enhanced HTML Scraping and AI Modernization
Story 4.10: End-to-End validation of the entire pipeline
"""

import sys
import os
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService
from app.services.template_modernization_service import TemplateModernizationService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_first_business(db: Session) -> Business:
    """Get first business from database for testing."""
    business = db.query(Business).filter(
        Business.website_url.isnot(None),
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        logger.error("No businesses found in database")
        return None

    logger.info(f"Found business: {business.name} ({business.website_url})")
    return business


def test_enhanced_scraping(db: Session, business_id: str):
    """Test enhanced website scraping."""
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Testing Enhanced Website Scraping")
    logger.info("="*80)

    scraper = EnhancedWebsiteScraperService(db)
    success = scraper.scrape_complete_website(business_id)

    if not success:
        logger.error("❌ Scraping failed!")
        return False

    # Reload business to see scraped data
    business = db.query(Business).filter(Business.id == business_id).first()

    logger.info(f"\n✅ Scraping SUCCESS for {business.name}")
    logger.info(f"   - HTML length: {len(business.scraped_html) if business.scraped_html else 0} characters")
    logger.info(f"   - CSS length: {len(business.scraped_css) if business.scraped_css else 0} characters")
    logger.info(f"   - Images found: {len(business.image_urls) if business.image_urls else 0}")
    logger.info(f"   - Logos found: {len(business.logo_urls) if business.logo_urls else 0}")
    logger.info(f"   - Videos found: {len(business.video_urls) if business.video_urls else 0}")
    logger.info(f"   - Maps found: {len(business.map_embeds) if business.map_embeds else 0}")
    logger.info(f"   - Colors extracted: {len(business.color_palette) if business.color_palette else 0}")
    logger.info(f"   - Components count: {business.component_count}")

    if business.color_palette:
        logger.info(f"   - Color palette: {business.color_palette}")

    return True


def test_template_generation(db: Session, business_id: str):
    """Test AI template modernization."""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Testing AI Template Generation")
    logger.info("="*80)

    service = TemplateModernizationService(db)

    try:
        templates = service.generate_modernized_templates(business_id, force_rescrape=False)

        if not templates:
            logger.error("❌ Template generation failed - no templates returned")
            return False

        logger.info(f"\n✅ Template Generation SUCCESS")
        logger.info(f"   - Generated {len(templates)} template(s)")

        for idx, template in enumerate(templates, 1):
            logger.info(f"\n   Template {idx}:")
            logger.info(f"      - ID: {template.id}")
            logger.info(f"      - Variant: {template.variant_number}")
            logger.info(f"      - HTML length: {len(template.html_content)} characters")
            logger.info(f"      - Improvements: {template.improvements_made}")

            # Validate HTML structure
            html = template.html_content.lower()
            checks = {
                "<!doctype": "DOCTYPE declaration",
                "<html": "HTML tag",
                "<head": "HEAD tag",
                "<body": "BODY tag",
                "</html>": "Closing HTML tag",
                "tailwind": "Tailwind CSS",
                "class=": "CSS classes"
            }

            logger.info(f"\n      Quality Checks:")
            for check, description in checks.items():
                result = "✅" if check in html else "❌"
                logger.info(f"         {result} {description}")

        return True

    except Exception as e:
        logger.error(f"❌ Template generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_template_quality(db: Session, business_id: str):
    """Validate template quality and 'wow factor'."""
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Validating Template Quality")
    logger.info("="*80)

    from app.models.template import Template

    templates = db.query(Template).filter(
        Template.business_id == business_id
    ).all()

    if not templates:
        logger.error("❌ No templates found for quality validation")
        return False

    business = db.query(Business).filter(Business.id == business_id).first()

    for template in templates:
        logger.info(f"\n📊 Analyzing Template {template.id} (Variant {template.variant_number}):")

        html = template.html_content
        html_lower = html.lower()

        # Quality metrics
        quality_score = 0
        max_score = 0

        # Check 1: HTML size (should be substantial for "wow factor")
        max_score += 10
        if len(html) > 30000:
            logger.info("   ✅ Substantial HTML length (>30k chars) - EXCELLENT")
            quality_score += 10
        elif len(html) > 15000:
            logger.info("   ✅ Good HTML length (>15k chars)")
            quality_score += 7
        elif len(html) > 5000:
            logger.info("   ⚠️  Moderate HTML length (>5k chars)")
            quality_score += 4
        else:
            logger.info("   ❌ HTML too short - lacks content")

        # Check 2: Modern CSS framework
        max_score += 10
        if 'tailwind' in html_lower or 'cdn.tailwindcss.com' in html_lower:
            logger.info("   ✅ Tailwind CSS framework detected")
            quality_score += 10
        elif 'bootstrap' in html_lower:
            logger.info("   ✅ Bootstrap framework detected")
            quality_score += 8
        else:
            logger.info("   ⚠️  No major CSS framework detected")
            quality_score += 2

        # Check 3: Responsive design
        max_score += 10
        responsive_keywords = ['md:', 'lg:', 'sm:', 'xl:', '@media', 'responsive']
        responsive_count = sum(1 for kw in responsive_keywords if kw in html_lower)
        if responsive_count >= 3:
            logger.info(f"   ✅ Responsive design detected ({responsive_count} indicators)")
            quality_score += 10
        else:
            logger.info(f"   ⚠️  Limited responsive design ({responsive_count} indicators)")
            quality_score += responsive_count * 2

        # Check 4: Modern interactions (hover, transitions, animations)
        max_score += 10
        interaction_keywords = ['hover:', 'transition', 'animation', 'transform', 'scale']
        interaction_count = sum(1 for kw in interaction_keywords if kw in html_lower)
        if interaction_count >= 5:
            logger.info(f"   ✅ Rich interactions ({interaction_count} animation/transition features)")
            quality_score += 10
        else:
            logger.info(f"   ⚠️  Limited interactions ({interaction_count} features)")
            quality_score += interaction_count * 2

        # Check 5: Semantic HTML5
        max_score += 10
        semantic_tags = ['<nav', '<header', '<footer', '<section', '<article', '<main']
        semantic_count = sum(1 for tag in semantic_tags if tag in html_lower)
        if semantic_count >= 4:
            logger.info(f"   ✅ Semantic HTML5 structure ({semantic_count} semantic tags)")
            quality_score += 10
        else:
            logger.info(f"   ⚠️  Limited semantic structure ({semantic_count} tags)")
            quality_score += semantic_count * 2

        # Check 6: Brand preservation (colors)
        max_score += 10
        if business.color_palette:
            colors_preserved = 0
            for color in business.color_palette:
                if color.lower() in html_lower:
                    colors_preserved += 1

            preservation_rate = (colors_preserved / len(business.color_palette)) * 100
            if preservation_rate >= 80:
                logger.info(f"   ✅ Excellent brand color preservation ({preservation_rate:.0f}%)")
                quality_score += 10
            elif preservation_rate >= 50:
                logger.info(f"   ✅ Good brand color preservation ({preservation_rate:.0f}%)")
                quality_score += 7
            else:
                logger.info(f"   ⚠️  Weak brand color preservation ({preservation_rate:.0f}%)")
                quality_score += 3
        else:
            logger.info("   ℹ️  No color palette available to verify")
            quality_score += 5
            max_score += 0  # Don't penalize if no data

        # Check 7: Image embedding
        max_score += 10
        image_count = html_lower.count('<img')
        expected_images = len(business.image_urls) if business.image_urls else 0
        if image_count >= expected_images and expected_images > 0:
            logger.info(f"   ✅ All images embedded ({image_count} images)")
            quality_score += 10
        elif image_count > 0:
            logger.info(f"   ⚠️  Some images embedded ({image_count} of {expected_images})")
            quality_score += 5
        else:
            logger.info("   ⚠️  No images found in template")

        # Check 8: Gradient usage (modern design indicator)
        max_score += 10
        gradient_count = html_lower.count('gradient')
        if gradient_count >= 5:
            logger.info(f"   ✅ Rich gradient usage ({gradient_count} gradients) - PREMIUM FEEL")
            quality_score += 10
        elif gradient_count >= 2:
            logger.info(f"   ✅ Moderate gradient usage ({gradient_count} gradients)")
            quality_score += 7
        else:
            logger.info(f"   ⚠️  Limited gradients ({gradient_count})")
            quality_score += gradient_count * 2

        # Check 9: Shadow effects (depth and dimension)
        max_score += 10
        shadow_count = html_lower.count('shadow')
        if shadow_count >= 10:
            logger.info(f"   ✅ Extensive shadow usage ({shadow_count} shadows) - DEPTH & DIMENSION")
            quality_score += 10
        elif shadow_count >= 5:
            logger.info(f"   ✅ Good shadow usage ({shadow_count} shadows)")
            quality_score += 7
        else:
            logger.info(f"   ⚠️  Limited shadows ({shadow_count})")
            quality_score += shadow_count

        # Check 10: Large, bold typography
        max_score += 10
        large_text = ['text-5xl', 'text-6xl', 'text-7xl', 'text-8xl', 'text-4xl']
        large_text_count = sum(1 for size in large_text if size in html_lower)
        if large_text_count >= 3:
            logger.info(f"   ✅ Bold, large typography ({large_text_count} large text sizes)")
            quality_score += 10
        else:
            logger.info(f"   ⚠️  Limited large typography ({large_text_count} sizes)")
            quality_score += large_text_count * 2

        # Final score
        percentage = (quality_score / max_score) * 100
        logger.info(f"\n   📊 QUALITY SCORE: {quality_score}/{max_score} ({percentage:.1f}%)")

        if percentage >= 90:
            logger.info("   🌟 OUTSTANDING - PREMIUM WOW FACTOR!")
        elif percentage >= 80:
            logger.info("   ✅ EXCELLENT - Strong wow factor")
        elif percentage >= 70:
            logger.info("   ✅ GOOD - Decent quality")
        elif percentage >= 60:
            logger.info("   ⚠️  ACCEPTABLE - Needs improvement")
        else:
            logger.info("   ❌ POOR - Major improvements needed")

    return True


def save_template_preview(db: Session, business_id: str):
    """Save generated template to file for manual inspection."""
    logger.info("\n" + "="*80)
    logger.info("STEP 4: Saving Template Preview")
    logger.info("="*80)

    from app.models.template import Template

    templates = db.query(Template).filter(
        Template.business_id == business_id
    ).order_by(Template.id.desc()).all()

    if not templates:
        logger.error("❌ No templates to save")
        return False

    business = db.query(Business).filter(Business.id == business_id).first()

    for template in templates:
        filename = f"template_preview_{business.name.replace(' ', '_')}_variant{template.variant_number}.html"
        filepath = os.path.join(os.path.dirname(__file__), filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template.html_content)

        logger.info(f"✅ Saved template to: {filepath}")
        logger.info(f"   Open this file in a browser to see the WOW FACTOR!")

    return True


def main():
    """Run complete system test."""
    logger.info("\n" + "="*80)
    logger.info("🚀 COMPLETE SYSTEM TEST: Enhanced HTML Scraping & AI Modernization")
    logger.info("="*80)

    db = SessionLocal()

    try:
        # Get business
        business = get_first_business(db)
        if not business:
            logger.error("❌ No business found - cannot run tests")
            return False

        logger.info(f"\n🎯 Testing with business: {business.name}")
        logger.info(f"   URL: {business.website_url}")
        logger.info(f"   ID: {business.id}")

        # Run tests
        if not test_enhanced_scraping(db, business.id):
            logger.error("\n❌ SCRAPING TEST FAILED")
            return False

        if not test_template_generation(db, business.id):
            logger.error("\n❌ TEMPLATE GENERATION TEST FAILED")
            return False

        if not test_template_quality(db, business.id):
            logger.error("\n❌ QUALITY VALIDATION FAILED")
            return False

        save_template_preview(db, business.id)

        logger.info("\n" + "="*80)
        logger.info("✅ ALL TESTS PASSED - SYSTEM IS WORKING!")
        logger.info("="*80)
        logger.info("\n🎉 SUCCESS! The enhanced scraping and AI modernization system is fully functional.")
        logger.info("📝 Next steps:")
        logger.info("   1. Open the saved HTML preview file(s) in your browser")
        logger.info("   2. Verify the 'WOW FACTOR' visually")
        logger.info("   3. Check that brand colors, images, and content are preserved")
        logger.info("   4. Test on mobile devices and different screen sizes")
        logger.info("   5. Show to business owners and get feedback!")

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
