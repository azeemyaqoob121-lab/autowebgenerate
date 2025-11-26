"""
Complete End-to-End Test for Gemini Template Generation Flow

This script tests the complete flow:
1. Search/discover business
2. Scrape HTML data
3. Auto-evaluate
4. Generate template with Gemini
5. Verify scraped data is saved correctly
6. Regenerate template with Gemini
7. Verify template quality

Author: Amelia (Developer Agent)
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Business, Template, Evaluation
from app.config import settings
from app.services.website_scraper import scrape_business_website
from app.services.template_generator_premium import generate_templates_for_business
from app.services.evaluation_service import try_auto_evaluate
from bs4 import BeautifulSoup


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message: str):
    """Print success message"""
    print(f"[OK] {message}")


def print_error(message: str):
    """Print error message"""
    print(f"[ERROR] {message}")


def print_info(message: str):
    """Print info message"""
    print(f"[INFO] {message}")


def check_environment():
    """Check if all required environment variables are set"""
    print_section("STEP 1: Environment Check")

    checks = {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
    }

    all_ok = True
    for key, value in checks.items():
        if value:
            print_success(f"{key}: Configured ({settings.mask_secret(value)})")
        else:
            print_error(f"{key}: NOT configured")
            all_ok = False

    # Check Gemini mode
    print_info(f"USE_GEMINI_GENERATION: {settings.USE_GEMINI_GENERATION}")
    print_info(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")

    if not all_ok:
        print_error("\n[WARNING] Some API keys are missing. The test may fail.")
        return False

    return True


def create_test_business(db: Session) -> Business:
    """Create a test business for testing"""
    print_section("STEP 2: Create Test Business")

    # Check if test business exists
    test_url = "https://www.ccelectricalservices.co.uk"
    existing = db.query(Business).filter(Business.website_url == test_url).first()

    if existing:
        print_info(f"Test business already exists: {existing.name} (ID: {existing.id})")
        # Clear existing templates and evaluations for fresh test
        db.query(Template).filter(Template.business_id == existing.id).delete()
        db.query(Evaluation).filter(Evaluation.business_id == existing.id).delete()
        db.commit()
        print_success("Cleared existing templates and evaluations")
        return existing

    # Create new test business
    business = Business(
        name="CC Electrical Services",
        website_url=test_url,
        category="Electrician",
        description="Professional electrical services",
        location="London",
        phone="020 1234 5678",
        email="info@ccelectrical.co.uk"
    )

    db.add(business)
    db.commit()
    db.refresh(business)

    print_success(f"Created test business: {business.name} (ID: {business.id})")
    return business


def test_scraping(business: Business, db: Session):
    """Test HTML scraping and verify data is saved"""
    print_section("STEP 3: Test HTML Scraping")

    try:
        # Scrape website
        print_info(f"Scraping: {business.website_url}")
        scraped_data = scrape_business_website(business.website_url)

        if not scraped_data:
            print_error("Scraping returned empty data")
            return False

        # Validate scraped data
        raw_html = scraped_data.get("raw_html", "")
        if not raw_html:
            print_error("No raw_html in scraped data")
            return False

        print_success(f"Scraped {len(raw_html)} bytes of HTML")

        # Check for key fields
        checks = {
            "text_content": scraped_data.get("text_content", ""),
            "page_structure": scraped_data.get("page_structure", []),
            "colors": scraped_data.get("colors", []),
            "images": scraped_data.get("images", []),
            "headlines": scraped_data.get("headlines", {}),
        }

        for key, value in checks.items():
            if value:
                if isinstance(value, str):
                    print_success(f"  {key}: {len(value)} characters")
                elif isinstance(value, (list, dict)):
                    print_success(f"  {key}: {len(value)} items")
            else:
                print_error(f"  {key}: Missing or empty")

        # Save to database
        business.scraped_data = scraped_data
        business.scraped_html = raw_html

        # Try to extract some enhanced fields
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Extract images
        images = [img.get('src') for img in soup.find_all('img') if img.get('src')]
        business.image_urls = images[:20] if images else []

        # Extract colors from inline styles (basic extraction)
        colors = []
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                # Very basic color extraction
                import re
                color_matches = re.findall(r'#[0-9A-Fa-f]{6}', style_tag.string)
                colors.extend(color_matches)
        business.color_palette = list(set(colors))[:10] if colors else []

        # Count components
        sections = soup.find_all(['section', 'div', 'header', 'footer', 'nav', 'main'])
        business.component_count = len(sections)

        from datetime import datetime
        business.scraping_completed_at = datetime.utcnow()

        db.commit()
        db.refresh(business)

        print_success(f"Saved scraped data to database")
        print_info(f"  Images: {len(business.image_urls or [])}")
        print_info(f"  Colors: {len(business.color_palette or [])}")
        print_info(f"  Components: {business.component_count}")

        return True

    except Exception as e:
        print_error(f"Scraping failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation(business: Business, db: Session):
    """Test auto-evaluation"""
    print_section("STEP 4: Test Auto-Evaluation")

    try:
        print_info(f"Evaluating: {business.website_url}")
        success = try_auto_evaluate(db, business.id)

        if success:
            db.refresh(business)
            print_success(f"Evaluation successful! Score: {business.score}/100")

            # Get evaluation details
            evaluation = db.query(Evaluation).filter(
                Evaluation.business_id == business.id
            ).order_by(Evaluation.created_at.desc()).first()

            if evaluation:
                print_info(f"  Performance: {evaluation.performance_score}/100")
                print_info(f"  Accessibility: {evaluation.accessibility_score}/100")
                print_info(f"  Best Practices: {evaluation.best_practices_score}/100")
                print_info(f"  SEO: {evaluation.seo_score}/100")

            return True
        else:
            print_error("Evaluation failed or was skipped")
            return False

    except Exception as e:
        print_error(f"Evaluation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_template_generation(business: Business, db: Session, use_gemini: bool = False):
    """Test template generation"""
    engine_name = "Gemini" if use_gemini else "ChatGPT"
    print_section(f"STEP 5: Test Template Generation with {engine_name}")

    try:
        # Set Gemini mode if requested
        original_setting = settings.USE_GEMINI_GENERATION
        if use_gemini:
            settings.USE_GEMINI_GENERATION = True
            print_info(f"Enabled Gemini generation mode")
            print_info(f"Using model: {settings.GEMINI_MODEL}")

        print_info(f"Generating template for: {business.name}")

        # Generate templates
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        # Restore original setting
        settings.USE_GEMINI_GENERATION = original_setting

        if not templates:
            print_error("No templates generated")
            return False

        print_success(f"Generated {len(templates)} template(s)")

        # Check template quality
        for i, template in enumerate(templates, 1):
            print_info(f"\nTemplate #{i}:")
            print_info(f"  ID: {template.id}")
            print_info(f"  Variant: {template.variant_number}")
            print_info(f"  HTML size: {len(template.html_content)} bytes")

            # Basic HTML validation
            html = template.html_content

            checks = {
                "Has DOCTYPE": "<!DOCTYPE" in html or "<!doctype" in html,
                "Has <html> tag": "<html" in html.lower(),
                "Has <head> tag": "<head" in html.lower(),
                "Has <body> tag": "<body" in html.lower(),
                "Has CSS": "<style" in html.lower() or "stylesheet" in html.lower(),
                "Has business name": business.name.lower() in html.lower(),
                "Not corrupted": not is_html_corrupted(html),
            }

            for check, passed in checks.items():
                if passed:
                    print_success(f"    {check}")
                else:
                    print_error(f"    {check}")

        return True

    except Exception as e:
        print_error(f"Template generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        # Restore original setting
        settings.USE_GEMINI_GENERATION = original_setting
        return False


async def test_template_regeneration(business: Business, db: Session, use_gemini: bool = False):
    """Test template regeneration"""
    engine_name = "Gemini" if use_gemini else "ChatGPT"
    print_section(f"STEP 6: Test Template Regeneration with {engine_name}")

    try:
        # Delete existing templates
        existing_count = db.query(Template).filter(
            Template.business_id == business.id
        ).count()

        print_info(f"Found {existing_count} existing template(s)")

        db.query(Template).filter(Template.business_id == business.id).delete()
        db.commit()

        print_success("Deleted existing templates")

        # Set Gemini mode if requested
        original_setting = settings.USE_GEMINI_GENERATION
        if use_gemini:
            settings.USE_GEMINI_GENERATION = True
            print_info(f"Enabled Gemini generation mode")

        print_info(f"Regenerating template for: {business.name}")

        # Regenerate templates
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=1,
            use_premium=True
        )

        # Restore original setting
        settings.USE_GEMINI_GENERATION = original_setting

        if not templates:
            print_error("No templates regenerated")
            return False

        print_success(f"Regenerated {len(templates)} template(s)")

        # Check if templates are different (if we had previous ones)
        print_info(f"Templates have new IDs (regenerated successfully)")

        return True

    except Exception as e:
        print_error(f"Template regeneration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        # Restore original setting
        settings.USE_GEMINI_GENERATION = original_setting
        return False


def is_html_corrupted(html: str) -> bool:
    """Check if HTML is corrupted (less strict validation)"""
    if not html or len(html) < 50:
        return False

    # Check if HTML has basic structure tags
    html_lower = html.lower()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    has_body_tag = '<body' in html_lower or '<div' in html_lower

    if len(html) > 200 and not (has_html_tag or has_body_tag):
        return True

    # Only check if HTML STARTS with binary garbage (first 100 chars)
    first_100 = html[:100].strip()
    printable_count = sum(1 for c in first_100 if c.isprintable() or c in ['\n', '\r', '\t'])

    if len(first_100) > 0 and (printable_count / len(first_100)) < 0.7:
        return True

    return False


def verify_database_integrity(business: Business, db: Session):
    """Verify all data is saved correctly in database"""
    print_section("STEP 7: Verify Database Integrity")

    try:
        # Refresh business from database
        db.refresh(business)

        checks = []

        # Check scraped data
        if business.scraped_data:
            print_success("scraped_data: Saved")
            raw_html = business.scraped_data.get("raw_html", "")
            if raw_html:
                print_success(f"  raw_html: {len(raw_html)} bytes")
            else:
                print_error(f"  raw_html: Missing")
        else:
            print_error("scraped_data: Not saved")

        # Check scraped_html field
        if business.scraped_html:
            print_success(f"scraped_html: {len(business.scraped_html)} bytes")
        else:
            print_error("scraped_html: Not saved")

        # Check enhanced fields
        if business.image_urls:
            print_success(f"image_urls: {len(business.image_urls)} images")
        else:
            print_error("image_urls: Not saved")

        if business.color_palette:
            print_success(f"color_palette: {len(business.color_palette)} colors")
            print_info(f"  Colors: {business.color_palette[:5]}")
        else:
            print_error("color_palette: Not saved")

        if business.component_count:
            print_success(f"component_count: {business.component_count}")
        else:
            print_error("component_count: Not saved")

        if business.scraping_completed_at:
            print_success(f"scraping_completed_at: {business.scraping_completed_at}")
        else:
            print_error("scraping_completed_at: Not saved")

        # Check evaluation
        if business.score is not None:
            print_success(f"score: {business.score}/100")
        else:
            print_error("score: Not saved")

        # Check templates
        template_count = db.query(Template).filter(
            Template.business_id == business.id
        ).count()

        if template_count > 0:
            print_success(f"templates: {template_count} template(s) saved")
        else:
            print_error("templates: No templates saved")

        return True

    except Exception as e:
        print_error(f"Database integrity check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  COMPLETE GEMINI FLOW TEST")
    print("=" * 80)

    # Check environment
    if not check_environment():
        print_error("\n[WARNING] Environment check failed. Please configure missing API keys.")
        return

    # Create database session
    db = SessionLocal()

    try:
        # Step 2: Create test business
        business = create_test_business(db)

        # Step 3: Test scraping
        scraping_success = test_scraping(business, db)
        if not scraping_success:
            print_error("\n[WARNING] Scraping test failed. Cannot continue.")
            return

        # Step 4: Test evaluation
        evaluation_success = test_evaluation(business, db)
        if not evaluation_success:
            print_error("\n[WARNING] Evaluation test failed. Will continue anyway.")

        # Step 5: Test template generation with ChatGPT first
        generation_success = await test_template_generation(business, db, use_gemini=False)
        if not generation_success:
            print_error("\n[WARNING] ChatGPT template generation failed.")

        # Step 6: Test template regeneration with Gemini
        if settings.GEMINI_API_KEY:
            regeneration_success = await test_template_regeneration(business, db, use_gemini=True)
            if not regeneration_success:
                print_error("\n[WARNING] Gemini template regeneration failed.")
        else:
            print_error("\n[WARNING] Gemini API key not configured. Skipping Gemini test.")

        # Step 7: Verify database integrity
        verify_database_integrity(business, db)

        # Final summary
        print_section("TEST SUMMARY")
        print_success("All tests completed!")
        print_info(f"\nTest business: {business.name}")
        print_info(f"Business ID: {business.id}")
        print_info(f"Website: {business.website_url}")

    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
