"""Content Extraction Module

Extracts and preserves existing business assets from old websites:
- Logo images
- Color palettes
- Text content (about, services, testimonials)
- Contact information
- Existing media assets

This ensures brand identity is preserved while upgrading design.

Based on brainstorming session: docs/brainstorming-session-results-2025-11-06.md
Priority #1 - Content Extraction & Reuse
"""

from typing import Dict, List, Optional, Tuple
import re
import logging
from urllib.parse import urljoin, urlparse
from collections import Counter

logger = logging.getLogger(__name__)


def extract_colors_from_text(html_content: str) -> List[str]:
    """
    Extract color codes from HTML/CSS content with enhanced detection.

    Args:
        html_content: Raw HTML content from website

    Returns:
        List of hex color codes found (e.g., ['#FF5733', '#3498DB'])
    """
    colors = []

    # 1. Match hex colors (#RGB or #RRGGBB) - more aggressive pattern
    hex_pattern = r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b'
    hex_matches = re.findall(hex_pattern, html_content)

    # 2. Match rgb/rgba colors
    rgb_pattern = r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[\d.]+)?\s*\)'
    rgb_matches = re.findall(rgb_pattern, html_content)

    # 3. Extract from CSS properties (background-color, color, border-color, etc.)
    css_color_pattern = r'(?:background-color|color|border-color|fill|stroke)\s*:\s*([#]?[0-9a-fA-F]{3,6}|rgba?\([^)]+\))'
    css_matches = re.findall(css_color_pattern, html_content, re.IGNORECASE)

    # 4. Extract from inline styles
    inline_style_pattern = r'style\s*=\s*["\'][^"\']*(?:background-color|color)\s*:\s*([^;"\']+)'
    inline_matches = re.findall(inline_style_pattern, html_content, re.IGNORECASE)

    # Process hex colors
    for color in hex_matches:
        # Normalize 3-digit hex to 6-digit
        if len(color) == 4:  # #RGB
            color = f"#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}"
        colors.append(color.upper())

    # Process CSS matches
    for color in css_matches:
        if color.startswith('#'):
            if len(color) == 4:  # #RGB
                color = f"#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}"
            colors.append(color.upper())
        elif color.startswith('rgb'):
            # Extract RGB values
            rgb_vals = re.findall(r'\d+', color)
            if len(rgb_vals) >= 3:
                hex_color = f"#{int(rgb_vals[0]):02X}{int(rgb_vals[1]):02X}{int(rgb_vals[2]):02X}"
                colors.append(hex_color)

    # Process inline style matches
    for color in inline_matches:
        color = color.strip()
        if color.startswith('#'):
            if len(color) == 4:
                color = f"#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}"
            colors.append(color.upper())

    # Convert RGB to hex
    for r, g, b in rgb_matches:
        hex_color = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
        colors.append(hex_color)

    # Count occurrences and return most common
    color_counts = Counter(colors)

    # Filter out common defaults and near-white/near-black
    filtered_colors = []
    for color in color_counts:
        # Skip pure white, black, and very light/dark grays
        if color in ['#FFFFFF', '#000000', '#FFF', '#000', '#FEFEFE', '#010101']:
            continue
        # Skip very light colors (RGB > 250,250,250)
        if len(color) == 7:
            try:
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                if (r > 250 and g > 250 and b > 250) or (r < 5 and g < 5 and b < 5):
                    continue
            except:
                pass
        filtered_colors.append(color)

    # Return top 8 most common colors (increased from 5 for better variety)
    most_common = [color for color, count in Counter(filtered_colors).most_common(8)]

    logger.info(f"Extracted {len(most_common)} brand colors: {most_common[:5]}")

    return most_common


def extract_logo_urls(html_content: str, base_url: str) -> List[str]:
    """
    Extract potential logo image URLs from HTML.

    Args:
        html_content: Raw HTML content
        base_url: Website base URL for resolving relative paths

    Returns:
        List of potential logo image URLs
    """
    logo_urls = []

    # Common logo patterns in HTML
    logo_patterns = [
        r'<img[^>]+class=["\'][^"\']*logo[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]+class=["\'][^"\']*logo[^"\']*["\']',
        r'<img[^>]+alt=["\'][^"\']*logo[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
        r'<img[^>]+id=["\'][^"\']*logo[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
        r'<a[^>]+class=["\'][^"\']*logo[^"\']*["\'][^>]*>\s*<img[^>]+src=["\']([^"\']+)["\']',
    ]

    for pattern in logo_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, match)
            if absolute_url not in logo_urls:
                logo_urls.append(absolute_url)

    return logo_urls


def extract_text_content(html_content: str) -> Dict[str, str]:
    """
    Extract meaningful text content from HTML (about, services, etc).

    Args:
        html_content: Raw HTML content

    Returns:
        Dictionary with extracted text sections
    """
    # Remove script and style tags
    cleaned = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'<style[^>]*>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', cleaned)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Extract sections based on common headings
    content = {
        "full_text": text[:5000],  # First 5000 chars
        "about": "",
        "services": "",
        "contact": ""
    }

    # Try to find "About" section
    about_match = re.search(
        r'(?:about\s+us|about|who\s+we\s+are|our\s+story)[\s:]*([^.]{50,500})',
        html_content,
        re.IGNORECASE | re.DOTALL
    )
    if about_match:
        about_text = re.sub(r'<[^>]+>', ' ', about_match.group(1))
        content["about"] = re.sub(r'\s+', ' ', about_text).strip()[:500]

    # Try to find "Services" section
    services_match = re.search(
        r'(?:our\s+services|services|what\s+we\s+do|offerings)[\s:]*([^.]{50,500})',
        html_content,
        re.IGNORECASE | re.DOTALL
    )
    if services_match:
        services_text = re.sub(r'<[^>]+>', ' ', services_match.group(1))
        content["services"] = re.sub(r'\s+', ' ', services_text).strip()[:500]

    return content


