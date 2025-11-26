"""
Enhanced Website Scraper Service
Comprehensive website scraping with Selenium support, retry logic, and database integration.
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

import time
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

from app.models.business import Business
from app.services.asset_extractor_service import AssetExtractorService
from app.services.website_scraper import WebsiteContentScraper
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedWebsiteScraperService:
    """
    Enhanced website scraper with:
    - HTTP/HTTPS support
    - Selenium headless browser for JavaScript-heavy sites
    - Retry logic with exponential backoff
    - Complete HTML/CSS extraction
    - Asset cataloging (images, logos, videos, maps, colors)
    - Component structure analysis
    - Database integration for Business model
    """

    def __init__(self, db: Session):
        """
        Initialize scraper service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.max_retries = 3
        self.timeout = 30

    def scrape_complete_website(self, business_id: str) -> bool:
        """
        Scrape complete website for a business and store in database.

        This is the main entry point for enhanced scraping.

        Args:
            business_id: UUID of business to scrape

        Returns:
            True if scraping succeeded, False otherwise
        """
        try:
            # Load business from database
            business = self.db.query(Business).filter(Business.id == business_id).first()
            if not business:
                logger.error(f"[EnhancedScraper] Business {business_id} not found")
                return False

            url = business.website_url
            if not url:
                logger.error(f"[EnhancedScraper] Business {business_id} has no website URL")
                return False

            logger.info(f"[EnhancedScraper] Starting scrape for {business.name}: {url}")

            # Try standard scraping first (faster)
            html, css = self._scrape_with_requests(url)

            # If failed, try Selenium (handles JS-heavy sites)
            if not html:
                logger.info(f"[EnhancedScraper] Standard scraping failed, trying Selenium for {url}")
                html, css = self._scrape_with_selenium(url)

            # If both failed, log error and return
            if not html:
                error_msg = f"Failed to scrape {url} after trying requests and Selenium"
                logger.error(f"[EnhancedScraper] {error_msg}")
                business.scraping_error = error_msg
                business.scraping_completed_at = None
                self.db.commit()
                return False

            # Extract CSS (inline and external)
            external_css_urls = self._extract_external_css_urls(html, url)

            # Use AssetExtractorService to parse assets
            extractor = AssetExtractorService(base_url=url, html=html, css=css)
            assets = extractor.extract_all_assets()

            # Store everything in database
            business.scraped_html = html
            business.scraped_css = css
            business.external_css_urls = external_css_urls
            business.image_urls = assets['image_urls']
            business.logo_urls = assets['logo_urls']
            business.video_urls = assets['video_urls']
            business.map_embeds = assets['map_embeds']
            business.color_palette = assets['color_palette']
            business.component_count = assets['component_count']
            business.component_structure = assets['component_structure']
            business.scraping_completed_at = datetime.utcnow()
            business.scraping_error = None

            self.db.commit()

            logger.info(f"[EnhancedScraper] ✅ Successfully scraped {business.name}: "
                       f"{len(assets['image_urls'])} images, {len(assets['logo_urls'])} logos, "
                       f"{len(assets['video_urls'])} videos, {len(assets['color_palette'])} colors, "
                       f"{assets['component_count']} components")

            return True

        except Exception as e:
            logger.error(f"[EnhancedScraper] Unexpected error scraping business {business_id}: {str(e)}")
            if business:
                business.scraping_error = f"Unexpected error: {str(e)}"
                business.scraping_completed_at = None
                self.db.commit()
            return False

    def _scrape_with_requests(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """
        Scrape website using requests library (fast, works for static sites).

        Includes retry logic with exponential backoff.

        Args:
            url: Website URL to scrape

        Returns:
            Tuple of (html, css) or (None, None) if failed
        """
        for attempt in range(self.max_retries):
            try:
                # Enhanced headers to bypass bot protection
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                }

                response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
                response.raise_for_status()

                html = response.text

                # Extract inline CSS from <style> tags
                scraper = WebsiteContentScraper(url)
                scraper.html = html
                scraper.soup = scraper.soup if scraper.soup else BeautifulSoup(html, 'html.parser')

                # Fetch external CSS
                external_css = scraper.fetch_external_css()

                # Combine inline CSS (from <style> tags) with external CSS
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                style_tags = soup.find_all('style')
                inline_css = '\n'.join([style.get_text() for style in style_tags])
                combined_css = inline_css + "\n" + external_css

                logger.info(f"[EnhancedScraper] ✅ Scraped {url} with requests (attempt {attempt + 1})")
                return html, combined_css

            except requests.exceptions.SSLError as e:
                logger.warning(f"[EnhancedScraper] SSL error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                return None, None

            except requests.exceptions.Timeout as e:
                logger.warning(f"[EnhancedScraper] Timeout on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, None

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else "unknown"
                logger.warning(f"[EnhancedScraper] HTTP {status_code} error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1 and status_code not in [404, 403, 410]:
                    time.sleep(2 ** attempt)
                    continue
                return None, None

            except Exception as e:
                logger.warning(f"[EnhancedScraper] Error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, None

        return None, None

    def _scrape_with_selenium(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """
        Scrape website using Selenium headless Chrome (handles JavaScript-heavy sites).

        Args:
            url: Website URL to scrape

        Returns:
            Tuple of (html, css) or (None, None) if failed
        """
        driver = None
        try:
            # Set up headless Chrome
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)

            # Load page
            driver.get(url)

            # Wait for body to load
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.TAG_NAME, 'body')
            )

            # Give JavaScript time to render (2 seconds)
            time.sleep(2)

            # Get rendered HTML
            html = driver.page_source

            # Extract CSS (inline + external)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            style_tags = soup.find_all('style')
            inline_css = '\n'.join([style.get_text() for style in style_tags])

            # Fetch external CSS using requests
            scraper = WebsiteContentScraper(url)
            scraper.html = html
            scraper.soup = soup
            external_css = scraper.fetch_external_css()

            combined_css = inline_css + "\n" + external_css

            logger.info(f"[EnhancedScraper] ✅ Scraped {url} with Selenium (JS-rendered)")
            return html, combined_css

        except TimeoutException:
            logger.error(f"[EnhancedScraper] Selenium timeout for {url}")
            return None, None

        except WebDriverException as e:
            logger.error(f"[EnhancedScraper] Selenium WebDriver error for {url}: {str(e)}")
            return None, None

        except Exception as e:
            logger.error(f"[EnhancedScraper] Selenium error for {url}: {str(e)}")
            return None, None

        finally:
            if driver:
                driver.quit()

    def _extract_external_css_urls(self, html: str, base_url: str) -> list[str]:
        """
        Extract external CSS file URLs from HTML.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative URLs

        Returns:
            List of absolute CSS file URLs
        """
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        css_urls = []

        try:
            soup = BeautifulSoup(html, 'html.parser')
            link_tags = soup.find_all('link', rel='stylesheet')

            for link in link_tags:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    css_urls.append(absolute_url)

            logger.info(f"[EnhancedScraper] Found {len(css_urls)} external CSS files")

        except Exception as e:
            logger.error(f"[EnhancedScraper] Error extracting CSS URLs: {str(e)}")

        return css_urls


def scrape_business_complete(db: Session, business_id: str) -> bool:
    """
    Convenience function to scrape a business website.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        True if successful, False otherwise
    """
    scraper = EnhancedWebsiteScraperService(db)
    return scraper.scrape_complete_website(business_id)
