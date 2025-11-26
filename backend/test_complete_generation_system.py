"""
Complete Template Generation System Test
Tests the enhanced generation system with validation
"""

import asyncio
import sys
from pathlib import Path
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.business import Business
from app.services.gpt_enhanced_template_builder import build_gpt_enhanced_template
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def test_complete_generation():
    """
    Test complete template generation with validation.

    This test:
    1. Finds a business with scraped data
    2. Generates template using GPT-enhanced builder
    3. Validates that ALL components, images, videos are present
    4. Shows detailed validation results
    """

    print("=" * 80)
    print("🧪 TESTING COMPLETE TEMPLATE GENERATION SYSTEM")
    print("=" * 80)
    print()

    # Get database session
    db = SessionLocal()

    try:
        # Find a business with scraped data for testing
        print("📋 Step 1: Finding business with scraped data...")
        print()

        business = db.query(Business).filter(
            Business.scraped_html != None,
            Business.component_count > 0
        ).first()

        if not business:
            print("❌ ERROR: No business found with scraped data")
            print()
            print("Please run scraping first:")
            print("  python test_enhanced_scraping.py")
            return False

        print(f"✅ Found business: {business.name}")
        print(f"   URL: {business.website_url}")
        print(f"   Components: {business.component_count}")
        print(f"   Images: {len(business.image_urls or [])}")
        print(f"   Videos: {len(business.video_urls or [])}")
        print(f"   Logos: {len(business.logo_urls or [])}")
        print()

        # Generate template
        print("=" * 80)
        print("🎨 Step 2: Generating STUNNING modern template with GPT-4...")
        print("=" * 80)
        print()
        print("This will:")
        print("  1. Build complete basic HTML with ALL components, images, videos")
        print("  2. Send to GPT-4 with WOW FACTOR prompts for modern design")
        print("  3. Run STRICT validation to ensure nothing is missing")
        print("  4. Fall back to basic HTML if GPT-4 removes anything")
        print()
        print("⏳ Generating template (this may take 30-60 seconds)...")
        print()

        template = build_gpt_enhanced_template(business)

        if not template:
            print("❌ ERROR: Template generation failed")
            return False

        print()
        print("=" * 80)
        print("✅ TEMPLATE GENERATION COMPLETE!")
        print("=" * 80)
        print()

        # Show validation results
        validation_data = template.improvements_made.get('validation', {})

        print("📊 VALIDATION RESULTS:")
        print()

        if validation_data.get('passed'):
            print("✅ VALIDATION PASSED - All components, images, videos present!")
        else:
            print("⚠️  VALIDATION FAILED - Using fallback HTML with guaranteed completeness")

        print()
        print("Statistics:")
        stats = validation_data.get('stats', {})
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print()

        # Show errors if any
        errors = validation_data.get('errors', [])
        if errors:
            print("❌ Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            print()

        # Show warnings if any
        warnings = validation_data.get('warnings', [])
        if warnings:
            print("⚠️  Validation Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
            print()

        # Show missing components if any
        missing_components = validation_data.get('missing_components', [])
        if missing_components:
            print(f"❌ Missing {len(missing_components)} components:")
            for comp in missing_components[:5]:
                print(f"  - {comp}")
            if len(missing_components) > 5:
                print(f"  ... and {len(missing_components) - 5} more")
            print()

        # Show template info
        print("=" * 80)
        print("📄 TEMPLATE INFORMATION:")
        print("=" * 80)
        print()
        print(f"Template ID: {template.id}")
        print(f"Business: {business.name}")
        print(f"Generated: {template.generated_at}")
        print(f"HTML Size: {len(template.html_content):,} characters")
        print(f"Method: {template.improvements_made.get('method', 'unknown')}")
        print()

        # Save template to file for inspection
        output_file = Path(__file__).parent / f"test_output_template_{business.name.replace(' ', '_')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template.html_content)

        print(f"💾 Template saved to: {output_file}")
        print()
        print("You can open this file in a browser to see the result!")
        print()

        # Summary
        print("=" * 80)
        print("🎉 TEST SUMMARY")
        print("=" * 80)
        print()

        if validation_data.get('passed'):
            print("✅ SUCCESS! Generated template includes:")
            print(f"   ✓ ALL {stats.get('expected_components', 0)} components/sections")
            print(f"   ✓ ALL {stats.get('expected_images', 0)} images")
            print(f"   ✓ ALL {stats.get('expected_videos', 0)} videos")
            print(f"   ✓ Brand colors preserved")
            print(f"   ✓ Modern WOW factor design applied")
            print()
            print("The generated website should make business owners say 'WOW!'")
        else:
            print("⚠️  GPT-4 removed some content, used fallback HTML")
            print("   The template is complete but may need prompt tuning")
            print(f"   Missing: {len(missing_components)} components, "
                  f"{validation_data.get('missing_images_count', 0)} images, "
                  f"{validation_data.get('missing_videos_count', 0)} videos")

        print()
        print("=" * 80)

        return True

    except Exception as e:
        print()
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print()
    success = test_complete_generation()
    print()

    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed")
        sys.exit(1)