def extract_contact_info(html_content: str, business_phone: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Extract and validate contact information.

    Args:
        html_content: Raw HTML content
        business_phone: Known business phone (optional)

    Returns:
        Dictionary with contact info (phone, email, address)
    """
    contact = {
        "phone": business_phone,
        "email": None,
        "address": None
    }

    # Extract phone numbers (UK and international formats)
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\d{5}[\s]?\d{6}',  # UK format: 01234 567890
    ]

    for pattern in phone_patterns:
        phones = re.findall(pattern, html_content)
        if phones and not contact["phone"]:
            contact["phone"] = phones[0]
            break

    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, html_content)
    if emails:
        # Filter out common generic/spam emails
        valid_emails = [
            email for email in emails
            if not any(spam in email.lower() for spam in ['noreply', 'example', 'test', 'spam'])
        ]
        if valid_emails:
            contact["email"] = valid_emails[0]

    return contact


def extract_images(html_content: str, base_url: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Extract image URLs and metadata.

    Args:
        html_content: Raw HTML content
        base_url: Website base URL
        limit: Maximum number of images to extract

    Returns:
        List of image dictionaries with url, alt, and type
    """
    images = []

    # Match img tags with src and optional alt
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'](?:[^>]+alt=["\']([^"\']*)["\'])?[^>]*>'
    matches = re.findall(img_pattern, html_content, re.IGNORECASE)

    for src, alt in matches[:limit]:
        # Skip tiny images, tracking pixels, icons
        if any(skip in src.lower() for skip in ['icon', 'pixel', 'track', '1x1', 'spacer']):
            continue

        # Convert to absolute URL
        absolute_url = urljoin(base_url, src)

        # Determine image type from URL or alt text
        img_type = "general"
        if any(word in (src + alt).lower() for word in ['logo', 'brand']):
            img_type = "logo"
        elif any(word in (src + alt).lower() for word in ['hero', 'banner', 'header']):
            img_type = "hero"
        elif any(word in (src + alt).lower() for word in ['product', 'service', 'portfolio']):
            img_type = "content"

        images.append({
            "url": absolute_url,
            "alt": alt or "",
            "type": img_type
        })

    return images


def extract_business_content(
    html_content: str,
    base_url: str,
    business_phone: Optional[str] = None
) -> Dict:
    """
    Extract all useful content from business website.

    Main interface for content extraction.

    Args:
        html_content: Raw HTML content from website
        base_url: Website base URL
        business_phone: Known business phone (optional)

    Returns:
        Comprehensive dictionary with all extracted content:
        {
            "colors": ["#FF5733", "#3498DB"],
            "logos": ["https://example.com/logo.png"],
            "text_content": {"about": "...", "services": "...", "full_text": "..."},
            "contact": {"phone": "...", "email": "...", "address": "..."},
            "images": [{"url": "...", "alt": "...", "type": "..."}],
            "metadata": {
                "total_colors_found": 15,
                "total_images_found": 25,
                "has_logo": True,
                "has_about_section": True
            }
        }
    """

    logger.info(f"Extracting content from {base_url}")

    # Extract all components
    colors = extract_colors_from_text(html_content)
    logos = extract_logo_urls(html_content, base_url)
    text_content = extract_text_content(html_content)
    contact = extract_contact_info(html_content, business_phone)
    images = extract_images(html_content, base_url, limit=15)

    # Build result
    result = {
        "colors": colors,
        "logos": logos,
        "text_content": text_content,
        "contact": contact,
        "images": images,
        "metadata": {
            "total_colors_found": len(colors),
            "total_images_found": len(images),
            "has_logo": len(logos) > 0,
            "has_about_section": len(text_content.get("about", "")) > 50,
            "has_services_section": len(text_content.get("services", "")) > 50,
            "has_contact_info": any([
                contact.get("phone"),
                contact.get("email"),
                contact.get("address")
            ])
        }
    }

    logger.info(f"Extracted: {len(colors)} colors, {len(logos)} logos, {len(images)} images")

    return result


def get_fallback_colors(business_type: str) -> List[str]:
    """
    Get fallback color palette if extraction fails.

    Args:
        business_type: Business type from classifier

    Returns:
        List of appropriate fallback colors for business type
    """
    fallback_palettes = {
        "restaurant": ["#8B4513", "#D2691E", "#FFF8DC", "#2C1810"],
        "professional": ["#1E3A8A", "#475569", "#F8FAFC", "#334155"],
        "home_services": ["#2563EB", "#F97316", "#FFFFFF", "#1E40AF"],
        "health_medical": ["#3B82F6", "#FFFFFF", "#10B981", "#E0F2FE"],
        "beauty_wellness": ["#EC4899", "#A855F7", "#FDF2F8", "#F3E8FF"],
        "fitness": ["#DC2626", "#171717", "#F97316", "#FEE2E2"],
        "retail": ["#8B5CF6", "#F472B6", "#FFFFFF", "#DDD6FE"],
        "real_estate": ["#1E40AF", "#D97706", "#FFFFFF", "#DBEAFE"],
        "automotive": ["#64748B", "#DC2626", "#FFFFFF", "#F1F5F9"],
        "education": ["#2563EB", "#FBBF24", "#10B981", "#DBEAFE"],
        "creative": ["#8B5CF6", "#EC4899", "#F59E0B", "#F3E8FF"],
        "hospitality": ["#0EA5E9", "#F5F5DC", "#10B981", "#E0F2FE"]
    }

    return fallback_palettes.get(business_type, ["#3B82F6", "#FFFFFF", "#1F2937"])
