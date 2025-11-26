"""
Test script for ChatGPT HTML Generation - Maximum Quality Mode

This script tests the new ChatGPT-based website generation system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.chatgpt_html_generator import ChatGPTHTMLGenerator
from app.models import Business
from app.config import settings


async def test_chatgpt_generation():
    """Test ChatGPT HTML generation with mock data"""

    print("=" * 80)
    print("TESTING CHATGPT HTML GENERATION - MAXIMUM QUALITY MODE")
    print("=" * 80)

    # Check if OpenAI API key is configured
    if not settings.OPENAI_API_KEY:
        print("❌ ERROR: OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your .env file")
        return False

    print(f"✅ OpenAI API key configured: {settings.mask_secret(settings.OPENAI_API_KEY)}")
    print(f"✅ Model: {settings.CHATGPT_HTML_GENERATION_MODEL}")
    print(f"✅ Temperature: {settings.CHATGPT_HTML_TEMPERATURE}")
    print(f"✅ Max tokens: {settings.CHATGPT_HTML_MAX_TOKENS}")
    print(f"✅ Variants to generate: {settings.CHATGPT_GENERATE_VARIANTS}")
    print()

    # Create a test business
    test_business = Business(
        id="test-123",
        name="Test Electrical Services",
        category="Electrician",
        description="Professional electrical services in Birmingham",
        website_url="https://example-electrician.com",
        phone="0123 456 7890",
        email="info@example-electrician.com",
        address="123 Test Street, Birmingham"
    )

    # Create mock scraped data
    scraped_data = {
        "assets": {
            "logos": [
                {"local_path": "/assets/logo.png", "url": "https://example.com/logo.png"}
            ],
            "images": [
                {"url": "https://example.com/image1.jpg", "alt": "Service image"},
                {"url": "https://example.com/image2.jpg", "alt": "Team photo"}
            ],
            "videos": [],
            "colors": {
                "primary": "#667eea",
                "secondary": "#764ba2",
                "accent": "#f093fb"
            }
        },
        "content": {
            "navbar": {
                "logo": "/assets/logo.png",
                "menu_items": [
                    {"text": "Home", "link": "/"},
                    {"text": "Services", "link": "#services"},
                    {"text": "About", "link": "#about"},
                    {"text": "Contact", "link": "#contact"}
                ]
            },
            "hero": {
                "heading": "Professional Electrical Services",
                "subheadline": "Trusted electricians serving Birmingham since 2010",
                "cta_buttons": [
                    {"text": "Get Free Quote", "link": "#contact"},
                    {"text": "Call Now", "link": "tel:01234567890"}
                ]
            },
            "sections": [
                {
                    "type": "about",
                    "heading": "About Us",
                    "content": "We are a family-run electrical business with over 15 years of experience."
                }
            ],
            "footer": {
                "sections": ["About", "Services", "Contact"],
                "copyright": "© 2024 Test Electrical Services"
            }
        },
        "text_content": {
            "services": [
                {"name": "Domestic Electrical", "description": "All household electrical work"},
                {"name": "Commercial Electrical", "description": "Business electrical services"},
                {"name": "Emergency Callouts", "description": "24/7 emergency repairs"}
            ],
            "testimonials": [
                {"text": "Excellent service!", "author": "John Smith", "rating": 5},
                {"text": "Very professional", "author": "Jane Doe", "rating": 5}
            ]
        },
        "contact": {
            "phone": ["0123 456 7890"],
            "email": ["info@example-electrician.com"],
            "address": "123 Test Street, Birmingham"
        }
    }

    print("📊 Test Business:")
    print(f"   Name: {test_business.name}")
    print(f"   Category: {test_business.category}")
    print(f"   Website: {test_business.website_url}")
    print()

    print("🔧 Mock Scraped Data:")
    print(f"   Logos: {len(scraped_data['assets']['logos'])}")
    print(f"   Images: {len(scraped_data['assets']['images'])}")
    print(f"   Services: {len(scraped_data['text_content']['services'])}")
    print(f"   Testimonials: {len(scraped_data['text_content']['testimonials'])}")
    print()

    print("🚀 Starting ChatGPT HTML generation...")
    print("   This will:")
    print("   1. Generate 3 variants in parallel (gradient, glassmorphism, animation)")
    print("   2. Use AI to validate each variant (0-100 score)")
    print("   3. Select best variant")
    print("   4. Refine with additional GPT-4 call")
    print("   5. Final validation")
    print()
    print("⏳ Please wait... (this may take 1-2 minutes)")
    print()

    try:
        # Initialize generator
        generator = ChatGPTHTMLGenerator()

        # Generate HTML
        html, metadata = await generator.generate_modern_html_maximum_quality(
            business=test_business,
            scraped_data=scraped_data
        )

        print("=" * 80)
        print("✅ GENERATION SUCCESSFUL!")
        print("=" * 80)
        print()
        print("📊 Generation Metadata:")
        print(f"   Method: {metadata['generation_method']}")
        print(f"   Variants generated: {metadata['variants_generated']}")
        print(f"   Best style: {metadata['best_style']}")
        print(f"   Best variant score: {metadata['best_variant_score']}/100")
        print(f"   Final score: {metadata['final_score']}/100")
        print(f"   Quality level: {metadata['quality_level']}")
        print(f"   Total GPT-4 calls: {metadata['total_gpt4_calls']}")
        print(f"   Total tokens used: {metadata['total_tokens_used']:,}")
        print(f"   Estimated cost: ${metadata['estimated_cost']:.2f}")
        print()
        print(f"📄 Generated HTML size: {len(html):,} characters")
        print()

        # Save to file
        output_file = Path(__file__).parent / "test_chatgpt_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"💾 Saved to: {output_file}")
        print()
        print("🎉 You can now open this file in a browser to see the result!")
        print()

        return True

    except Exception as e:
        print("=" * 80)
        print("❌ GENERATION FAILED!")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test"""
    result = asyncio.run(test_chatgpt_generation())
    if result:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
