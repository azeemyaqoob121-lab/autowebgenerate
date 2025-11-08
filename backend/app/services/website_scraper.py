"""
Intelligent Website Content Scraper
Extracts ALL content from existing business websites to create improved versions
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional, Any
import json
from collections import Counter

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class WebsiteContentScraper:
    """
    Comprehensive website content scraper that extracts:
    - Logo and branding assets
    - All text content (headlines, about, services, menu)
    - Images with URLs
    - Color scheme
    - Navigation structure
    - Contact information
    - Social media links
    - Certifications and awards
    - Team members
    - Reviews and testimonials
    """

    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.soup = None
        self.html = None

    def fetch_website(self) -> bool:
        """Fetch the website HTML"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()

            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            logger.info(f"Successfully fetched website: {self.url}")
            return True

        except Exception as e:
            logger.error(f"Failed to fetch website {self.url}: {str(e)}")
            return False

    def extract_logo(self) -> Optional[str]:
        """Extract logo image URL"""
        try:
            # Common logo selectors
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                '.logo img',
                '#logo img',
                'header img:first-of-type',
                '.navbar-brand img',
                '.site-logo img',
                '.brand img'
            ]

            for selector in logo_selectors:
                logo = self.soup.select_one(selector)
                if logo and logo.get('src'):
                    logo_url = urljoin(self.url, logo['src'])
                    logger.info(f"Found logo: {logo_url}")
                    return logo_url

            # Fallback: Get first image in header
            header = self.soup.find(['header', 'nav'])
            if header:
                img = header.find('img')
                if img and img.get('src'):
                    logo_url = urljoin(self.url, img['src'])
                    logger.info(f"Found logo in header: {logo_url}")
                    return logo_url

        except Exception as e:
            logger.error(f"Error extracting logo: {str(e)}")

        return None

    def extract_headlines(self) -> Dict[str, str]:
        """Extract main headlines and taglines"""
        headlines = {}

        try:
            # Page title
            title = self.soup.find('title')
            if title:
                headlines['page_title'] = title.get_text().strip()

            # H1 (main headline)
            h1 = self.soup.find('h1')
            if h1:
                headlines['main_headline'] = h1.get_text().strip()

            # Meta description
            meta_desc = self.soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                headlines['meta_description'] = meta_desc['content'].strip()

            # Hero section text
            hero_sections = self.soup.select('.hero, .banner, .jumbotron, #hero, [class*="hero"]')
            for hero in hero_sections[:1]:  # Just first hero
                text = hero.get_text().strip()
                if text and len(text) > 20:
                    headlines['hero_text'] = text[:500]  # First 500 chars
                    break

            logger.info(f"Extracted {len(headlines)} headlines")

        except Exception as e:
            logger.error(f"Error extracting headlines: {str(e)}")

        return headlines

    def extract_about_content(self) -> Optional[str]:
        """Extract About/Company description content"""
        try:
            # Common about section selectors
            about_selectors = [
                '#about',
                '.about',
                '[class*="about"]',
                '#company',
                '.company-info',
                '#story',
                '.our-story'
            ]

            for selector in about_selectors:
                about_section = self.soup.select_one(selector)
                if about_section:
                    text = about_section.get_text().strip()
                    if len(text) > 50:
                        logger.info(f"Found about content: {len(text)} characters")
                        return text[:2000]  # Limit to 2000 chars

            # Fallback: Look for paragraphs with company keywords
            paragraphs = self.soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 100 and any(keyword in text.lower() for keyword in ['we are', 'our', 'company', 'established', 'founded', 'passion', 'mission', 'vision']):
                    logger.info(f"Found about content in paragraph: {len(text)} characters")
                    return text[:2000]

        except Exception as e:
            logger.error(f"Error extracting about content: {str(e)}")

        return None

    def extract_services_or_menu(self) -> List[Dict[str, Any]]:
        """Extract services (for service businesses) or menu items (for restaurants)"""
        items = []

        try:
            # Look for menu sections (restaurants)
            menu_sections = self.soup.select('[class*="menu"], [id*="menu"]')
            for section in menu_sections:
                # Get category/section name
                category_elem = section.find(['h2', 'h3', 'h4'])
                category = category_elem.get_text().strip() if category_elem else "Main Menu"

                # Get items
                list_items = section.find_all(['li', '.menu-item', '.item', '[class*="dish"]'])
                for item in list_items[:20]:  # Limit to 20 items per section
                    text = item.get_text().strip()
                    if text and len(text) > 3:
                        items.append({
                            'category': category,
                            'name': text[:200],
                            'type': 'menu_item'
                        })

            # Look for services sections
            service_sections = self.soup.select('[class*="service"], [id*="service"], [class*="offering"]')
            for section in service_sections:
                # Get service cards/items
                service_items = section.find_all(['div', 'article', 'li'], class_=re.compile(r'(service|card|item)'))
                for item in service_items[:15]:  # Limit to 15 services
                    title_elem = item.find(['h3', 'h4', 'h5', 'strong'])
                    desc_elem = item.find('p')

                    if title_elem:
                        title = title_elem.get_text().strip()
                        desc = desc_elem.get_text().strip() if desc_elem else ""

                        items.append({
                            'category': 'Services',
                            'name': title,
                            'description': desc[:300],
                            'type': 'service'
                        })

            logger.info(f"Extracted {len(items)} services/menu items")

        except Exception as e:
            logger.error(f"Error extracting services/menu: {str(e)}")

        return items

    def extract_images(self) -> List[str]:
        """Extract all meaningful images (excluding icons and tiny images)"""
        images = []

        try:
            img_tags = self.soup.find_all('img')
            for img in img_tags[:50]:  # Limit to 50 images
                src = img.get('src') or img.get('data-src')
                if not src:
                    continue

                # Skip tiny images, icons, and logos
                if any(keyword in src.lower() for keyword in ['icon', 'logo', 'sprite', 'pixel', 'arrow', 'bullet']):
                    continue

                # Get absolute URL
                img_url = urljoin(self.url, src)

                # Get alt text for context
                alt_text = img.get('alt', '')

                images.append({
                    'url': img_url,
                    'alt': alt_text[:200]
                })

            logger.info(f"Extracted {len(images)} images")

        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")

        return images

    def extract_contact_info(self) -> Dict[str, Any]:
        """Extract contact information"""
        contact = {}

        try:
            # Phone numbers
            phone_pattern = r'(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}'
            text = self.soup.get_text()
            phones = re.findall(phone_pattern, text)
            if phones:
                # Clean and format first phone
                phone = ''.join(phones[0]).strip()
                contact['phone'] = phone

            # Email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                contact['email'] = emails[0]

            # Address (look in footer or contact sections)
            address_sections = self.soup.select('.address, .location, [class*="address"], [class*="location"], footer')
            for section in address_sections:
                text = section.get_text().strip()
                # Look for UK postcodes
                postcode_pattern = r'[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}'
                if re.search(postcode_pattern, text):
                    contact['address'] = text[:200]
                    break

            # Opening hours
            hours_sections = self.soup.select('[class*="hours"], [class*="opening"]')
            if hours_sections:
                contact['hours'] = hours_sections[0].get_text().strip()[:300]

            logger.info(f"Extracted contact info: {list(contact.keys())}")

        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")

        return contact

    def extract_social_media(self) -> Dict[str, str]:
        """Extract social media links"""
        social = {}

        try:
            # Social media patterns
            social_patterns = {
                'facebook': r'facebook\.com/[\w\-\.]+',
                'instagram': r'instagram\.com/[\w\-\.]+',
                'twitter': r'twitter\.com/[\w\-\.]+',
                'linkedin': r'linkedin\.com/(company|in)/[\w\-\.]+',
                'youtube': r'youtube\.com/(channel|user|c)/[\w\-\.]+',
                'tiktok': r'tiktok\.com/@[\w\-\.]+',
                'tripadvisor': r'tripadvisor\.[a-z\.]+/.+'
            }

            # Check href attributes
            links = self.soup.find_all('a', href=True)
            for link in links:
                href = link['href'].lower()
                for platform, pattern in social_patterns.items():
                    if re.search(pattern, href):
                        social[platform] = link['href']
                        break

            logger.info(f"Found {len(social)} social media links")

        except Exception as e:
            logger.error(f"Error extracting social media: {str(e)}")

        return social

    def extract_colors(self) -> List[str]:
        """Extract dominant color scheme"""
        colors = []

        try:
            # Look for CSS color values in style tags and inline styles
            color_pattern = r'#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}'

            # Check style tags
            style_tags = self.soup.find_all('style')
            for style in style_tags:
                found_colors = re.findall(color_pattern, style.get_text())
                colors.extend(found_colors)

            # Check inline styles
            elements_with_style = self.soup.find_all(style=True)
            for elem in elements_with_style[:100]:
                found_colors = re.findall(color_pattern, elem['style'])
                colors.extend(found_colors)

            # Get most common colors (excluding white, black, grays)
            color_counter = Counter(colors)
            filtered_colors = [c for c in color_counter.most_common(10)
                             if c[0].lower() not in ['#ffffff', '#fff', '#000000', '#000']]

            unique_colors = [c[0] for c in filtered_colors[:5]]
            logger.info(f"Extracted {len(unique_colors)} dominant colors")

            return unique_colors

        except Exception as e:
            logger.error(f"Error extracting colors: {str(e)}")

        return []

    def extract_certifications_awards(self) -> List[str]:
        """Extract certifications, awards, and badges"""
        certifications = []

        try:
            # Keywords to look for
            cert_keywords = ['award', 'certified', 'certification', 'winner', 'accredited', 'approved',
                           'member', 'association', 'badge', 'usda', 'halal', 'organic', 'verified']

            # Check images with relevant alt text
            images = self.soup.find_all('img', alt=True)
            for img in images:
                alt = img['alt'].lower()
                if any(keyword in alt for keyword in cert_keywords):
                    certifications.append(img['alt'])

            # Check text content
            text_elements = self.soup.find_all(['span', 'div', 'p'], class_=re.compile(r'(cert|award|badge)', re.I))
            for elem in text_elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:
                    certifications.append(text)

            # Remove duplicates
            certifications = list(set(certifications))[:10]
            logger.info(f"Found {len(certifications)} certifications/awards")

        except Exception as e:
            logger.error(f"Error extracting certifications: {str(e)}")

        return certifications

    def extract_navigation(self) -> List[str]:
        """Extract main navigation menu items"""
        nav_items = []

        try:
            # Find navigation elements
            nav = self.soup.find(['nav', 'header'])
            if nav:
                links = nav.find_all('a')
                for link in links[:10]:  # Limit to 10 main nav items
                    text = link.get_text().strip()
                    if text and len(text) < 50:
                        nav_items.append(text)

            logger.info(f"Extracted {len(nav_items)} navigation items")

        except Exception as e:
            logger.error(f"Error extracting navigation: {str(e)}")

        return nav_items

    def extract_testimonials(self) -> List[Dict[str, str]]:
        """Extract customer testimonials/reviews"""
        testimonials = []

        try:
            # Common testimonial selectors
            testimonial_sections = self.soup.select('[class*="testimonial"], [class*="review"], [class*="feedback"]')

            for section in testimonial_sections[:5]:  # Limit to 5 testimonials
                # Try to find author
                author_elem = section.find(['cite', 'span', 'strong', 'h4', 'h5'], class_=re.compile(r'(author|name|customer)', re.I))
                author = author_elem.get_text().strip() if author_elem else "Customer"

                # Get testimonial text
                text_elem = section.find(['p', 'blockquote'])
                if text_elem:
                    text = text_elem.get_text().strip()
                    if text and len(text) > 20:
                        testimonials.append({
                            'author': author,
                            'text': text[:500]
                        })

            logger.info(f"Extracted {len(testimonials)} testimonials")

        except Exception as e:
            logger.error(f"Error extracting testimonials: {str(e)}")

        return testimonials

    def fetch_external_css(self) -> str:
        """Fetch external CSS files and return combined CSS content"""
        combined_css = ""

        try:
            # Find all <link> tags with CSS stylesheets
            link_tags = self.soup.find_all('link', rel='stylesheet')

            for link in link_tags[:5]:  # Limit to first 5 stylesheets
                css_url = link.get('href')
                if not css_url:
                    continue

                # Make absolute URL
                css_url = urljoin(self.url, css_url)

                try:
                    logger.info(f"Fetching external CSS: {css_url}")
                    response = requests.get(css_url, timeout=10)
                    response.raise_for_status()
                    combined_css += f"\n/* CSS from {css_url} */\n"
                    combined_css += response.text
                    logger.info(f"✓ Fetched {len(response.text)} chars from {css_url}")
                except Exception as e:
                    logger.warning(f"Failed to fetch CSS {css_url}: {e}")

        except Exception as e:
            logger.error(f"Error fetching external CSS: {e}")

        return combined_css

    def scrape_all(self) -> Dict[str, Any]:
        """
        Master function that extracts ALL content from the website
        Returns a comprehensive dictionary with all scraped data
        """
        logger.info(f"Starting comprehensive scrape of: {self.url}")

        # Fetch the website
        if not self.fetch_website():
            logger.error(f"Failed to fetch website: {self.url}")
            return {}

        # Fetch external CSS files for color extraction
        external_css = self.fetch_external_css()

        # Combine HTML with external CSS for complete color extraction
        raw_html_with_css = self.html + f"\n<style>\n{external_css}\n</style>"

        # Extract all content
        scraped_data = {
            'url': self.url,
            'domain': self.domain,
            'logo': self.extract_logo(),
            'headlines': self.extract_headlines(),
            'about': self.extract_about_content(),
            'services_menu': self.extract_services_or_menu(),
            'images': self.extract_images(),
            'contact': self.extract_contact_info(),
            'social_media': self.extract_social_media(),
            'colors': self.extract_colors(),
            'certifications': self.extract_certifications_awards(),
            'navigation': self.extract_navigation(),
            'testimonials': self.extract_testimonials(),
            'raw_html': raw_html_with_css,  # Include HTML + external CSS
            'text_content': self.soup.get_text()[:5000]  # First 5000 chars of text
        }

        logger.info(f"Scraping complete! Extracted data from {len(scraped_data)} categories")
        logger.info(f"✓ Included {len(external_css)} chars of external CSS")
        return scraped_data


def scrape_business_website(url: str) -> Dict[str, Any]:
    """
    Convenience function to scrape a business website

    Args:
        url: Website URL to scrape

    Returns:
        Dictionary containing all scraped content
    """
    try:
        scraper = WebsiteContentScraper(url)
        return scraper.scrape_all()
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}")
        return {}
