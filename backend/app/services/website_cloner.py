"""
Website Cloner Service

Downloads the original website HTML/CSS and creates a cleaned, improved version
that maintains the EXACT same visual structure and layout.

This is NOT a template generator - it CLONES the original website!
"""

import re
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import urllib3

# Disable SSL warnings for cloning (some websites have certificate issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WebsiteCloner:
    """
    Clones an existing website while preserving its exact visual structure.

    Strategy:
    1. Download original HTML
    2. Download all CSS files
    3. Fix broken links and assets
    4. Clean up code
    5. Improve content with GPT-4 (optional)
    6. Return website that LOOKS IDENTICAL to original
    """

    def __init__(self, url: str):
        """Initialize the cloner with a target URL"""
        self.url = url
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.html = ""
        self.soup = None
        self.css_files = []

    def fetch_original_html(self) -> bool:
        """Download the original HTML from the website - works for both HTTP and HTTPS"""
        try:
            logger.info(f"[CLONE] Downloading original HTML from: {self.url}")

            # Enhanced headers to bypass anti-bot protection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
            }

            # Detect if URL is HTTP or HTTPS and try the correct one first
            is_https = self.url.startswith('https://')
            is_http = self.url.startswith('http://')

            # If no protocol, add https://
            if not is_https and not is_http:
                self.url = 'https://' + self.url
                is_https = True

            success = False
            response = None

            # Try the primary protocol first
            try:
                logger.info(f"[CLONE] Trying primary URL: {self.url}")
                response = requests.get(self.url, headers=headers, timeout=30, allow_redirects=True, verify=False)
                response.raise_for_status()
                success = True
            except Exception as e:
                logger.warning(f"[CLONE] Primary URL failed: {e}")

                # Try alternative protocol
                if is_https:
                    # Try HTTP
                    http_url = self.url.replace('https://', 'http://')
                    logger.info(f"[CLONE] HTTPS failed, trying HTTP: {http_url}")
                    try:
                        response = requests.get(http_url, headers=headers, timeout=30, allow_redirects=True)
                        response.raise_for_status()
                        self.url = http_url
                        self.base_url = f"{urlparse(http_url).scheme}://{urlparse(http_url).netloc}"
                        success = True
                    except Exception as e2:
                        logger.error(f"[CLONE] HTTP fallback also failed: {e2}")
                else:
                    # Try HTTPS
                    https_url = self.url.replace('http://', 'https://')
                    logger.info(f"[CLONE] HTTP failed, trying HTTPS: {https_url}")
                    try:
                        response = requests.get(https_url, headers=headers, timeout=30, allow_redirects=True, verify=False)
                        response.raise_for_status()
                        self.url = https_url
                        self.base_url = f"{urlparse(https_url).scheme}://{urlparse(https_url).netloc}"
                        success = True
                    except Exception as e2:
                        logger.error(f"[CLONE] HTTPS fallback also failed: {e2}")

            if not success or not response:
                raise Exception("Could not fetch website via HTTP or HTTPS")

            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')

            logger.info(f"[CLONE] Successfully downloaded {len(self.html)} bytes of HTML from {self.url}")
            return True

        except Exception as e:
            logger.error(f"[CLONE] Failed to fetch original HTML: {e}")
            return False

    def download_css_files(self) -> List[str]:
        """Download all CSS files from the original website"""
        css_content = []

        try:
            # Find all <link> tags with stylesheets
            link_tags = self.soup.find_all('link', rel='stylesheet')

            logger.info(f"[CLONE] Found {len(link_tags)} CSS files to download")

            for link in link_tags[:10]:  # Limit to 10 CSS files
                href = link.get('href')
                if not href:
                    continue

                # Make absolute URL
                css_url = urljoin(self.base_url, href)

                try:
                    logger.info(f"[CLONE] Downloading CSS: {css_url}")
                    response = requests.get(css_url, timeout=10)
                    response.raise_for_status()
                    css_content.append(response.text)
                    logger.info(f"[CLONE] Downloaded {len(response.text)} bytes of CSS")
                except Exception as e:
                    logger.warning(f"[CLONE] Failed to download CSS {css_url}: {e}")

            self.css_files = css_content
            logger.info(f"[CLONE] Successfully downloaded {len(css_content)} CSS files")
            return css_content

        except Exception as e:
            logger.error(f"[CLONE] Error downloading CSS files: {e}")
            return []

    def clean_and_fix_html(self, downloaded_assets: Dict[str, Any]) -> str:
        """
        Clean the HTML and fix broken links while maintaining structure.

        This KEEPS the original HTML structure EXACTLY as-is, just fixes:
        - Broken image links
        - Broken CSS links
        - Broken script links
        - Invalid URLs
        """
        try:
            logger.info("[CLONE] Cleaning and fixing HTML while preserving structure...")

            # 1. Fix image sources - replace with downloaded images
            images_map = {}
            if downloaded_assets and 'images' in downloaded_assets:
                for img_data in downloaded_assets['images']:
                    # Handle both dict and ImageAsset object
                    if isinstance(img_data, dict):
                        original_url = img_data.get('original_url', '')
                        local_url = img_data.get('url', '')
                    else:
                        # ImageAsset object - has attributes not dict keys
                        original_url = getattr(img_data, 'original_url', '') or getattr(img_data, 'url', '')
                        local_url = getattr(img_data, 'url', '')

                    if original_url and local_url:
                        images_map[original_url] = local_url

            # Replace image sources
            for img in self.soup.find_all('img'):
                src = img.get('src')
                if src:
                    abs_src = urljoin(self.base_url, src)
                    if abs_src in images_map:
                        img['src'] = images_map[abs_src]
                        logger.info(f"[CLONE] Fixed image: {src} -> {images_map[abs_src]}")

            # 2. Inline all CSS
            if self.css_files:
                # Remove external CSS links
                for link in self.soup.find_all('link', rel='stylesheet'):
                    link.decompose()

                # Add inline CSS in <head>
                head = self.soup.find('head')
                if head:
                    style_tag = self.soup.new_tag('style')
                    style_tag.string = '\n'.join(self.css_files)
                    head.append(style_tag)
                    logger.info(f"[CLONE] Inlined {len(self.css_files)} CSS files")

            # 3. Remove tracking scripts and analytics
            for script in self.soup.find_all('script'):
                src = script.get('src', '')
                if any(tracker in src.lower() for tracker in ['google-analytics', 'gtag', 'facebook', 'tracking']):
                    script.decompose()
                    logger.info(f"[CLONE] Removed tracking script: {src}")

            # 4. Fix meta tags
            viewport = self.soup.find('meta', attrs={'name': 'viewport'})
            if not viewport:
                head = self.soup.find('head')
                if head:
                    meta = self.soup.new_tag('meta')
                    meta['name'] = 'viewport'
                    meta['content'] = 'width=device-width, initial-scale=1.0'
                    head.insert(0, meta)
                    logger.info("[CLONE] Added missing viewport meta tag")

            # 5. Convert to string
            cloned_html = str(self.soup)

            logger.info(f"[CLONE] Cleaning complete! Generated {len(cloned_html)} bytes of HTML")
            return cloned_html

        except Exception as e:
            logger.error(f"[CLONE] Error cleaning HTML: {e}")
            return str(self.soup)

    def clone_website(self, downloaded_assets: Dict[str, Any] = None) -> str:
        """
        Main method: Clone the entire website.

        Returns the cloned HTML that looks EXACTLY like the original.
        """
        try:
            logger.info(f"[CLONE] Starting website cloning process for: {self.url}")

            # Step 1: Download original HTML
            if not self.fetch_original_html():
                raise Exception("Failed to fetch original HTML")

            # Step 2: Download CSS files
            self.download_css_files()

            # Step 3: Clean and fix HTML
            cloned_html = self.clean_and_fix_html(downloaded_assets or {})

            logger.info(f"[CLONE] Website cloning complete! Size: {len(cloned_html)} bytes")
            return cloned_html

        except Exception as e:
            logger.error(f"[CLONE] Website cloning failed: {e}")
            raise Exception(f"Failed to clone website: {str(e)}")
