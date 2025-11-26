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


def validate_scraped_html(html: str, url: str) -> bool:
    """
    Validate that scraped HTML is clean and usable.

    IMPORTANT: This validation is now LESS STRICT to avoid false positives.
    Modern websites often have binary data in SVGs, data URIs, and other embedded content.
    We only reject HTML if it's COMPLETELY corrupted (no structure or starts with garbage).

    Checks for:
    - Minimum length requirement
    - Basic HTML structure present
    - Not starting with binary garbage (first 100 chars should be mostly printable)

    Args:
        html: HTML string to validate
        url: URL that was scraped (for logging)

    Returns:
        True if valid, False if completely corrupted or invalid
    """
    if not html or len(html) < 100:
        logger.error(f"[VALIDATION FAILED] HTML too short or empty for {url}")
        return False

    # Check for basic HTML structure first
    html_lower = html.lower()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    has_body_tag = '<body' in html_lower or '<div' in html_lower  # Allow div-only pages

    if not (has_html_tag or has_body_tag):
        logger.error(f"[VALIDATION FAILED] Missing basic HTML structure tags for {url}")
        return False

    # LESS STRICT: Only check if HTML STARTS with binary garbage (first 100 chars)
    # Modern websites often have binary data embedded in SVGs, data URIs, etc.
    # We only reject if the HTML is completely corrupted (no readable text at start)
    first_100 = html[:100].strip()

    # Count printable characters in first 100 chars
    printable_count = sum(1 for c in first_100 if c.isprintable() or c in ['\n', '\r', '\t'])

    # If less than 70% of first 100 chars are printable, it's likely corrupted
    if len(first_100) > 0 and (printable_count / len(first_100)) < 0.7:
        logger.error(f"[VALIDATION FAILED] HTML starts with binary garbage (only {printable_count}/{len(first_100)} printable chars) from {url}")
        return False

    logger.info(f"[VALIDATION PASSED] HTML has valid structure and is usable for {url}")
    return True


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
        """Fetch the website HTML with HTTP/HTTPS fallback"""
        # Enhanced headers to bypass anti-bot protection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            # IMPORTANT: Don't request 'br' (brotli) encoding unless brotli package is installed
            # Otherwise requests library won't decompress and we'll get binary garbage
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }

        # Try original URL first
        try:
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()

            # IMPORTANT: Use response.text instead of response.content.decode()
            # response.text automatically handles GZIP/deflate/brotli decompression AND decoding
            # response.content gives you raw compressed bytes which causes binary garbage
            self.html = response.text

            # Remove any NULL bytes that can't be stored in PostgreSQL
            self.html = self.html.replace('\x00', '')

            self.soup = BeautifulSoup(self.html, 'html.parser')
            logger.info(f"Successfully fetched and decoded website: {self.url} ({len(self.html)} bytes)")
            return True

        except Exception as e:
            logger.warning(f"Failed to fetch {self.url}: {str(e)}")

            # Try HTTPS if HTTP failed
            if self.url.startswith('http://'):
                https_url = self.url.replace('http://', 'https://', 1)
                try:
                    logger.info(f"Retrying with HTTPS: {https_url}")
                    response = requests.get(https_url, headers=headers, timeout=15)
                    response.raise_for_status()

                    self.url = https_url  # Update URL to HTTPS

                    # Use response.text (auto-decompresses and decodes)
                    self.html = response.text

                    # Remove any NULL bytes
                    self.html = self.html.replace('\x00', '')

                    self.soup = BeautifulSoup(self.html, 'html.parser')
                    logger.info(f"Successfully fetched and decoded website with HTTPS: {https_url} ({len(self.html)} bytes)")
                    return True
                except Exception as e2:
                    logger.error(f"HTTPS fallback also failed: {str(e2)}")

            logger.error(f"Failed to fetch website {self.url}")
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

    def validate_image_url(self, url: str) -> bool:
        """
        Validate if an image URL is accessible and returns an image.

        Args:
            url: Image URL to validate

        Returns:
            True if image is accessible, False otherwise
        """
        try:
            # Skip data URIs (they're always valid)
            if url.startswith('data:image'):
                return True

            # Quick HEAD request to check if image exists
            response = requests.head(
                url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5,
                allow_redirects=True
            )

            # Check if successful (200-299) or permanent redirect (301)
            if response.status_code in range(200, 400):
                # Check if content-type is an image
                content_type = response.headers.get('Content-Type', '').lower()
                if 'image' in content_type or not content_type:
                    # If no content-type or is an image, it's valid
                    return True

            logger.warning(f"Image validation failed: {url} (status: {response.status_code})")
            return False

        except Exception as e:
            logger.warning(f"Image validation error for {url}: {str(e)}")
            return False

    def extract_images(self) -> List[str]:
        """Extract all meaningful images (excluding icons and tiny images) with URL validation"""
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

                # Skip invalid URLs (data URIs without proper format, javascript:, etc.)
                if not img_url.startswith(('http://', 'https://', 'data:image')):
                    logger.warning(f"Skipping invalid URL: {img_url}")
                    continue

                # VALIDATE IMAGE URL BEFORE ADDING
                if not self.validate_image_url(img_url):
                    logger.warning(f"Skipping inaccessible image: {img_url}")
                    continue

                # Get alt text for context
                alt_text = img.get('alt', '')

                images.append({
                    'url': img_url,
                    'alt': alt_text[:200]
                })

            logger.info(f"Extracted and validated {len(images)} working images")

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

    def extract_fonts(self) -> Dict[str, List[str]]:
        """Extract font families used on the website"""
        fonts = {
            'primary': [],
            'headings': [],
            'body': []
        }

        try:
            # Font pattern matching
            font_pattern = r'font-family:\s*([^;]+)'

            # Check style tags
            style_tags = self.soup.find_all('style')
            for style in style_tags:
                found_fonts = re.findall(font_pattern, style.get_text(), re.IGNORECASE)
                for font in found_fonts:
                    # Clean font names
                    font_list = [f.strip().strip('"').strip("'") for f in font.split(',')]
                    fonts['primary'].extend(font_list)

            # Check inline styles
            elements_with_style = self.soup.find_all(style=True)
            for elem in elements_with_style[:50]:
                found_fonts = re.findall(font_pattern, elem['style'], re.IGNORECASE)
                for font in found_fonts:
                    font_list = [f.strip().strip('"').strip("'") for f in font.split(',')]
                    if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        fonts['headings'].extend(font_list)
                    elif elem.name in ['p', 'span', 'div']:
                        fonts['body'].extend(font_list)

            # Remove duplicates and generic fonts
            generic_fonts = ['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui']
            for key in fonts:
                fonts[key] = [f for f in list(set(fonts[key])) if f.lower() not in generic_fonts][:3]

            logger.info(f"Extracted fonts - Primary: {fonts['primary'][:3]}")

            return fonts

        except Exception as e:
            logger.error(f"Error extracting fonts: {str(e)}")

        return fonts

    def extract_videos(self) -> List[Dict[str, str]]:
        """Extract video URLs from the website"""
        videos = []

        try:
            # Check video tags
            video_tags = self.soup.find_all('video')
            for video in video_tags[:5]:  # Limit to 5 videos
                sources = video.find_all('source')
                for source in sources:
                    src = source.get('src')
                    if src:
                        video_url = urljoin(self.url, src)
                        videos.append({
                            'url': video_url,
                            'type': source.get('type', 'video/mp4'),
                            'poster': video.get('poster', '')
                        })
                        break  # Just first source per video

            # Check for YouTube embeds
            youtube_pattern = r'(?:youtube\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]+)'
            iframes = self.soup.find_all('iframe', src=True)
            for iframe in iframes:
                src = iframe['src']
                match = re.search(youtube_pattern, src)
                if match:
                    videos.append({
                        'url': f"https://www.youtube.com/embed/{match.group(1)}",
                        'type': 'youtube',
                        'video_id': match.group(1)
                    })

            # Check for Vimeo embeds
            vimeo_pattern = r'player\.vimeo\.com/video/(\d+)'
            for iframe in iframes:
                src = iframe['src']
                match = re.search(vimeo_pattern, src)
                if match:
                    videos.append({
                        'url': f"https://player.vimeo.com/video/{match.group(1)}",
                        'type': 'vimeo',
                        'video_id': match.group(1)
                    })

            logger.info(f"Extracted {len(videos)} videos")

        except Exception as e:
            logger.error(f"Error extracting videos: {str(e)}")

        return videos

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
                    logger.info(f"[CSS] Fetched {len(response.text)} chars from {css_url}")
                except Exception as e:
                    logger.warning(f"Failed to fetch CSS {css_url}: {e}")

        except Exception as e:
            logger.error(f"Error fetching external CSS: {e}")

        return combined_css

    def extract_page_structure(self) -> List[Dict[str, Any]]:
        """
        Extract the ACTUAL page structure - REAL content sections only (no cookies/nav/footer).
        This allows us to recreate THEIR layout with meaningful content.

        Returns list of REAL content sections in order
        """
        sections = []

        # NOISE KEYWORDS - sections to SKIP (cookies, navigation, footers, etc.)
        noise_keywords = [
            'cookie', 'consent', 'gdpr', 'privacy-policy', 'policy',
            'navigation', 'navbar', 'nav-menu', 'site-nav',
            'language-selector', 'location-selector', 'country-select',
            'sign-in', 'login-form', 'account-menu',
            'shopping-cart', 'cart', 'basket',
            'sidebar', 'widget', 'ad-banner', 'advertisement',
            'popup', 'modal', 'overlay', 'lightbox',
            'site-footer', 'page-footer', 'footer-nav'
        ]

        # Find main content area (skip headers, footers, navs)
        main_content = (
            self.soup.find('main') or
            self.soup.find(id=re.compile(r'main|content', re.I)) or
            self.soup.find(class_=re.compile(r'main|content|page-content', re.I)) or
            self.soup.find('body')
        )

        if not main_content:
            return []

        # Find all major sections - be more flexible with class names
        # First try semantic HTML5 sections and articles
        section_elements = main_content.find_all(['section', 'article'], recursive=True)

        # If no sections found, search for ALL divs recursively
        if len(section_elements) < 3:
            # Search for all divs (the filtering later will remove noise)
            all_divs = main_content.find_all('div', recursive=True)
            section_elements.extend(all_divs[:50])  # Take first 50 divs to analyze

        # Filter out noise sections
        filtered_sections = []
        for element in section_elements[:25]:  # Check first 25
            section_id = element.get('id', '').lower()
            section_class = ' '.join(element.get('class', [])).lower()
            combined = f"{section_id} {section_class}"

            # SKIP if this matches noise keywords
            if any(noise in combined for noise in noise_keywords):
                continue

            # Get text content
            section_text = element.get_text(strip=True, separator=' ')

            # SKIP if section is too small (< 20 chars) - allow minimal hero sections
            if len(section_text) < 20:
                continue

            # SKIP if it's mostly links (navigation)
            links = element.find_all('a')
            link_text_length = sum(len(a.get_text(strip=True)) for a in links)
            total_text_length = len(section_text)
            if links and len(links) > 10 and total_text_length < 500:
                continue  # Too many links, not enough text = navigation
            if total_text_length > 0 and (link_text_length / total_text_length) > 0.8:
                continue  # More than 80% is links = navigation

            filtered_sections.append(element)

        # Process filtered sections
        for idx, element in enumerate(filtered_sections[:12]):  # Keep top 12 real sections
            section_id = element.get('id', '')
            section_class = ' '.join(element.get('class', []))

            # Extract LONGER content (2000 chars instead of 500 for GPT-4 analysis)
            section_text = element.get_text(strip=True, separator=' ')

            # Find heading
            heading = element.find(['h1', 'h2', 'h3', 'h4'])
            heading_text = heading.get_text(strip=True) if heading else ""

            # Identify section type
            combined_text = f"{section_id} {section_class} {heading_text} {section_text[:300]}".lower()

            section_type = "content"  # Default

            # First section is usually hero
            if idx == 0:
                section_type = "hero"
            elif any(word in combined_text for word in ['hero', 'banner', 'jumbotron', 'intro', 'welcome']):
                section_type = "hero"
            elif any(word in combined_text for word in ['about', 'who we are', 'our story', 'company', 'mission', 'vision']):
                section_type = "about"
            elif any(word in combined_text for word in ['service', 'what we do', 'offering', 'solutions', 'menu', 'food', 'dishes', 'products']):
                section_type = "services"
            elif any(word in combined_text for word in ['portfolio', 'work', 'projects', 'gallery', 'showcase', 'examples']):
                section_type = "portfolio"
            elif any(word in combined_text for word in ['testimonial', 'review', 'client', 'feedback', 'rating', 'say']):
                section_type = "testimonials"
            elif any(word in combined_text for word in ['team', 'staff', 'people', 'meet', 'experts']):
                section_type = "team"
            elif any(word in combined_text for word in ['contact', 'get in touch', 'reach us', 'find us', 'location', 'hours', 'call', 'email']):
                section_type = "contact"
            elif any(word in combined_text for word in ['pricing', 'plans', 'packages', 'price', 'cost']):
                section_type = "pricing"
            elif any(word in combined_text for word in ['faq', 'questions', 'q&a', 'frequently', 'asked']):
                section_type = "faq"
            elif any(word in combined_text for word in ['feature', 'why', 'benefit', 'advantage']):
                section_type = "features"
            elif any(word in combined_text for word in ['offer', 'deal', 'promotion', 'special', 'discount']):
                section_type = "offers"

            sections.append({
                'order': idx,
                'type': section_type,
                'heading': heading_text,
                'content': section_text[:1500],  # Save 1500 chars per section for GPT-4
                'id': section_id,
                'classes': section_class
            })

        logger.info(f"[PAGE STRUCTURE] Detected {len(sections)} REAL content sections (filtered out {len(filtered_sections) - len(sections)} utility sections):")
        for s in sections[:5]:  # Log first 5
            preview = s['heading'][:40] if s['heading'] else s['content'][:40]
            logger.info(f"   {s['order']}. {s['type'].upper()}: {preview}...")

        return sections

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
        # IMPORTANT: Only add CSS if it's valid and doesn't break HTML structure
        if external_css and len(external_css) > 0:
            # Clean external CSS - remove any NULL bytes or problematic characters
            external_css_clean = external_css.replace('\x00', '').strip()
            raw_html_with_css = self.html + f"\n<style>\n{external_css_clean}\n</style>"
        else:
            raw_html_with_css = self.html

        logger.info(f"[HTML] Combined HTML size: {len(raw_html_with_css)} bytes (original: {len(self.html)}, CSS: {len(external_css)})")

        # Extract page structure FIRST
        page_structure = self.extract_page_structure()

        # Extract MAIN CONTENT text only (not navigation/cookies/footer)
        main_content = (
            self.soup.find('main') or
            self.soup.find(id=re.compile(r'main|content', re.I)) or
            self.soup.find(class_=re.compile(r'main|content|page-content', re.I)) or
            self.soup.find('body')
        )
        main_text = main_content.get_text(strip=True, separator=' ')[:10000] if main_content else self.soup.get_text()[:5000]

        # Extract all content
        scraped_data = {
            'url': self.url,
            'domain': self.domain,
            'logo': self.extract_logo(),
            'headlines': self.extract_headlines(),
            'about': self.extract_about_content(),
            'services_menu': self.extract_services_or_menu(),
            'images': self.extract_images(),
            'videos': self.extract_videos(),  # NEW: Extract videos
            'contact': self.extract_contact_info(),
            'social_media': self.extract_social_media(),
            'colors': self.extract_colors(),
            'fonts': self.extract_fonts(),  # NEW: Extract fonts
            'certifications': self.extract_certifications_awards(),
            'navigation': self.extract_navigation(),
            'testimonials': self.extract_testimonials(),
            'page_structure': page_structure,  # Actual page sections (FILTERED)
            'raw_html': raw_html_with_css,  # Include HTML + external CSS
            'text_content': main_text  # MAIN CONTENT text only (up to 10000 chars)
        }

        # CRITICAL: Validate scraped HTML before returning
        # UPDATED: Validate the ORIGINAL HTML, not raw_html_with_css (which has appended CSS)
        # The CSS might contain data URIs or other content that triggers false positives
        # DEBUG: Log HTML preview before validation
        html_preview = self.html[:200] if self.html else "EMPTY"
        logger.info(f"[DEBUG] HTML preview (first 200 chars): {html_preview}")
        logger.info(f"[DEBUG] HTML has <!doctype: {('<!doctype' in self.html.lower())}")
        logger.info(f"[DEBUG] HTML has <html: {('<html' in self.html.lower())}")
        logger.info(f"[DEBUG] HTML has <body: {('<body' in self.html.lower())}")

        if not validate_scraped_html(self.html, self.url):
            logger.error(f"[VALIDATION FAILED] Scraped HTML is corrupted or invalid for {self.url}")
            logger.error(f"[SAFETY] Returning empty dict to prevent corrupted data from being saved")
            return {}

        logger.info(f"Scraping complete! Extracted data from {len(scraped_data)} categories")
        logger.info(f"[CSS] Included {len(external_css)} chars of external CSS")
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
