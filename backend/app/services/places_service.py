"""Google Places API service for real-time business discovery"""
import requests
from typing import Dict, Any, List, Optional
from app.utils.logging_config import get_logger
from app.config import settings

logger = get_logger(__name__)


class PlacesService:
    """
    Service for discovering real businesses using Google Places API (New).

    This service uses the new Google Places API to find real UK businesses by location
    and category, returning actual business data with website URLs.
    """

    # Google Places API (New) endpoints
    PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
    PLACE_DETAILS_URL = "https://places.googleapis.com/v1/places"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Places service.

        Args:
            api_key: Google API key (same key used for PageSpeed Insights)
        """
        self.api_key = api_key or getattr(settings, 'GOOGLE_API_KEY', None)
        if not self.api_key:
            logger.warning("No Google API key configured for Places API")

    def search_businesses(
        self,
        location: str,
        category: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for real businesses by location and category using Places API (New).

        Args:
            location: UK location (e.g., "London", "Manchester", "Birmingham")
            category: Business category/niche (e.g., "plumber", "restaurant", "electrician")
            max_results: Maximum number of results to return (default: 10)

        Returns:
            List of business dictionaries with name, address, phone, website, etc.

        Raises:
            Exception: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Google API key not configured. Please set GOOGLE_API_KEY in .env file")

        logger.info(f"Searching for '{category}' businesses in '{location}'")

        try:
            # Build search query
            query = f"{category} in {location}, UK"

            # Prepare request headers and body for new API
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount"
            }

            body = {
                "textQuery": query,
                "languageCode": "en",
                "regionCode": "GB",  # UK region code
                "maxResultCount": min(max_results, 20)  # API limit is 20
            }

            # Make API request (POST for new API)
            response = requests.post(
                self.PLACES_SEARCH_URL,
                headers=headers,
                json=body,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Get places from response
            places = data.get("places", [])

            if not places:
                logger.warning(f"No businesses found for '{category}' in '{location}'")
                return []

            # Process results
            businesses = []
            for place in places[:max_results]:
                try:
                    business_data = self._process_place_result(place)
                    if business_data:
                        businesses.append(business_data)
                except Exception as e:
                    logger.warning(f"Failed to process place {place.get('displayName', {}).get('text', 'Unknown')}: {str(e)}")
                    continue

            logger.info(f"Found {len(businesses)} businesses for '{category}' in '{location}'")
            return businesses

        except requests.exceptions.Timeout:
            logger.error(f"Places API request timed out")
            raise Exception("Business search timed out. Please try again.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Places API request failed: {str(e)}")
            raise Exception(f"Failed to search businesses: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during business search: {str(e)}")
            raise Exception(f"Business search error: {str(e)}")

    def _process_place_result(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single place result from Places API (New).

        Args:
            place: Place data from Places API (New)

        Returns:
            Processed business data dictionary or None if invalid
        """
        # Extract business information from new API format
        place_id = place.get("id")
        if not place_id:
            return None

        # Get name (displayName.text in new API)
        display_name = place.get("displayName", {})
        name = display_name.get("text") if isinstance(display_name, dict) else None
        if not name:
            return None

        # Get address
        address = place.get("formattedAddress", "")

        # Get location coordinates
        location = place.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        # Get contact info
        phone = place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber")
        website = place.get("websiteUri")

        # Get rating and reviews
        rating = place.get("rating", 0)
        user_ratings_total = place.get("userRatingCount", 0)

        # Get business type/category
        types = place.get("types", [])
        category = types[0] if types else "business"

        business_data = {
            "name": name,
            "address": address,
            "city": self._extract_city_from_address(address),
            "category": category,
            "phone": phone,
            "website_url": website,
            "latitude": latitude,
            "longitude": longitude,
            "rating": rating,
            "reviews_count": user_ratings_total,
            "place_id": place_id
        }

        return business_data

    def _extract_city_from_address(self, address: str) -> str:
        """
        Extract city name from formatted address.

        Args:
            address: Formatted address string

        Returns:
            City name or empty string
        """
        if not address:
            return ""

        # Try to extract city (usually after first comma)
        parts = address.split(",")
        if len(parts) >= 2:
            # Return the part that's likely the city (second part)
            return parts[1].strip()

        return ""


# Global singleton instance
_places_service: Optional[PlacesService] = None


def get_places_service() -> PlacesService:
    """
    Get or create the global Places service instance.

    Returns:
        PlacesService instance
    """
    global _places_service
    if _places_service is None:
        _places_service = PlacesService()
    return _places_service
