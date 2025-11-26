"""
Asset Extractor Service
Extracts and normalizes specific assets from scraped HTML for enhanced template modernization.
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import Counter

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class AssetExtractorService:
    """
    Service for extracting and normalizing specific assets from scraped HTML.

    Extracts:
    - Images (all img src URLs)
    - Logos (subset of images with logo indicators)
    - Videos (video tags + iframe embeds for YouTube/Vimeo)
    - Maps (Google Maps, other map iframe embeds)
    - Colors (hex codes from CSS and inline styles)
    - Component structure (major HTML sections)
    """

    def __init__(self, base_url: str, html: str, css: str = ""):
        """
        Initialize extractor with HTML and CSS content.

        Args:
            base_url: Base URL for resolving relative URLs
            html: HTML content to parse
            css: CSS content (inline + external)
        """
        self.base_url = base_url
        self.html = html
        self.css = css
        self.soup = BeautifulSoup(html, 'html.parser')

    def extract_images(self) -> List[str]:
        """
        Extract ALL image URLs from HTML.

        Returns:
            List of absolute image URLs
        """
        image_urls = []

        try:
            img_tags = self.soup.find_all('img')
            for img in img_tags:
                # Try src, data-src, srcset
                src = img.get('src') or img.get('data-src')
                if not src:
                    srcset = img.get('srcset')
                    if srcset:
                        # Extract first URL from srcset
                        src = srcset.split(',')[0].split()[0]

                if src:
                    # Convert to absolute URL
                    absolute_url = urljoin(self.base_url, src)
                    image_urls.append(absolute_url)

            # Remove duplicates while preserving order
            image_urls = list(dict.fromkeys(image_urls))

            logger.info(f"[AssetExtractor] Extracted {len(image_urls)} image URLs")

        except Exception as e:
            logger.error(f"[AssetExtractor] Error extracting images: {str(e)}")

        return image_urls

    def extract_logos(self, image_urls: List[str]) -> List[str]:
        """
        Extract logo URLs from all images (subset of image_urls).

        Logos are identified by:
        - Filename contains 'logo'
        - Alt text contains 'logo'
        - Class/ID contains 'logo'
        - First image in header/nav

        Args:
            image_urls: List of all image URLs (from extract_images)

        Returns:
            List of logo URLs (subset of image_urls)
        """
        logo_urls = []

        try:
            # Logo selectors
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                'img[id*="logo" i]',
                '.logo img',
                '#logo img',
                'header img:first-of-type',
                '.navbar-brand img',
                '.site-logo img',
                '.brand img'
            ]

            for selector in logo_selectors:
                logos = self.soup.select(selector)
                for logo in logos:
                    src = logo.get('src') or logo.get('data-src')
                    if src:
                        absolute_url = urljoin(self.base_url, src)
                        if absolute_url in image_urls:  # Must be in image_urls
                            logo_urls.append(absolute_url)

            # Remove duplicates
            logo_urls = list(dict.fromkeys(logo_urls))

            logger.info(f"[AssetExtractor] Identified {len(logo_urls)} logo URLs from {len(image_urls)} images")

        except Exception as e:
            logger.error(f"[AssetExtractor] Error extracting logos: {str(e)}")

        return logo_urls

    def extract_videos(self) -> List[str]:
        """
        Extract video URLs and iframe embeds.

        Extracts:
        - <video> tags with <source> elements
        - YouTube iframe embeds
        - Vimeo iframe embeds
        - Other video iframes

        Returns:
            List of video URLs/embed codes
        """
        video_urls = []

        try:
            # Extract <video> tags
            video_tags = self.soup.find_all('video')
            for video in video_tags:
                sources = video.find_all('source')
                for source in sources:
                    src = source.get('src')
                    if src:
                        absolute_url = urljoin(self.base_url, src)
                        video_urls.append(absolute_url)
                        break  # First source per video

            # Extract YouTube embeds
            youtube_pattern = r'(?:youtube\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]+)'
            iframes = self.soup.find_all('iframe', src=True)
            for iframe in iframes:
                src = iframe['src']
                match = re.search(youtube_pattern, src)
                if match:
                    video_id = match.group(1)
                    video_urls.append(f"https://www.youtube.com/embed/{video_id}")

            # Extract Vimeo embeds
            vimeo_pattern = r'player\.vimeo\.com/video/(\d+)'
            for iframe in iframes:
                src = iframe['src']
                match = re.search(vimeo_pattern, src)
                if match:
                    video_id = match.group(1)
                    video_urls.append(f"https://player.vimeo.com/video/{video_id}")

            # Remove duplicates
            video_urls = list(dict.fromkeys(video_urls))

            logger.info(f"[AssetExtractor] Extracted {len(video_urls)} video URLs/embeds")

        except Exception as e:
            logger.error(f"[AssetExtractor] Error extracting videos: {str(e)}")

        return video_urls

    def extract_maps(self) -> List[str]:
        """
        Extract map iframe embeds (Google Maps, other map providers).

        Returns:
            List of map iframe src URLs
        """
        map_embeds = []

        try:
            # Map provider patterns
            map_patterns = [
                r'google\.com/maps',
                r'maps\.google',
                r'openstreetmap\.org',
                r'mapbox\.com',
                r'bing\.com/maps'
            ]

            iframes = self.soup.find_all('iframe', src=True)
            for iframe in iframes:
                src = iframe['src']
                if any(re.search(pattern, src, re.I) for pattern in map_patterns):
                    map_embeds.append(src)

            logger.info(f"[AssetExtractor] Extracted {len(map_embeds)} map embeds")

        except Exception as e:
            logger.error(f"[AssetExtractor] Error extracting maps: {str(e)}")

        return map_embeds

    def extract_colors(self) -> List[str]:
        """
        Extract hex color codes from CSS and inline styles.

        Returns dominant colors (excluding pure white/black/common grays).

        Returns:
            List of hex color codes (e.g., ['#FF6B6B', '#4ECDC4'])
        """
        colors = []

        try:
            # Hex color pattern (3 or 6 digits)
            color_pattern = r'#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}'

            # Extract from CSS content
            if self.css:
                found_colors = re.findall(color_pattern, self.css)
                colors.extend(found_colors)

            # Extract from <style> tags in HTML
            style_tags = self.soup.find_all('style')
            for style in style_tags:
                found_colors = re.findall(color_pattern, style.get_text())
                colors.extend(found_colors)

            # Extract from inline styles
            elements_with_style = self.soup.find_all(style=True)
            for elem in elements_with_style:
                found_colors = re.findall(color_pattern, elem['style'])
                colors.extend(found_colors)

            # Normalize 3-digit hex to 6-digit
            normalized_colors = []
            for color in colors:
                if len(color) == 4:  # #RGB
                    # Convert #RGB to #RRGGBB
                    r, g, b = color[1], color[2], color[3]
                    normalized = f"#{r}{r}{g}{g}{b}{b}".upper()
                    normalized_colors.append(normalized)
                else:
                    normalized_colors.append(color.upper())

            # Filter out common colors (white, black, grays)
            excluded_colors = {
                '#FFFFFF', '#FFF',
                '#000000', '#000',
                '#F0F0F0', '#E0E0E0', '#CCCCCC', '#CCC',
                '#EEEEEE', '#EEE', '#DDDDDD', '#DDD'
            }

            # Count color frequency
            color_counter = Counter(normalized_colors)

            # Get top 10 most common colors (excluding common ones)
            dominant_colors = []
            for color, count in color_counter.most_common(20):
                if color not in excluded_colors and color not in dominant_colors:
                    dominant_colors.append(color)
                if len(dominant_colors) >= 10:
                    break

            logger.info(f"[AssetExtractor] Extracted {len(dominant_colors)} dominant colors from {len(colors)} total")

            return dominant_colors

        except Exception as e:
            logger.error(f"[AssetExtractor] Error extracting colors: {str(e)}")
            return []

    def count_components(self) -> int:
        """
        Count ALL major HTML sections/components aggressively.

        Counts:
        - Header, nav, hero sections
        - All semantic sections (<section>, <article>)
        - All major div containers with substantial content
        - Footer

        Returns:
            Number of major components/sections
        """
        try:
            components = []

            # Always count header if exists
            header = self.soup.find('header')
            if header:
                components.append(header)

            # Always count nav if exists
            nav = self.soup.find('nav')
            if nav and nav not in components:
                components.append(nav)

            # Find main content area (body by default)
            body = self.soup.find('body')
            if not body:
                return len(components)

            # Count ALL semantic sections and articles
            semantic_sections = body.find_all(['section', 'article', 'aside'], recursive=True)
            components.extend(semantic_sections)

            # Count ALL major divs (top-level divs in body or main containers)
            # This catches old-style websites that don't use semantic HTML
            major_containers = body.find_all('div', recursive=False)
            for div in major_containers:
                # Include div if it has substantial text content (>50 chars)
                text_content = div.get_text(strip=True)
                if len(text_content) > 50:
                    # Check it's not already counted (e.g., inside a section)
                    if div not in components:
                        components.append(div)

            # Also count divs with common section class names
            section_patterns = [
                r'hero', r'banner', r'services', r'about', r'features',
                r'testimonial', r'portfolio', r'contact', r'cta', r'call.to.action',
                r'team', r'pricing', r'faq', r'gallery', r'clients', r'partners'
            ]
            for pattern in section_patterns:
                matching_divs = body.find_all('div', class_=re.compile(pattern, re.I))
                for div in matching_divs:
                    if div not in components and len(div.get_text(strip=True)) > 50:
                        components.append(div)

            # Count footer
            footer = self.soup.find('footer')
            if footer and footer not in components:
                components.append(footer)

            # Remove duplicates while preserving order
            unique_components = []
            seen = set()
            for comp in components:
                comp_id = id(comp)
                if comp_id not in seen:
                    seen.add(comp_id)
                    unique_components.append(comp)

            component_count = len(unique_components)
            logger.info(f"[AssetExtractor] Counted {component_count} components/sections (aggressive detection)")

            return component_count

        except Exception as e:
            logger.error(f"[AssetExtractor] Error counting components: {str(e)}")
            return 0

    def analyze_component_structure(self) -> List[Dict[str, str]]:
        """
        Analyze and describe the structure of ALL major HTML components aggressively.

        Returns:
            List of component descriptors with type, heading, and order
        """
        components = []

        try:
            all_components = []
            body = self.soup.find('body')
            if not body:
                return []

            # Collect same components as count_components() method
            # Header
            header = self.soup.find('header')
            if header:
                all_components.append(header)

            # Nav
            nav = self.soup.find('nav')
            if nav and nav not in all_components:
                all_components.append(nav)

            # Semantic sections
            semantic_sections = body.find_all(['section', 'article', 'aside'], recursive=True)
            all_components.extend(semantic_sections)

            # Major divs
            major_containers = body.find_all('div', recursive=False)
            for div in major_containers:
                text_content = div.get_text(strip=True)
                if len(text_content) > 50 and div not in all_components:
                    all_components.append(div)

            # Divs with section-like class names
            section_patterns = [
                r'hero', r'banner', r'services', r'about', r'features',
                r'testimonial', r'portfolio', r'contact', r'cta', r'call.to.action',
                r'team', r'pricing', r'faq', r'gallery', r'clients', r'partners'
            ]
            for pattern in section_patterns:
                matching_divs = body.find_all('div', class_=re.compile(pattern, re.I))
                for div in matching_divs:
                    if div not in all_components and len(div.get_text(strip=True)) > 50:
                        all_components.append(div)

            # Footer
            footer = self.soup.find('footer')
            if footer and footer not in all_components:
                all_components.append(footer)

            # Remove duplicates
            unique_components = []
            seen = set()
            for comp in all_components:
                comp_id = id(comp)
                if comp_id not in seen:
                    seen.add(comp_id)
                    unique_components.append(comp)

            # Analyze each component (NO LIMIT - include all components)
            for idx, element in enumerate(unique_components):
                section_id = element.get('id', '')
                section_class = ' '.join(element.get('class', []))

                # Find heading
                heading = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                heading_text = heading.get_text(strip=True) if heading else ""

                # Extract actual text content from this component
                # Get all text but limit to first 500 chars to keep database size reasonable
                content_text = element.get_text(separator=' ', strip=True)
                content_text = ' '.join(content_text.split())  # Normalize whitespace
                content_preview = content_text[:500] if content_text else ""

                # Determine component type
                combined = f"{section_id} {section_class} {heading_text}".lower()

                component_type = "content"  # Default
                if idx == 0 or any(word in combined for word in ['hero', 'banner', 'jumbotron']):
                    component_type = "hero"
                elif any(word in combined for word in ['about', 'story', 'mission']):
                    component_type = "about"
                elif any(word in combined for word in ['service', 'offering', 'product']):
                    component_type = "services"
                elif any(word in combined for word in ['portfolio', 'work', 'project']):
                    component_type = "portfolio"
                elif any(word in combined for word in ['testimonial', 'review', 'feedback']):
                    component_type = "testimonials"
                elif any(word in combined for word in ['team', 'staff', 'people']):
                    component_type = "team"
                elif any(word in combined for word in ['contact', 'get in touch']):
                    component_type = "contact"
                elif any(word in combined for word in ['pricing', 'plans', 'packages']):
                    component_type = "pricing"

                components.append({
                    'order': idx,
                    'type': component_type,
                    'heading': heading_text[:100],
                    'content': content_preview,  # NEW: Include actual content text!
                    'id': section_id,
                    'classes': section_class
                })

            logger.info(f"[AssetExtractor] Analyzed {len(components)} component structures")

        except Exception as e:
            logger.error(f"[AssetExtractor] Error analyzing component structure: {str(e)}")

        return components

    def extract_all_assets(self) -> Dict[str, any]:
        """
        Extract all assets in one call.

        Returns:
            Dictionary with all extracted assets
        """
        logger.info("[AssetExtractor] Starting full asset extraction")

        image_urls = self.extract_images()
        logo_urls = self.extract_logos(image_urls)
        video_urls = self.extract_videos()
        map_embeds = self.extract_maps()
        color_palette = self.extract_colors()
        component_count = self.count_components()
        component_structure = self.analyze_component_structure()

        assets = {
            'image_urls': image_urls,
            'logo_urls': logo_urls,
            'video_urls': video_urls,
            'map_embeds': map_embeds,
            'color_palette': color_palette,
            'component_count': component_count,
            'component_structure': component_structure
        }

        logger.info(f"[AssetExtractor] Extraction complete: "
                   f"{len(image_urls)} images, {len(logo_urls)} logos, "
                   f"{len(video_urls)} videos, {len(map_embeds)} maps, "
                   f"{len(color_palette)} colors, {component_count} components")

        return assets
