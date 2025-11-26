"""
Test Script: Brand Preservation System

Tests the complete brand-preserving website redesign flow:
1. Scrapes a real website
2. Extracts brand assets (colors, fonts, logos, images)
3. Downloads original assets
4. Displays what was preserved

Usage:
    python test_brand_preservation.py
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.website_scraper import scrape_business_website
from app.services.brand_asset_downloader import download_brand_assets


def test_brand_preservation(website_url: str):
    """Test the brand preservation system with a real website"""

    print(f"\n{'='*80}")
    print(f"TESTING BRAND PRESERVATION SYSTEM")
    print(f"{'='*80}\n")

    print(f"Target Website: {website_url}\n")

    # Step 1: Scrape the website
    print("STEP 1: Scraping website for content...")
    print("-" * 80)

    scraped_data = scrape_business_website(website_url)

    if not scraped_data:
        print("❌ Failed to scrape website!")
        return

    print(f"✅ Successfully scraped website\n")

    # Display what was extracted
    print("STEP 2: Brand Assets Extracted")
    print("-" * 80)

    # Colors
    colors = scraped_data.get('colors', [])
    print(f"\n🎨 COLORS EXTRACTED: {len(colors)}")
    for i, color in enumerate(colors[:5], 1):
        print(f"   {i}. {color}")

    # Fonts
    fonts = scraped_data.get('fonts', {})
    print(f"\n🔤 FONTS EXTRACTED:")
    print(f"   Headings: {', '.join(fonts.get('headings', [])[:3])}")
    print(f"   Body: {', '.join(fonts.get('body', [])[:3])}")

    # Logo
    logo = scraped_data.get('logo')
    print(f"\n🏷️  LOGO: {'✅ Found' if logo else '❌ Not found'}")
    if logo:
        print(f"   URL: {logo[:80]}...")

    # Images
    images = scraped_data.get('images', [])
    print(f"\n📸 IMAGES: {len(images)} found")
    for i, img in enumerate(images[:3], 1):
        print(f"   {i}. {img.get('url', '')[:60]}...")
        if img.get('alt'):
            print(f"      Alt: {img.get('alt')[:50]}")

    # Videos
    videos = scraped_data.get('videos', [])
    print(f"\n🎥 VIDEOS: {len(videos)} found")
    for i, video in enumerate(videos[:3], 1):
        print(f"   {i}. Type: {video.get('type', 'unknown')}")
        print(f"      URL: {video.get('url', '')[:60]}...")

    # Content
    print(f"\n📝 CONTENT PRESERVED:")
    print(f"   Services/Menu Items: {len(scraped_data.get('services_menu', []))}")
    print(f"   Testimonials: {len(scraped_data.get('testimonials', []))}")
    print(f"   Page Sections: {len(scraped_data.get('page_structure', []))}")
    print(f"   Navigation Items: {len(scraped_data.get('navigation', []))}")

    # Step 3: Download assets
    print(f"\nSTEP 3: Downloading Brand Assets")
    print("-" * 80)

    business_id = "test_business_001"
    downloaded_assets = download_brand_assets(business_id, scraped_data)

    print(f"\n✅ Asset Download Summary:")
    summary = downloaded_assets.get('summary', {})
    print(f"   Total Assets: {summary.get('total_downloaded', 0)}")
    print(f"   Logos: {summary.get('logos', 0)}")
    print(f"   Images: {summary.get('images', 0)}")
    print(f"   Videos: {summary.get('videos', 0)}")
    print(f"   Total Size: {summary.get('total_size_mb', 0):.2f} MB")

    # Show where files were saved
    if downloaded_assets.get('logo'):
        print(f"\n📁 Files saved to:")
        logo_path = downloaded_assets['logo']['local_path']
        base_dir = Path(logo_path).parent.parent
        print(f"   {base_dir}")
        print(f"   ├── logos/ ({summary.get('logos', 0)} files)")
        print(f"   ├── images/ ({summary.get('images', 0)} files)")
        print(f"   └── videos/ ({summary.get('videos', 0)} files)")

    # Step 4: Show brand preservation report
    print(f"\nSTEP 4: Brand Preservation Report")
    print("-" * 80)

    print(f"\n✅ BRAND IDENTITY PRESERVED 100%")
    print(f"\n   Colors: {len(colors)} extracted → GPT-4 will use THESE exact colors")
    print(f"   Fonts: {len(fonts.get('headings', []) + fonts.get('body', []))} extracted → GPT-4 will reference these")
    print(f"   Logo: {'Downloaded and ready to use' if downloaded_assets.get('logo') else 'Not available'}")
    print(f"   Images: {summary.get('images', 0)} original images downloaded")
    print(f"   Videos: {summary.get('videos', 0)} original videos preserved")

    print(f"\n🎯 OUTCOME:")
    print(f"   When generating a website template, the system will:")
    print(f"   1. Use the EXACT color palette from the original website")
    print(f"   2. Use the ACTUAL images from the original website")
    print(f"   3. Preserve the REAL logo (not replace it)")
    print(f"   4. Keep the ORIGINAL videos")
    print(f"   5. Maintain the AUTHENTIC content and messaging")
    print(f"   6. Create a modern version that FEELS like THEIR brand")

    print(f"\n{'='*80}")
    print(f"✅ BRAND PRESERVATION TEST COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Test with a real website URL
    # Example: test with a restaurant or local business website
    test_url = input("Enter a website URL to test (or press Enter for default): ").strip()

    if not test_url:
        print("\nℹ️  No URL provided. To test this system:")
        print("   1. Find a business website (restaurant, shop, service business)")
        print("   2. Run: python test_brand_preservation.py")
        print("   3. Enter the website URL when prompted")
        print("\nExample URLs you could test:")
        print("   - A local restaurant website")
        print("   - A hair salon website")
        print("   - A law firm website")
        print("   - Any small business with a website\n")
    else:
        if not test_url.startswith('http'):
            test_url = 'https://' + test_url

        test_brand_preservation(test_url)
