"""
Brand Asset Downloader Service

Downloads and saves original brand assets (logos, images, videos) from scraped websites.
Preserves 100% of the original brand identity by using THEIR actual media files.
"""

import os
import requests
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
import base64
from io import BytesIO
from PIL import Image

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class BrandAssetDownloader:
    """
    Downloads and manages brand assets from original websites.

    Features:
    - Downloads logos, images, and videos
    - Optimizes images (resize, compress) while maintaining quality
    - Generates thumbnails for videos
    - Stores assets with organized folder structure
    - Returns CDN-ready URLs or base64 data URIs
    """

    def __init__(self, business_id: str, storage_dir: str = "static/brand_assets"):
        """
        Initialize the downloader

        Args:
            business_id: Unique identifier for the business
            storage_dir: Base directory for storing assets
        """
        self.business_id = business_id
        self.base_dir = Path(storage_dir) / business_id

        # Create subdirectories
        self.logos_dir = self.base_dir / "logos"
        self.images_dir = self.base_dir / "images"
        self.videos_dir = self.base_dir / "videos"

        # Create directories if they don't exist
        for directory in [self.logos_dir, self.images_dir, self.videos_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized BrandAssetDownloader for business {business_id}")

    def download_file(self, url: str, timeout: int = 15) -> Optional[bytes]:
        """
        Download a file from a URL

        Args:
            url: URL to download from
            timeout: Request timeout in seconds

        Returns:
            File content as bytes, or None if download fails
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()

            # Check file size (max 10MB for images, 50MB for videos)
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > 50:
                    logger.warning(f"File too large ({size_mb:.1f}MB): {url}")
                    return None

            content = response.content
            logger.info(f"Downloaded {len(content)} bytes from {url}")
            return content

        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return None

    def get_file_extension(self, url: str, content: bytes) -> str:
        """
        Determine file extension from URL or content type

        Args:
            url: Original URL
            content: File content

        Returns:
            File extension (e.g., '.jpg', '.png')
        """
        # Try to get from URL
        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.mp4', '.webm', '.mov']:
            return ext

        # Try to detect from content
        try:
            if content[:2] == b'\xff\xd8':
                return '.jpg'
            elif content[:8] == b'\x89PNG\r\n\x1a\n':
                return '.png'
            elif content[:6] in [b'GIF87a', b'GIF89a']:
                return '.gif'
            elif content[:4] == b'RIFF' and content[8:12] == b'WEBP':
                return '.webp'
        except:
            pass

        return '.jpg'  # Default fallback

    def optimize_image(self, image_bytes: bytes, max_width: int = 1920, quality: int = 85) -> bytes:
        """
        Optimize image file size while maintaining quality

        Args:
            image_bytes: Original image bytes
            max_width: Maximum width to resize to
            quality: JPEG quality (1-100)

        Returns:
            Optimized image bytes
        """
        try:
            # Open image
            img = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB if saving as JPEG
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {max_width}x{new_height}")

            # Save optimized
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_bytes = output.getvalue()

            # Calculate savings
            original_size = len(image_bytes) / 1024
            optimized_size = len(optimized_bytes) / 1024
            savings = ((original_size - optimized_size) / original_size) * 100

            logger.info(f"Optimized: {original_size:.1f}KB -> {optimized_size:.1f}KB ({savings:.1f}% savings)")

            return optimized_bytes

        except Exception as e:
            logger.error(f"Failed to optimize image: {str(e)}")
            return image_bytes  # Return original if optimization fails

    def generate_filename(self, url: str, content: bytes) -> str:
        """
        Generate a unique filename based on URL and content hash

        Args:
            url: Original URL
            content: File content

        Returns:
            Unique filename
        """
        # Create hash from URL + content
        hash_input = (url + str(len(content))).encode('utf-8')
        file_hash = hashlib.md5(hash_input).hexdigest()[:12]

        # Get extension
        ext = self.get_file_extension(url, content)

        return f"{file_hash}{ext}"

    def download_logo(self, logo_url: str, optimize: bool = True) -> Optional[Dict[str, str]]:
        """
        Download and save a logo

        Args:
            logo_url: URL of the logo to download
            optimize: Whether to optimize the image

        Returns:
            Dict with local_path, url, and data_uri
        """
        if not logo_url:
            return None

        try:
            # Download
            content = self.download_file(logo_url)
            if not content:
                return None

            # Optimize (smaller dimensions for logos)
            if optimize:
                content = self.optimize_image(content, max_width=800, quality=90)

            # Generate filename
            filename = self.generate_filename(logo_url, content)
            file_path = self.logos_dir / filename

            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(content)

            # Generate data URI for embedding
            ext = self.get_file_extension(logo_url, content)
            mime_type = f"image/{ext[1:]}" if ext != '.svg' else 'image/svg+xml'
            data_uri = f"data:{mime_type};base64,{base64.b64encode(content).decode('utf-8')}"

            logger.info(f"[DOWNLOAD] Downloaded logo: {filename}")

            return {
                'original_url': logo_url,
                'local_path': str(file_path),
                'filename': filename,
                'url': f"/brand_assets/{self.business_id}/logos/{filename}",
                'data_uri': data_uri,
                'size_kb': len(content) / 1024
            }

        except Exception as e:
            logger.error(f"Failed to download logo {logo_url}: {str(e)}")
            return None

    def download_image(self, image_data: Dict[str, str], optimize: bool = True) -> Optional[Dict[str, str]]:
        """
        Download and save an image

        Args:
            image_data: Dict with 'url' and optionally 'alt'
            optimize: Whether to optimize the image

        Returns:
            Dict with local_path, url, alt, and data_uri
        """
        image_url = image_data.get('url')
        if not image_url:
            return None

        try:
            # Download
            content = self.download_file(image_url)
            if not content:
                return None

            # Optimize
            if optimize:
                content = self.optimize_image(content, max_width=1920, quality=85)

            # Generate filename
            filename = self.generate_filename(image_url, content)
            file_path = self.images_dir / filename

            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(content)

            logger.info(f"[DOWNLOAD] Downloaded image: {filename}")

            return {
                'original_url': image_url,
                'local_path': str(file_path),
                'filename': filename,
                'url': f"/brand_assets/{self.business_id}/images/{filename}",
                'alt': image_data.get('alt', ''),
                'size_kb': len(content) / 1024
            }

        except Exception as e:
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None

    def download_video(self, video_data: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Download and save a video (only for direct video files, not YouTube/Vimeo)

        Args:
            video_data: Dict with 'url', 'type', etc.

        Returns:
            Dict with local_path and url, or original data for embeds
        """
        video_url = video_data.get('url')
        video_type = video_data.get('type', '')

        # If it's YouTube or Vimeo, just return the embed data
        if video_type in ['youtube', 'vimeo']:
            logger.info(f"Preserving {video_type} embed: {video_data.get('video_id')}")
            return video_data

        try:
            # Download direct video file
            content = self.download_file(video_url, timeout=30)
            if not content:
                return None

            # Generate filename
            filename = self.generate_filename(video_url, content)
            file_path = self.videos_dir / filename

            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(content)

            logger.info(f"[DOWNLOAD] Downloaded video: {filename} ({len(content) / 1024 / 1024:.1f}MB)")

            return {
                'original_url': video_url,
                'local_path': str(file_path),
                'filename': filename,
                'url': f"/brand_assets/{self.business_id}/videos/{filename}",
                'type': video_data.get('type', 'video/mp4'),
                'size_mb': len(content) / 1024 / 1024
            }

        except Exception as e:
            logger.error(f"Failed to download video {video_url}: {str(e)}")
            return None

    def download_all_assets(
        self,
        scraped_data: Dict[str, Any],
        max_images: int = 20
    ) -> Dict[str, Any]:
        """
        Download all brand assets from scraped website data

        Args:
            scraped_data: Output from WebsiteContentScraper.scrape_all()
            max_images: Maximum number of images to download

        Returns:
            Dict with downloaded assets organized by type
        """
        logger.info(f"Starting brand asset download for business {self.business_id}")

        downloaded_assets = {
            'logo': None,
            'images': [],
            'videos': [],
            'colors': scraped_data.get('colors', []),
            'fonts': scraped_data.get('fonts', {}),
            'summary': {
                'total_downloaded': 0,
                'logos': 0,
                'images': 0,
                'videos': 0,
                'total_size_mb': 0
            }
        }

        # Download logo
        logo_url = scraped_data.get('logo')
        if logo_url:
            logo_data = self.download_logo(logo_url)
            if logo_data:
                downloaded_assets['logo'] = logo_data
                downloaded_assets['summary']['logos'] = 1
                downloaded_assets['summary']['total_downloaded'] += 1
                downloaded_assets['summary']['total_size_mb'] += logo_data.get('size_kb', 0) / 1024

        # Download images
        images = scraped_data.get('images', [])[:max_images]
        for img_data in images:
            downloaded_img = self.download_image(img_data)
            if downloaded_img:
                downloaded_assets['images'].append(downloaded_img)
                downloaded_assets['summary']['images'] += 1
                downloaded_assets['summary']['total_downloaded'] += 1
                downloaded_assets['summary']['total_size_mb'] += downloaded_img.get('size_kb', 0) / 1024

        # Download videos
        videos = scraped_data.get('videos', [])
        for video_data in videos[:5]:  # Limit to 5 videos
            downloaded_video = self.download_video(video_data)
            if downloaded_video:
                downloaded_assets['videos'].append(downloaded_video)
                downloaded_assets['summary']['videos'] += 1
                downloaded_assets['summary']['total_downloaded'] += 1
                if 'size_mb' in downloaded_video:
                    downloaded_assets['summary']['total_size_mb'] += downloaded_video.get('size_mb', 0)

        logger.info(
            f"[DOWNLOAD] Asset download complete: "
            f"{downloaded_assets['summary']['logos']} logos, "
            f"{downloaded_assets['summary']['images']} images, "
            f"{downloaded_assets['summary']['videos']} videos "
            f"({downloaded_assets['summary']['total_size_mb']:.1f}MB total)"
        )

        return downloaded_assets


def download_brand_assets(business_id: str, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to download all brand assets

    Args:
        business_id: Unique business identifier
        scraped_data: Scraped website data

    Returns:
        Dict with all downloaded assets
    """
    downloader = BrandAssetDownloader(business_id)
    return downloader.download_all_assets(scraped_data)
