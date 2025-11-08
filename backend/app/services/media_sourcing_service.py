"""Media Sourcing Service

Automatically fetches premium images and videos from Unsplash and Pexels
based on business type and requirements.
"""

import logging
import random
from typing import List, Dict, Optional
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class ImageAsset:
    """Represents an image asset with attribution"""

    def __init__(
        self,
        url: str,
        alt: str,
        photographer: str = "",
        photographer_url: str = "",
        source: str = "Unsplash"
    ):
        self.url = url
        self.alt = alt
        self.photographer = photographer
        self.photographer_url = photographer_url
        self.source = source

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "alt": self.alt,
            "photographer": self.photographer,
            "photographer_url": self.photographer_url,
            "source": self.source
        }


class VideoAsset:
    """Represents a video asset"""

    def __init__(
        self,
        url: str,
        poster: str = "",
        attribution: str = "",
        duration: int = 0
    ):
        self.url = url
        self.poster = poster
        self.attribution = attribution
        self.duration = duration

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "poster": self.poster,
            "attribution": self.attribution,
            "duration": self.duration
        }


class MediaSourcingService:
    """
    Service for fetching premium media from Unsplash and Pexels.

    Features:
    - Business-type-specific image searches
    - Hero background video sourcing
    - Fallback to placeholder images
    - Proper attribution handling
    - Rate limit management
    """

    # Business-type-specific search keywords
    BUSINESS_KEYWORDS = {
        "restaurant": [
            "fine dining", "food plating", "restaurant ambiance",
            "chef cooking", "gourmet food", "restaurant interior",
            "food photography", "culinary", "dining experience",
            "appetizer", "main course", "dessert presentation"
        ],
        "service_business": [
            "professional handyman", "home renovation", "tools equipment",
            "construction", "repair service", "contractor work",
            "before after home", "professional service", "quality workmanship"
        ],
        "professional_services": [
            "office professional", "business meeting", "corporate team",
            "modern workspace", "business consulting", "professional office",
            "team collaboration", "executive", "business success"
        ],
        "retail": [
            "boutique shopping", "product display", "retail interior",
            "shopping experience", "store front", "merchandise",
            "retail design", "product photography", "store display"
        ],
        "healthcare": [
            "medical professional", "healthcare", "clinic interior",
            "patient care", "medical equipment", "hospital",
            "doctor", "health wellness", "medical facility"
        ],
        "fitness": [
            "fitness training", "gym equipment", "workout", "personal trainer",
            "fitness studio", "athletic", "exercise", "health fitness",
            "gym interior", "wellness"
        ],
        "default": [
            "business", "professional", "modern office", "corporate",
            "team", "success", "innovation", "growth"
        ]
    }

    VIDEO_KEYWORDS = {
        "restaurant": [
            "cooking", "food preparation", "restaurant kitchen", "dining",
            "chef cooking", "gourmet food", "fine dining", "culinary art",
            "food plating", "restaurant ambiance"
        ],
        "service_business": [
            "construction", "renovation", "handyman", "tools",
            "building", "craftsmanship", "contractor", "home improvement",
            "repair work", "skilled trades"
        ],
        "professional_services": [
            "business meeting", "office", "corporate", "team",
            "collaboration", "conference", "professional workspace", "business people",
            "teamwork", "modern office"
        ],
        "retail": [
            "shopping", "store", "retail", "products",
            "boutique", "customer shopping", "retail display", "storefront",
            "shopping mall", "commercial"
        ],
        "healthcare": [
            "medical", "healthcare", "clinic", "doctor",
            "hospital", "patient care", "medical facility", "health",
            "medical professional", "healthcare worker"
        ],
        "health_medical": [
            "medical", "healthcare", "clinic", "doctor",
            "dental", "dentist", "medical office", "patient",
            "healthcare professional", "medical treatment"
        ],
        "fitness": [
            "fitness", "gym", "workout", "exercise",
            "training", "athlete", "sports", "wellness",
            "fitness studio", "active lifestyle"
        ],
        "default": [
            "business", "office", "professional", "corporate",
            "modern workspace", "technology", "innovation", "success",
            "growth", "teamwork"
        ]
    }

    def __init__(self, unsplash_key: str = "", pexels_key: str = ""):
        """
        Initialize media sourcing service.

        Args:
            unsplash_key: Unsplash API access key
            pexels_key: Pexels API key
        """
        self.unsplash_key = unsplash_key
        self.pexels_key = pexels_key

        self.unsplash_api_url = "https://api.unsplash.com"
        self.pexels_api_url = "https://api.pexels.com/v1"

        logger.info(
            f"MediaSourcingService initialized "
            f"(Unsplash: {'✓' if unsplash_key else '✗'}, "
            f"Pexels: {'✓' if pexels_key else '✗'})"
        )

    async def get_business_images(
        self,
        business_type: str,
        business_name: str = "",
        count: int = 15,
        orientation: str = "landscape"
    ) -> List[ImageAsset]:
        """
        Fetch business-appropriate images from Unsplash.

        Args:
            business_type: Type of business (restaurant, service_business, etc.)
            business_name: Name of business (for more specific searches)
            count: Number of images to fetch (default 15)
            orientation: Image orientation (landscape, portrait, squarish)

        Returns:
            List of ImageAsset objects
        """
        if not self.unsplash_key:
            logger.warning("No Unsplash API key configured, using placeholder images")
            return self.get_placeholder_images(count)

        try:
            # Get keywords for business type
            keywords = self.BUSINESS_KEYWORDS.get(
                business_type,
                self.BUSINESS_KEYWORDS["default"]
            )

            # Fetch images for multiple keywords to get variety
            images = []
            images_per_keyword = max(2, count // len(keywords[:6]))  # Use up to 6 keywords

            for keyword in keywords[:6]:
                try:
                    keyword_images = await self._fetch_unsplash_images(
                        query=keyword,
                        count=images_per_keyword,
                        orientation=orientation
                    )
                    images.extend(keyword_images)

                    if len(images) >= count:
                        break

                except Exception as e:
                    logger.error(f"Error fetching images for keyword '{keyword}': {e}")
                    continue

            # If we didn't get enough images, fill with placeholders
            if len(images) < count:
                logger.warning(
                    f"Only fetched {len(images)}/{count} images from Unsplash, "
                    f"filling with placeholders"
                )
                images.extend(
                    self.get_placeholder_images(count - len(images), business_type)
                )

            return images[:count]

        except Exception as e:
            logger.error(f"Error in get_business_images: {e}")
            return self.get_placeholder_images(count, business_type)

    async def _fetch_unsplash_images(
        self,
        query: str,
        count: int = 5,
        orientation: str = "landscape"
    ) -> List[ImageAsset]:
        """
        Fetch images from Unsplash API.

        Args:
            query: Search query
            count: Number of images
            orientation: Image orientation

        Returns:
            List of ImageAsset objects
        """
        url = f"{self.unsplash_api_url}/search/photos"
        params = {
            "query": query,
            "per_page": min(count, 30),  # Unsplash max is 30
            "orientation": orientation,
            "order_by": "relevant"
        }
        headers = {
            "Authorization": f"Client-ID {self.unsplash_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        f"Unsplash API error: {response.status} - {await response.text()}"
                    )
                    return []

                data = await response.json()

                images = []
                for photo in data.get("results", []):
                    images.append(
                        ImageAsset(
                            url=photo["urls"]["regular"],  # 1080px wide
                            alt=photo.get("alt_description", query),
                            photographer=photo["user"]["name"],
                            photographer_url=photo["user"]["links"]["html"],
                            source="Unsplash"
                        )
                    )

                return images

    async def get_hero_video(
        self,
        business_type: str,
        min_duration: int = 10,
        max_duration: int = 30
    ) -> Optional[VideoAsset]:
        """
        Fetch relevant hero background video from Pexels with variety.

        Args:
            business_type: Type of business
            min_duration: Minimum video duration in seconds
            max_duration: Maximum video duration in seconds

        Returns:
            VideoAsset object or None
        """
        if not self.pexels_key:
            logger.warning("No Pexels API key configured, no hero video available")
            return None

        try:
            # Get video keywords for business type
            keywords = self.VIDEO_KEYWORDS.get(
                business_type,
                self.VIDEO_KEYWORDS["default"]
            )

            # RANDOMIZE keyword order for variety across different businesses
            shuffled_keywords = keywords.copy()
            random.shuffle(shuffled_keywords)

            logger.info(f"Searching for hero video with keywords: {shuffled_keywords}")

            # Try each keyword until we find a suitable video
            for keyword in shuffled_keywords:
                try:
                    video = await self._fetch_pexels_video(
                        query=keyword,
                        min_duration=min_duration,
                        max_duration=max_duration
                    )

                    if video:
                        logger.info(f"✓ Selected hero video for keyword: '{keyword}'")
                        return video

                except Exception as e:
                    logger.error(f"Error fetching video for keyword '{keyword}': {e}")
                    continue

            logger.warning("No suitable video found on Pexels")
            return None

        except Exception as e:
            logger.error(f"Error in get_hero_video: {e}")
            return None

    async def _fetch_pexels_video(
        self,
        query: str,
        min_duration: int = 10,
        max_duration: int = 30
    ) -> Optional[VideoAsset]:
        """
        Fetch a video from Pexels API with random selection for variety.

        Args:
            query: Search query
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds

        Returns:
            VideoAsset object or None
        """
        url = f"{self.pexels_api_url}/videos/search"
        params = {
            "query": query,
            "per_page": 30,  # Get more videos for better variety
            "orientation": "landscape",
            "size": "medium"  # HD quality
        }
        headers = {
            "Authorization": self.pexels_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        f"Pexels API error: {response.status} - {await response.text()}"
                    )
                    return None

                data = await response.json()

                # Collect ALL suitable videos first (not just the first one)
                suitable_videos = []

                for video_data in data.get("videos", []):
                    duration = video_data.get("duration", 0)

                    # Check duration constraints
                    if min_duration <= duration <= max_duration:
                        # Get HD video file
                        video_files = video_data.get("video_files", [])

                        # Prefer 1920x1080 HD quality
                        hd_file = None
                        for vf in video_files:
                            if vf.get("quality") == "hd" or vf.get("width") >= 1920:
                                hd_file = vf
                                break

                        # Fallback to any HD file
                        if not hd_file:
                            hd_file = next(
                                (vf for vf in video_files if vf.get("quality") == "hd"),
                                None
                            )

                        # Fallback to first video file
                        if not hd_file and video_files:
                            hd_file = video_files[0]

                        if hd_file:
                            suitable_videos.append({
                                "url": hd_file["link"],
                                "poster": video_data.get("image", ""),
                                "attribution": f"Video by {video_data['user']['name']} on Pexels",
                                "duration": duration
                            })

                # RANDOMLY select one from suitable videos for variety
                if suitable_videos:
                    selected = random.choice(suitable_videos)
                    logger.info(
                        f"✓ Selected random video from {len(suitable_videos)} options "
                        f"for query '{query}'"
                    )
                    return VideoAsset(
                        url=selected["url"],
                        poster=selected["poster"],
                        attribution=selected["attribution"],
                        duration=selected["duration"]
                    )

                logger.warning(
                    f"No video found for '{query}' with duration "
                    f"{min_duration}-{max_duration}s"
                )
                return None

    def get_placeholder_images(
        self,
        count: int,
        business_type: str = "default"
    ) -> List[ImageAsset]:
        """
        Generate placeholder images using Unsplash Source API.

        This is a fallback when the Unsplash API is unavailable or rate-limited.

        Args:
            count: Number of placeholder images
            business_type: Type of business for relevant placeholders

        Returns:
            List of ImageAsset objects with Unsplash Source URLs
        """
        keywords = self.BUSINESS_KEYWORDS.get(
            business_type,
            self.BUSINESS_KEYWORDS["default"]
        )

        images = []

        for i in range(count):
            # Rotate through keywords
            keyword = keywords[i % len(keywords)].replace(" ", ",")

            # Use Unsplash Source for random images
            # Format: https://source.unsplash.com/1920x1080/?keyword
            url = f"https://source.unsplash.com/1920x1080/?{keyword}"

            images.append(
                ImageAsset(
                    url=url,
                    alt=f"{keyword.replace(',', ' ')} image",
                    photographer="Unsplash",
                    photographer_url="https://unsplash.com",
                    source="Unsplash Source (Placeholder)"
                )
            )

        return images

    async def get_gallery_images(
        self,
        business_type: str,
        count: int = 12
    ) -> List[ImageAsset]:
        """
        Get curated gallery images for business.

        This is a convenience method that fetches images optimized for galleries.

        Args:
            business_type: Type of business
            count: Number of images (default 12)

        Returns:
            List of ImageAsset objects
        """
        return await self.get_business_images(
            business_type=business_type,
            count=count,
            orientation="landscape"
        )

    async def get_team_images(
        self,
        count: int = 4
    ) -> List[ImageAsset]:
        """
        Get professional team member photos.

        Args:
            count: Number of team images

        Returns:
            List of ImageAsset objects
        """
        return await self.get_business_images(
            business_type="professional_services",
            count=count,
            orientation="portrait"
        )

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Check if API keys are configured.

        Returns:
            Dict with 'unsplash' and 'pexels' bool values
        """
        return {
            "unsplash": bool(self.unsplash_key),
            "pexels": bool(self.pexels_key)
        }

    async def test_connection(self) -> Dict[str, str]:
        """
        Test connections to Unsplash and Pexels APIs.

        Returns:
            Dict with connection status for each service
        """
        results = {}

        # Test Unsplash
        if self.unsplash_key:
            try:
                images = await self._fetch_unsplash_images("test", count=1)
                results["unsplash"] = "✓ Connected" if images else "✗ Failed"
            except Exception as e:
                results["unsplash"] = f"✗ Error: {str(e)}"
        else:
            results["unsplash"] = "✗ No API key"

        # Test Pexels
        if self.pexels_key:
            try:
                video = await self._fetch_pexels_video("business", min_duration=5)
                results["pexels"] = "✓ Connected" if video else "✗ Failed"
            except Exception as e:
                results["pexels"] = f"✗ Error: {str(e)}"
        else:
            results["pexels"] = "✗ No API key"

        return results


# ===== USAGE EXAMPLE =====
async def example_usage():
    """Example of how to use MediaSourcingService"""

    service = MediaSourcingService(
        unsplash_key="YOUR_UNSPLASH_ACCESS_KEY",
        pexels_key="YOUR_PEXELS_API_KEY"
    )

    # Test connection
    status = await service.test_connection()
    print("API Connection Status:", status)

    # Get restaurant images
    restaurant_images = await service.get_business_images(
        business_type="restaurant",
        business_name="Fine Dining Restaurant",
        count=15
    )

    print(f"\nFetched {len(restaurant_images)} restaurant images:")
    for img in restaurant_images[:3]:
        print(f"  - {img.alt} by {img.photographer}")

    # Get hero video
    hero_video = await service.get_hero_video(
        business_type="restaurant",
        min_duration=10,
        max_duration=30
    )

    if hero_video:
        print(f"\nHero video: {hero_video.attribution} ({hero_video.duration}s)")
    else:
        print("\nNo hero video available")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
