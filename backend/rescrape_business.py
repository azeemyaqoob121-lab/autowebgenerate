"""
Re-scrape a business website to get fresh clean HTML with the fixed scraper.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business
from app.services.website_scraper import scrape_business_website

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rescrape_business(business_id: str):
    """Re-scrape a business website with the fixed scraper"""
    db: Session = SessionLocal()

    try:
        # Find the business
        business = db.query(Business).filter(Business.id == business_id).first()

        if not business:
            logger.error(f"Business with ID {business_id} not found")
            return False

        logger.info(f"Found business: {business.name}")
        logger.info(f"Website URL: {business.website_url}")

        # Re-scrape the website
        logger.info("Re-scraping website with fixed scraper...")
        scraped_data = scrape_business_website(business.website_url)

        if not scraped_data:
            logger.error("Failed to scrape website")
            return False

        # Update the business with new scraped data
        logger.info("Updating business with fresh scraped data...")

        business.scraped_html = scraped_data.get('raw_html', '')
        business.scraped_css = scraped_data.get('css', '')
        business.scraped_data = scraped_data
        business.external_css_urls = scraped_data.get('external_css', [])
        business.image_urls = scraped_data.get('images', [])
        business.logo_urls = scraped_data.get('logo', [])
        business.color_palette = scraped_data.get('colors', [])

        db.commit()

        logger.info("✅ Successfully re-scraped and updated business!")
        logger.info(f"   HTML length: {len(business.scraped_html)} characters")
        logger.info(f"   Has <body>: {'<body' in business.scraped_html.lower()}")
        logger.info(f"   Has </html>: {'</html>' in business.scraped_html.lower()}")

        # Show a preview of the HTML
        html_preview = business.scraped_html[:200]
        logger.info(f"   HTML preview: {html_preview}")

        return True

    except Exception as e:
        logger.error(f"Error re-scraping business: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Re-scrape a business website")
    parser.add_argument("business_id", help="Business ID to re-scrape")

    args = parser.parse_args()

    logger.info(f"Re-scraping business: {args.business_id}")
    logger.info("")

    rescrape_business(args.business_id)
