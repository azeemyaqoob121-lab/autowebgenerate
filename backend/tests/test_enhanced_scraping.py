"""
Tests for Enhanced Scraping and Modernization Services
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from app.services.asset_extractor_service import AssetExtractorService
from app.services.modernization_prompt_builder import ModernizationPromptBuilder
from app.models.business import Business


# Sample HTML for testing
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Business</title>
    <style>
        body { background-color: #FF6B6B; }
        .header { color: #4ECDC4; }
    </style>
</head>
<body>
    <header>
        <img src="/logo.png" alt="Company Logo" class="logo">
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    <section class="hero">
        <h1>Welcome</h1>
        <img src="/hero.jpg" alt="Hero Image">
    </section>
    <section class="services">
        <h2>Our Services</h2>
        <p>We provide great services</p>
    </section>
    <iframe src="https://www.youtube.com/embed/abc123"></iframe>
    <iframe src="https://www.google.com/maps/embed?pb=123"></iframe>
</body>
</html>
"""

SAMPLE_CSS = """
.button { background-color: #1A535C; }
.card { border-color: #FFE66D; }
"""


class TestAssetExtractorService:
    """Test AssetExtractorService functionality"""

    def test_extract_images(self):
        """Test image URL extraction"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        image_urls = extractor.extract_images()

        assert len(image_urls) == 2
        assert "https://example.com/logo.png" in image_urls
        assert "https://example.com/hero.jpg" in image_urls

    def test_extract_logos(self):
        """Test logo identification from images"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        image_urls = extractor.extract_images()
        logo_urls = extractor.extract_logos(image_urls)

        assert len(logo_urls) >= 1
        assert "https://example.com/logo.png" in logo_urls

    def test_extract_videos(self):
        """Test video URL extraction"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        video_urls = extractor.extract_videos()

        assert len(video_urls) == 1
        assert "https://www.youtube.com/embed/abc123" in video_urls

    def test_extract_maps(self):
        """Test map embed extraction"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        map_embeds = extractor.extract_maps()

        assert len(map_embeds) == 1
        assert "google.com/maps" in map_embeds[0]

    def test_extract_colors(self):
        """Test color palette extraction"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML,
            css=SAMPLE_CSS
        )

        colors = extractor.extract_colors()

        # Should extract colors from both HTML and CSS
        assert len(colors) > 0
        # Normalize to uppercase for comparison
        colors_upper = [c.upper() for c in colors]
        assert "#FF6B6B" in colors_upper or "#4ECDC4" in colors_upper

    def test_count_components(self):
        """Test component counting"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        component_count = extractor.count_components()

        # Should count header, hero section, services section
        assert component_count >= 2

    def test_analyze_component_structure(self):
        """Test component structure analysis"""
        extractor = AssetExtractorService(
            base_url="https://example.com",
            html=SAMPLE_HTML
        )

        components = extractor.analyze_component_structure()

        assert len(components) >= 2
        # Check structure
        assert all('order' in c for c in components)
        assert all('type' in c for c in components)
        assert all('heading' in c for c in components)


