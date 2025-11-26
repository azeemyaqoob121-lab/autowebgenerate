"""
Test script to re-scrape AH Electrical Services and verify component detection
"""
import sys
sys.path.insert(0, 'C:\\Users\\rabia\\Documents\\project AutoWeb Outreach AI\\AutoWeb_Outreach_AI\\backend')

from app.database import SessionLocal
from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService
from app.models.business import Business
import json

# Business ID for AH Electrical Services
BUSINESS_ID = "2edd681b-2cdf-46f9-9bf6-80cad0c00f20"

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("TESTING UPDATED COMPONENT DETECTION")
        print("=" * 80)

        # Load business
        business = db.query(Business).filter(Business.id == BUSINESS_ID).first()

        if not business:
            print(f"[ERROR] Business {BUSINESS_ID} not found - check database!")
            return

        print(f"\nBusiness: {business.name}")
        print(f"URL: {business.website_url}")
        print(f"\nStarting re-scrape with updated component detection...")

        # Re-scrape with updated component detection logic
        scraper = EnhancedWebsiteScraperService(db)
        success = scraper.scrape_complete_website(str(business.id))

        if not success:
            print(f"[ERROR] Re-scraping failed!")
            print(f"Error: {business.scraping_error}")
            return

        # Refresh business to get updated data
        db.refresh(business)

        print("\n" + "=" * 80)
        print("[SUCCESS] RE-SCRAPING COMPLETE - RESULTS:")
        print("=" * 80)

        # Show OLD vs NEW component count
        print(f"\nComponent Count: {business.component_count}")
        print(f"   (Expected: 6+ components for AH Electrical)")

        # Show component structure details
        print(f"\nComponent Structure:")
        if business.component_structure:
            for idx, comp in enumerate(business.component_structure, 1):
                print(f"   {idx}. {comp.get('type', 'unknown').upper()}: {comp.get('heading', 'No heading')[:60]}")
                if comp.get('classes'):
                    print(f"      Classes: {comp.get('classes')[:80]}")
        else:
            print("   [WARNING] No component structure data")

        # Show asset counts
        print(f"\nAssets Extracted:")
        print(f"   - Images: {len(business.image_urls or [])}")
        print(f"   - Logos: {len(business.logo_urls or [])}")
        print(f"   - Videos: {len(business.video_urls or [])}")
        print(f"   - Maps: {len(business.map_embeds or [])}")
        print(f"   - Colors: {len(business.color_palette or [])}")

        # Show color palette
        if business.color_palette:
            print(f"\nColor Palette: {', '.join(business.color_palette[:10])}")

        print("\n" + "=" * 80)

        if business.component_count >= 6:
            print("[SUCCESS] Component detection is working correctly! (6+ components)")
            print("   Ready to regenerate templates with full structure preservation!")
        elif business.component_count >= 3:
            print("[PARTIAL] Detected some components but may need adjustment")
        else:
            print("[ISSUE] Component count still low. May need further investigation.")

        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    main()
