"""
Template Validation Service
Ensures generated templates include ALL scraped components, images, and videos
"""

import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from app.models.business import Business
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class TemplateValidationResult:
    """Result of template validation"""

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.stats = {}
        self.missing_components = []
        self.missing_images = []
        self.missing_videos = []

    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
        logger.error(f"[VALIDATION ERROR] {message}")

    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
        logger.warning(f"[VALIDATION WARNING] {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
            "missing_components": self.missing_components,
            "missing_images": self.missing_images,
            "missing_videos": self.missing_videos
        }


class TemplateValidator:
    """
    Validates generated templates against scraped business data.

    Ensures:
    1. ALL components/sections from original are present
    2. ALL images from scraped data are embedded
    3. ALL videos from scraped data are embedded
    4. Brand colors are preserved
    5. HTML is valid and complete
    """

    def __init__(self, business: Business):
        """
        Initialize validator with business data.

        Args:
            business: Business model with scraped data
        """
        self.business = business

        # Extract expected data from business
        self.expected_components = business.component_structure or []
        self.expected_images = business.image_urls or []
        self.expected_videos = business.video_urls or []
        self.expected_logos = business.logo_urls or []
        self.expected_colors = business.color_palette or []

        logger.info(f"[VALIDATOR] Initialized for {business.name}")
        logger.info(f"[VALIDATOR] Expected: {len(self.expected_components)} components, "
                   f"{len(self.expected_images)} images, {len(self.expected_videos)} videos, "
                   f"{len(self.expected_logos)} logos")

    def validate_template(self, html_content: str) -> TemplateValidationResult:
        """
        Validate generated HTML template.

        Args:
            html_content: Generated HTML string

        Returns:
            TemplateValidationResult with validation details
        """
        result = TemplateValidationResult()

        logger.info(f"[VALIDATOR] Starting validation for {self.business.name}")
        logger.info(f"[VALIDATOR] HTML size: {len(html_content)} characters")

        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            result.add_error(f"Failed to parse HTML: {str(e)}")
            return result

        # 1. Validate HTML structure
        self._validate_html_structure(soup, result)

        # 2. Validate component count
        self._validate_components(soup, result)

        # 3. Validate images
        self._validate_images(soup, result)

        # 4. Validate videos
        self._validate_videos(soup, result)

        # 5. Validate logos
        self._validate_logos(soup, result)

        # 6. Validate brand colors
        self._validate_colors(html_content, result)

        # 7. Overall statistics
        result.stats = {
            "html_size": len(html_content),
            "expected_components": len(self.expected_components),
            "found_sections": len(soup.find_all(['section', 'div', 'article'])),
            "expected_images": len(self.expected_images),
            "found_images": len(soup.find_all('img')),
            "expected_videos": len(self.expected_videos),
            "found_videos": len(soup.find_all(['video', 'iframe'])),
            "expected_logos": len(self.expected_logos),
            "found_logos": self._count_logos(soup),
            "expected_colors": len(self.expected_colors),
            "found_colors": self._count_color_usage(html_content)
        }

        # Log summary
        if result.is_valid:
            logger.info(f"[VALIDATOR] ✅ VALIDATION PASSED for {self.business.name}")
        else:
            logger.error(f"[VALIDATOR] ❌ VALIDATION FAILED for {self.business.name}")
            logger.error(f"[VALIDATOR] Errors: {len(result.errors)}")
            for error in result.errors:
                logger.error(f"[VALIDATOR]   - {error}")

        if result.warnings:
            logger.warning(f"[VALIDATOR] ⚠️ Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                logger.warning(f"[VALIDATOR]   - {warning}")

        return result

    def _validate_html_structure(self, soup: BeautifulSoup, result: TemplateValidationResult):
        """Validate basic HTML structure"""

        # Check for required tags
        if not soup.find('html'):
            result.add_error("Missing <html> tag")

        if not soup.find('head'):
            result.add_error("Missing <head> tag")

        if not soup.find('body'):
            result.add_error("Missing <body> tag")

        # Check for viewport meta tag (mobile responsiveness)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            result.add_warning("Missing viewport meta tag - may not be mobile responsive")

        # Check for title
        title = soup.find('title')
        if not title or not title.string:
            result.add_warning("Missing or empty <title> tag")

    def _validate_components(self, soup: BeautifulSoup, result: TemplateValidationResult):
        """Validate all components are present"""

        expected_count = len(self.expected_components)

        # Count sections/major divs
        sections = soup.find_all(['section', 'article', 'div'])
        # Filter to only major structural elements (exclude nested divs)
        major_sections = [s for s in sections if s.name in ['section', 'article']]

        found_count = len(major_sections)

        logger.info(f"[VALIDATOR] Components: Expected {expected_count}, Found {found_count} major sections")

        if found_count < expected_count:
            missing = expected_count - found_count
            result.add_error(
                f"MISSING COMPONENTS: Expected {expected_count} components but found only {found_count}. "
                f"Missing {missing} sections!"
            )
            result.missing_components = [
                comp.get('heading', comp.get('type', 'Unknown'))
                for comp in self.expected_components[found_count:]
            ]
        elif found_count < expected_count * 0.8:  # Less than 80% of components
            result.add_warning(
                f"Component count lower than expected: {found_count} vs {expected_count}"
            )

    def _validate_images(self, soup: BeautifulSoup, result: TemplateValidationResult):
        """Validate all images are embedded"""

        img_tags = soup.find_all('img')
        found_image_urls = [img.get('src', '') for img in img_tags if img.get('src')]

        expected_count = len(self.expected_images)
        found_count = len(found_image_urls)

        logger.info(f"[VALIDATOR] Images: Expected {expected_count}, Found {found_count}")

        # Count how many expected images appear in generated HTML
        matched_images = 0
        missing_images = []

        for expected_url in self.expected_images:
            # Normalize URLs for comparison (remove query params, fragments)
            expected_clean = expected_url.split('?')[0].split('#')[0]

            found = False
            for found_url in found_image_urls:
                found_clean = found_url.split('?')[0].split('#')[0]
                if expected_clean in found_url or found_clean.endswith(found_clean.split('/')[-1]):
                    found = True
                    matched_images += 1
                    break

            if not found:
                missing_images.append(expected_url)

        logger.info(f"[VALIDATOR] Matched {matched_images} out of {expected_count} expected images")

        # Strict validation: ALL images must be present
        if matched_images < expected_count:
            missing_count = expected_count - matched_images
            result.add_error(
                f"MISSING IMAGES: Expected {expected_count} images but only {matched_images} are embedded. "
                f"Missing {missing_count} images!"
            )
            result.missing_images = missing_images[:10]  # First 10 missing

        # Warning if image count is suspiciously low
        if found_count < 3:
            result.add_warning(f"Very few images in output ({found_count}). Expected {expected_count}.")

    def _validate_videos(self, soup: BeautifulSoup, result: TemplateValidationResult):
        """Validate all videos are embedded"""

        # Find video elements (both <video> and <iframe> for embeds)
        video_tags = soup.find_all('video')
        iframe_tags = soup.find_all('iframe')

        found_video_urls = []
        for video in video_tags:
            src = video.get('src', '')
            if src:
                found_video_urls.append(src)

        for iframe in iframe_tags:
            src = iframe.get('src', '')
            # Check if it's a video embed (YouTube, Vimeo, etc.)
            if src and any(platform in src.lower() for platform in ['youtube', 'vimeo', 'wistia', 'dailymotion']):
                found_video_urls.append(src)

        expected_count = len(self.expected_videos)
        found_count = len(found_video_urls)

        logger.info(f"[VALIDATOR] Videos: Expected {expected_count}, Found {found_count}")

        if expected_count > 0:
            # Count matched videos
            matched_videos = 0
            missing_videos = []

            for expected_url in self.expected_videos:
                found = False
                for found_url in found_video_urls:
                    if expected_url in found_url or self._is_same_video(expected_url, found_url):
                        found = True
                        matched_videos += 1
                        break

                if not found:
                    missing_videos.append(expected_url)

            logger.info(f"[VALIDATOR] Matched {matched_videos} out of {expected_count} expected videos")

            if matched_videos < expected_count:
                missing_count = expected_count - matched_videos
                result.add_error(
                    f"MISSING VIDEOS: Expected {expected_count} videos but only {matched_videos} are embedded. "
                    f"Missing {missing_count} videos!"
                )
                result.missing_videos = missing_videos

    def _validate_logos(self, soup: BeautifulSoup, result: TemplateValidationResult):
        """Validate logos are present"""

        expected_count = len(self.expected_logos)

        if expected_count == 0:
            return  # No logos expected

        # Count logo images (typically in header/nav)
        logo_count = self._count_logos(soup)

        logger.info(f"[VALIDATOR] Logos: Expected {expected_count}, Found {logo_count}")

        if logo_count == 0:
            result.add_error("MISSING LOGO: No logo found in header/navigation")
        elif logo_count < expected_count:
            result.add_warning(f"Logo count lower than expected: {logo_count} vs {expected_count}")

    def _validate_colors(self, html_content: str, result: TemplateValidationResult):
        """Validate brand colors are used"""

        if not self.expected_colors:
            return  # No colors to validate

        color_usage_count = self._count_color_usage(html_content)

        logger.info(f"[VALIDATOR] Brand Colors: Expected {len(self.expected_colors)}, "
                   f"Found {color_usage_count} color references")

        if color_usage_count == 0:
            result.add_warning("Brand colors not found in HTML - may be using different colors")

    def _count_logos(self, soup: BeautifulSoup) -> int:
        """Count logo images in header/nav"""
        count = 0

        # Check header/nav for logos
        header = soup.find('header')
        nav = soup.find('nav')

        for container in [header, nav]:
            if container:
                # Look for images with 'logo' in class/id/alt
                logo_imgs = container.find_all('img', class_=lambda x: x and 'logo' in x.lower())
                count += len(logo_imgs)

                logo_imgs = container.find_all('img', id=lambda x: x and 'logo' in x.lower())
                count += len(logo_imgs)

                logo_imgs = container.find_all('img', alt=lambda x: x and 'logo' in x.lower())
                count += len(logo_imgs)

        # Also check for any img in header/nav (even without logo class)
        if count == 0:
            if header:
                count += len(header.find_all('img'))
            if nav:
                count += len(nav.find_all('img'))

        return count

    def _count_color_usage(self, html_content: str) -> int:
        """Count how many brand colors appear in HTML"""
        count = 0
        html_lower = html_content.lower()

        for color in self.expected_colors:
            # Normalize color (remove #, make lowercase)
            color_clean = color.replace('#', '').lower()

            # Count occurrences in HTML
            if color_clean in html_lower or f"#{color_clean}" in html_lower:
                count += 1

        return count

    def _is_same_video(self, url1: str, url2: str) -> bool:
        """Check if two video URLs point to same video (handle different embed formats)"""

        # Extract video ID from YouTube URLs
        if 'youtube' in url1.lower() or 'youtu.be' in url1.lower():
            id1 = self._extract_youtube_id(url1)
            id2 = self._extract_youtube_id(url2)
            if id1 and id2:
                return id1 == id2

        # Extract video ID from Vimeo URLs
        if 'vimeo' in url1.lower():
            id1 = self._extract_vimeo_id(url1)
            id2 = self._extract_vimeo_id(url2)
            if id1 and id2:
                return id1 == id2

        # Fallback: simple URL comparison
        return url1.strip('/') == url2.strip('/')

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        import re

        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\?\/]+)',
            r'youtube\.com\/embed\/([^&\?\/]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _extract_vimeo_id(self, url: str) -> Optional[str]:
        """Extract Vimeo video ID from URL"""
        import re

        match = re.search(r'vimeo\.com\/(\d+)', url)
        if match:
            return match.group(1)

        return None


def validate_template(business: Business, html_content: str) -> TemplateValidationResult:
    """
    Convenience function to validate a template.

    Args:
        business: Business model with scraped data
        html_content: Generated HTML content

    Returns:
        TemplateValidationResult
    """
    validator = TemplateValidator(business)
    return validator.validate_template(html_content)