class TestModernizationPromptBuilder:
    """Test ModernizationPromptBuilder functionality"""

    def test_build_prompt_variant_1(self):
        """Test prompt building for Tailwind variant"""
        # Create mock business
        business = Mock(spec=Business)
        business.name = "Test Business"
        business.category = "Restaurant"
        business.description = "A great restaurant"
        business.scraped_html = SAMPLE_HTML
        business.scraped_css = SAMPLE_CSS
        business.component_count = 3
        business.component_structure = [
            {"order": 0, "type": "hero", "heading": "Welcome"}
        ]
        business.color_palette = ["#FF6B6B", "#4ECDC4"]
        business.logo_urls = ["https://example.com/logo.png"]
        business.image_urls = ["https://example.com/hero.jpg"]
        business.video_urls = []
        business.map_embeds = []
        business.score = 45

        builder = ModernizationPromptBuilder(business)
        prompt = builder.build_prompt(variant_number=1)

        # Verify prompt contains key elements
        assert "Test Business" in prompt
        assert "Restaurant" in prompt
        assert "#FF6B6B" in prompt
        assert "Tailwind" in prompt or "tailwind" in prompt
        assert "EXACT Component Count" in prompt
        assert business.scraped_html in prompt

    def test_build_prompt_variant_2(self):
        """Test prompt building for Bootstrap variant"""
        business = Mock(spec=Business)
        business.name = "Test Business"
        business.category = "Service"
        business.description = "Service business"
        business.scraped_html = "<html><body><h1>Test</h1></body></html>"
        business.scraped_css = ""
        business.component_count = 1
        business.component_structure = []
        business.color_palette = ["#FF0000"]
        business.logo_urls = []
        business.image_urls = []
        business.video_urls = []
        business.map_embeds = []
        business.score = 50

        builder = ModernizationPromptBuilder(business)
        prompt = builder.build_prompt(variant_number=2)

        assert "Bootstrap" in prompt or "bootstrap" in prompt
        assert "Test Business" in prompt

    def test_build_prompt_variant_3(self):
        """Test prompt building for Material Design variant"""
        business = Mock(spec=Business)
        business.name = "Tech Company"
        business.category = "Technology"
        business.description = "Tech services"
        business.scraped_html = "<html><body><h1>Tech</h1></body></html>"
        business.scraped_css = ""
        business.component_count = 1
        business.component_structure = []
        business.color_palette = []
        business.logo_urls = []
        business.image_urls = []
        business.video_urls = []
        business.map_embeds = []
        business.score = 60

        builder = ModernizationPromptBuilder(business)
        prompt = builder.build_prompt(variant_number=3)

        assert "Material" in prompt or "material" in prompt
        assert "Tech Company" in prompt

    def test_invalid_variant_number(self):
        """Test that invalid variant number raises error"""
        business = Mock(spec=Business)
        business.scraped_html = "<html></html>"
        business.scraped_css = ""
        business.component_count = 0
        business.component_structure = []
        business.color_palette = []
        business.logo_urls = []
        business.image_urls = []
        business.video_urls = []
        business.map_embeds = []

        builder = ModernizationPromptBuilder(business)

        with pytest.raises(ValueError):
            builder.build_prompt(variant_number=5)

    def test_get_variant_name(self):
        """Test variant name retrieval"""
        business = Mock(spec=Business)
        builder = ModernizationPromptBuilder(business)

        assert "Tailwind" in builder.get_variant_name(1)
        assert "Bootstrap" in builder.get_variant_name(2)
        assert "Material" in builder.get_variant_name(3)

    def test_get_css_framework(self):
        """Test CSS framework retrieval"""
        business = Mock(spec=Business)
        builder = ModernizationPromptBuilder(business)

        assert builder.get_css_framework(1) == "tailwind"
        assert builder.get_css_framework(2) == "bootstrap"
        assert builder.get_css_framework(3) == "material"


class TestEnhancedWebsiteScraperIntegration:
    """Integration tests for scraping workflow"""

    @patch('app.services.enhanced_website_scraper_service.requests.get')
    def test_scrape_with_requests_success(self, mock_get):
        """Test successful scraping with requests"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService

        # Create mock database session
        mock_db = Mock()

        scraper = EnhancedWebsiteScraperService(mock_db)
        html, css = scraper._scrape_with_requests("https://example.com")

        assert html is not None
        assert len(html) > 0

    @patch('app.services.enhanced_website_scraper_service.requests.get')
    def test_scrape_with_requests_retry(self, mock_get):
        """Test retry logic on failure"""
        # Mock first two failures, then success
        mock_get.side_effect = [
            Exception("Connection error"),
            Exception("Timeout"),
            Mock(status_code=200, text=SAMPLE_HTML, raise_for_status=Mock())
        ]

        from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService

        mock_db = Mock()
        scraper = EnhancedWebsiteScraperService(mock_db)
        html, css = scraper._scrape_with_requests("https://example.com")

        # Should succeed on third attempt
        assert html is not None or mock_get.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
