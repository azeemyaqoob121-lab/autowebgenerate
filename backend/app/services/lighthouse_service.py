"""Lighthouse integration service using Google PageSpeed Insights API"""
import requests
from typing import Dict, Any, Optional
from app.utils.logging_config import get_logger
from app.config import settings

logger = get_logger(__name__)


class LighthouseService:
    """
    Service for running Google Lighthouse audits via PageSpeed Insights API.

    This service uses Google's free PageSpeed Insights API which runs Lighthouse
    audits on websites and returns performance, SEO, accessibility, and best practices scores.

    No API key required for basic usage, but rate limits apply.
    For production use, get a free API key from: https://developers.google.com/speed/docs/insights/v5/get-started
    """

    # PageSpeed Insights API endpoint
    API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Lighthouse service.

        Args:
            api_key: Optional Google API key for higher rate limits
        """
        self.api_key = api_key or getattr(settings, 'GOOGLE_API_KEY', None)
        logger.info(f"LighthouseService initialized with API key: {self.api_key[:30] if self.api_key else 'None'}...")

    def run_audit(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        """
        Run a Lighthouse audit on the given URL.

        Args:
            url: Website URL to audit
            strategy: "mobile" or "desktop" (default: mobile)

        Returns:
            Dict containing Lighthouse audit results with scores

        Raises:
            Exception: If the audit fails
        """
        logger.info(f"Starting Lighthouse audit for: {url} (strategy: {strategy})")

        try:
            # Prepare API request
            params = {
                "url": url,
                "strategy": strategy,
                "category": ["performance", "seo", "accessibility", "best-practices"]
            }

            # Add API key if available
            if self.api_key:
                params["key"] = self.api_key

            # Make API request
            response = requests.get(
                self.API_URL,
                params=params,
                timeout=60  # Lighthouse audits can take time
            )

            response.raise_for_status()
            data = response.json()

            # Extract Lighthouse results
            lighthouse_result = data.get("lighthouseResult", {})
            categories = lighthouse_result.get("categories", {})

            # Extract scores (0-1 range)
            performance_score = categories.get("performance", {}).get("score", 0)
            seo_score = categories.get("seo", {}).get("score", 0)
            accessibility_score = categories.get("accessibility", {}).get("score", 0)
            best_practices_score = categories.get("best-practices", {}).get("score", 0)

            # Calculate aggregate score (0-100)
            aggregate_score = ((performance_score + seo_score + accessibility_score + best_practices_score) / 4) * 100

            result = {
                "performance_score": performance_score,
                "seo_score": seo_score,
                "accessibility_score": accessibility_score,
                "best_practices_score": best_practices_score,
                "aggregate_score": aggregate_score,
                "lighthouse_data": {
                    "performance": round(performance_score * 100),
                    "seo": round(seo_score * 100),
                    "accessibility": round(accessibility_score * 100),
                    "best_practices": round(best_practices_score * 100),
                    "fetch_time": lighthouse_result.get("fetchTime"),
                    "final_url": lighthouse_result.get("finalUrl"),
                    "strategy": strategy
                },
                "success": True
            }

            logger.info(
                f"Lighthouse audit completed for {url}: "
                f"aggregate={aggregate_score:.2f}, "
                f"performance={performance_score:.2f}, "
                f"seo={seo_score:.2f}, "
                f"accessibility={accessibility_score:.2f}"
            )

            return result

        except requests.exceptions.Timeout:
            logger.error(f"Lighthouse audit timed out for {url}")
            raise Exception("Lighthouse audit timed out. Please try again.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Lighthouse audit failed for {url}: {str(e)}")
            raise Exception(f"Failed to run Lighthouse audit: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during Lighthouse audit for {url}: {str(e)}")
            raise Exception(f"Lighthouse audit error: {str(e)}")

    def run_audit_with_validation(self, url: str) -> Dict[str, Any]:
        """
        Run Lighthouse audit with URL validation.

        Only returns real data from Google PageSpeed Insights API.
        Raises exception if URL is invalid or audit fails.

        Args:
            url: Website URL to audit

        Returns:
            Dict containing real Lighthouse results

        Raises:
            Exception: If URL is invalid or audit fails
        """
        # Validate URL format
        if not url or not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")

        # Run real audit - no fallback
        return self.run_audit(url)


# Global singleton instance
_lighthouse_service: Optional[LighthouseService] = None


def get_lighthouse_service() -> LighthouseService:
    """
    Get or create the global Lighthouse service instance.

    Returns:
        LighthouseService instance
    """
    global _lighthouse_service
    if _lighthouse_service is None:
        _lighthouse_service = LighthouseService()
    return _lighthouse_service


def reset_lighthouse_service() -> None:
    """
    Reset the global Lighthouse service instance.
    Useful when API key has been updated.
    """
    global _lighthouse_service
    _lighthouse_service = None
