"""Premium AI Template Generation Service

Enhanced template generation using:
- PremiumTemplateBuilder for guaranteed features
- MediaSourcingService for rich media
- GPT-4 for content enhancement (not HTML generation)
- Business-niche specialization
"""

import logging
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from pathlib import Path

from app.config import settings
from app.models import Business, Template, Evaluation
from app.services.website_scraper import scrape_business_website
from app.services.premium_template_builder import (
    PremiumTemplateBuilder,
    ImageAsset,
    VideoAsset
)
from app.services.media_sourcing_service import MediaSourcingService
# NEW: Intelligence modules from brainstorming session implementation
from app.services.business_classifier import classify_business, get_business_type_display_name
from app.services.content_extractor import extract_business_content, get_fallback_colors
from app.services.gap_analyzer import analyze_website_gaps

logger = logging.getLogger(__name__)

# Configure OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class TemplateGenerationError(Exception):
    """Raised when template generation fails"""
    pass


async def generate_templates_for_business(
    business: Business,
    db: Session,
    num_variants: int = 1,  # Changed default to 1 for premium templates
    use_premium: bool = True
) -> List[Template]:
    """
    Generate premium AI-improved website templates for a business.

    NEW PREMIUM APPROACH:
    1. Classify business type
    2. Fetch premium media (Unsplash images, Pexels videos)
    3. Build structured HTML template programmatically
    4. Enhance content with GPT-4
    5. Inject enhanced content into template
    6. Validate against premium standards

    Args:
        business: Business model instance
        db: Database session
        num_variants: Number of template variants (default 1 for premium)
        use_premium: Use premium generation (True) or legacy (False)

    Returns:
        List of generated Template instances

    Raises:
        TemplateGenerationError: If generation fails
    """
    if not settings.OPENAI_API_KEY:
        raise TemplateGenerationError("OpenAI API key not configured")

    try:
        logger.info(f"Starting premium template generation for business: {business.name}")

        # Step 1: Scrape existing website for content
        scraped_data = {}
        raw_html = ""
        if business.website_url:
            try:
                logger.info(f"Scraping website: {business.website_url}")
                scraped_data = scrape_business_website(business.website_url)
                raw_html = scraped_data.get("raw_html", "")
                logger.info(f"Successfully scraped website content")
            except Exception as e:
                logger.error(f"Error scraping website: {e}")

        # Step 2: INTELLIGENT BUSINESS CLASSIFICATION (NEW)
        classification_result = classify_business(
            category=business.category or "",
            website_text=scraped_data.get("text_content", ""),
            business_name=business.name
        )
        business_type = classification_result["primary_type"]
        confidence = classification_result["confidence"]
        secondary_tags = classification_result["secondary_tags"]

        logger.info(
            f"🎯 Classified as: {get_business_type_display_name(business_type)} "
            f"({confidence:.0%} confidence) {secondary_tags}"
        )

        # Step 3: EXTRACT EXISTING CONTENT (NEW)
        extracted_content = {}
        if raw_html:
            try:
                extracted_content = extract_business_content(
                    html_content=raw_html,
                    base_url=business.website_url,
                    business_phone=business.phone
                )
                logger.info(
                    f"📦 Extracted: {extracted_content['metadata']['total_colors_found']} colors, "
                    f"{len(extracted_content.get('logos', []))} logos, "
                    f"{len(extracted_content.get('images', []))} images"
                )
            except Exception as e:
                logger.error(f"Content extraction failed: {e}")

        # Step 4: GAP ANALYSIS (NEW)
        gap_analysis = {}
        if raw_html:
            try:
                gap_analysis = analyze_website_gaps(
                    html_content=raw_html,
                    business_name=business.name,
                    business_type=business_type
                )
                logger.info(
                    f"🔍 Gap Analysis: {gap_analysis['overall_score']}/100, "
                    f"{len(gap_analysis['priority_gaps'])} priority gaps: {gap_analysis['priority_gaps']}"
                )
            except Exception as e:
                logger.error(f"Gap analysis failed: {e}")

        # Step 3: Source premium media
        media_assets = await _fetch_media_assets(business, business_type)
        logger.info(
            f"Fetched media: {len(media_assets.get('images', []))} images, "
            f"{'video' if media_assets.get('hero_video') else 'no video'}"
        )

        # Step 5: Build enhanced business data dict with intelligence
        business_data = {
            "name": business.name,
            "description": business.description or "",
            "category": business.category or "",
            "services": scraped_data.get("services_menu", []),
            "contact": {
                "phone": extracted_content.get("contact", {}).get("phone") or business.phone or "",
                "email": extracted_content.get("contact", {}).get("email") or business.email or "",
                "address": business.address or ""
            },
            "testimonials": scraped_data.get("testimonials", []),
            "logo": extracted_content.get("logos", [])[0] if extracted_content.get("logos", []) else scraped_data.get("logo", ""),
            "extracted_logos": extracted_content.get("logos", []),  # All extracted logos
            # NEW: Enhanced intelligence data
            "extracted_colors": extracted_content.get("colors", []) or get_fallback_colors(business_type),
            "extracted_text": extracted_content.get("text_content", {}),
            "extracted_images": extracted_content.get("images", []),
            "business_type": business_type,
            "business_type_display": get_business_type_display_name(business_type),
            "classification_confidence": confidence,
            "secondary_tags": secondary_tags,
            "gap_analysis": gap_analysis,
            "priority_improvements": gap_analysis.get("priority_gaps", []),
            "recommendations": gap_analysis.get("recommendations", [])
        }

        # Step 5: Build premium template structure
        builder = PremiumTemplateBuilder(
            business_data=business_data,
            media_assets=media_assets,
            scraped_content=scraped_data
        )

        # Step 6: Apply business-niche specialization
        builder.apply_niche_specialization(business_type)

        # Step 7: Enhance content with GPT-4
        enhanced_content = await _enhance_content_with_gpt4(
            business=business,
            business_type=business_type,
            scraped_data=scraped_data,
            content_placeholders=builder.get_content_placeholders()
        )

        logger.info("Successfully enhanced content with GPT-4")

        # Step 8: Inject enhanced content
        builder.inject_business_content(enhanced_content)

        # Step 9: Generate final HTML
        final_html = builder.build_html_structure()
        logger.info(f"Generated HTML: {len(final_html)} characters")

        # Step 10: Validate premium standards
        validation_errors = builder.validate_premium_standards()
        if validation_errors:
            logger.warning(f"Template validation issues: {validation_errors}")
        else:
            logger.info("✓ Template passed all premium validation checks")

        # Step 11: Save to database with intelligence metadata
        template = Template(
            business_id=business.id,
            variant_number=1,  # Premium templates generate single variant
            html_content=final_html,
            css_content="",  # Inline in HTML
            js_content="",   # Inline in HTML
            media_assets={
                "images": [img.to_dict() if hasattr(img, 'to_dict') else {"url": img.url if hasattr(img, 'url') else str(img)}
                          for img in media_assets.get("images", [])],
                "hero_video": media_assets.get("hero_video").to_dict() if media_assets.get("hero_video") else None,
                # Intelligence data
                "business_type": business_type,
                "business_type_display": get_business_type_display_name(business_type),
                "classification_confidence": confidence,
                "secondary_tags": secondary_tags,
                "extracted_colors": extracted_content.get("colors", [])[:5],
                "extracted_logos": extracted_content.get("logos", [])[:2],
                "gap_analysis_score": gap_analysis.get("overall_score", 0),
                "priority_gaps": gap_analysis.get("priority_gaps", []),
                "recommendations": gap_analysis.get("recommendations", [])[:3],
                "generation_metadata": {
                    "used_intelligent_classification": True,
                    "used_content_extraction": bool(extracted_content),
                    "used_gap_analysis": bool(gap_analysis),
                    "brainstorming_session_date": "2025-11-06"
                }
            },
            generated_at=datetime.utcnow()
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        logger.info(f"✓ Premium template generated successfully for: {business.name}")

        return [template]

    except Exception as e:
        logger.error(f"Premium template generation failed: {str(e)}", exc_info=True)
        raise TemplateGenerationError(f"Failed to generate premium template: {str(e)}")


# Old _classify_business_type function removed - now using intelligent classifier
# from app.services.business_classifier module (Priority #1 implementation)


async def _fetch_media_assets(
    business: Business,
    business_type: str
) -> Dict[str, Any]:
    """
    Fetch premium media assets from Unsplash and Pexels.

    Args:
        business: Business instance
        business_type: Classified business type

    Returns:
        Dict with 'images' and 'hero_video'
    """
    # Check if premium mode is enabled
    if not getattr(settings, 'PREMIUM_TEMPLATE_MODE', True):
        logger.info("Premium mode disabled, using placeholder images")
        media_service = MediaSourcingService()
        return {
            "images": media_service.get_placeholder_images(15, business_type),
            "hero_video": None
        }

    # Initialize media sourcing service
    media_service = MediaSourcingService(
        unsplash_key=getattr(settings, 'UNSPLASH_API_KEY', ''),
        pexels_key=getattr(settings, 'PEXELS_API_KEY', '')
    )

    # Validate API keys
    api_status = media_service.validate_api_keys()
    if not api_status['unsplash']:
        logger.warning("Unsplash API key not configured, using placeholders")

    # Fetch images
    try:
        image_count = getattr(settings, 'DEFAULT_IMAGE_COUNT', 15)
        images = await media_service.get_business_images(
            business_type=business_type,
            business_name=business.name,
            count=image_count
        )
    except Exception as e:
        logger.error(f"Error fetching images: {e}")
        images = media_service.get_placeholder_images(15, business_type)

    # Fetch hero video
    hero_video = None
    if getattr(settings, 'ENABLE_VIDEO_BACKGROUNDS', True):
        try:
            hero_video = await media_service.get_hero_video(
                business_type=business_type,
                min_duration=10,
                max_duration=30
            )
        except Exception as e:
            logger.error(f"Error fetching hero video: {e}")

    return {
        "images": images,
        "hero_video": hero_video
    }


async def _enhance_content_with_gpt4(
    business: Business,
    business_type: str,
    scraped_data: Dict[str, Any],
    content_placeholders: Dict[str, str]
) -> Dict[str, Any]:
    """
    Use GPT-4 to enhance business content quality.

    This does NOT generate HTML - only enhances text content.

    Args:
        business: Business instance
        business_type: Classified business type
        scraped_data: Scraped website content
        content_placeholders: Content sections needing enhancement

    Returns:
        Dict with enhanced content
    """
    if not client:
        logger.warning("OpenAI client not initialized, using basic content")
        return {
            "headline": business.name,
            "subheadline": business.description or "Welcome to our business",
            "value_props": ["Quality Service", "Professional Team", "Customer Satisfaction"],
            "services": [],
            "about": business.description or "We are committed to excellence.",
            "ctas": {
                "primary": "Get Started",
                "secondary": "Learn More",
                "urgent": "Contact Us Today",
                "value": "See How We Can Help",
                "trust": "Free Consultation"
            },
            "meta_description": business.description[:155] if business.description else business.name,
            "testimonials": []
        }

    # Load premium content enhancement prompt
    try:
        prompt_path = Path("app/prompts/premium_content_enhancement.txt")
        if not prompt_path.exists():
            prompt_path = Path(__file__).parent.parent / "prompts" / "premium_content_enhancement.txt"

        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()

        # Load niche-specific prompt if available
        niche_prompt_path = Path(__file__).parent.parent / "prompts" / "niche_templates" / f"{business_type}_template.txt"
        niche_prompt = ""
        if niche_prompt_path.exists():
            with open(niche_prompt_path, "r", encoding="utf-8") as f:
                niche_prompt = f.read()

    except Exception as e:
        logger.error(f"Error loading prompt templates: {e}")
        base_prompt = "Enhance the following business content to be professional and compelling."
        niche_prompt = ""

    # Build prompt with business data
    prompt = base_prompt.format(
        business_name=business.name,
        business_type=business_type,
        business_description=business.description or "",
        scraped_content=json.dumps(scraped_data.get("text_content", "")[:1000]),  # First 1000 chars
        services=json.dumps(scraped_data.get("services_menu", [])[:10]),
        target_audience="general audience"
    )

    # Append niche-specific guidelines
    if niche_prompt:
        prompt += "\n\n" + niche_prompt

    try:
        logger.info(f"Calling GPT-4 for content enhancement")

        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # GPT-4 Turbo
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert copywriter who creates premium, conversion-optimized website content. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )

        enhanced_content = json.loads(response.choices[0].message.content)
        logger.info("Successfully enhanced content with GPT-4")

        return enhanced_content

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT-4 JSON response: {e}")
        # Return basic content
        return {
            "headline": business.name,
            "subheadline": business.description or "Welcome to our business",
            "value_props": ["Quality Service", "Professional Team", "Customer Satisfaction"],
            "services": [],
            "about": business.description or "We are committed to excellence.",
            "ctas": {
                "primary": "Get Started",
                "secondary": "Learn More",
                "urgent": "Contact Us Today",
                "value": "See How We Can Help",
                "trust": "Free Consultation"
            },
            "meta_description": business.description[:155] if business.description else business.name,
            "testimonials": []
        }

    except Exception as e:
        logger.error(f"Error calling GPT-4 API: {e}", exc_info=True)
        raise TemplateGenerationError(f"GPT-4 content enhancement failed: {str(e)}")


def _build_business_context(business: Business, evaluation: Evaluation = None) -> Dict[str, Any]:
    """
    Build context dictionary for template generation.

    (Kept for backwards compatibility with legacy code)
    """
    context = {
        "name": business.name,
        "category": business.category or "General Business",
        "location": business.location or "Unknown",
        "description": business.description or f"A {business.category or 'business'} in {business.location or 'your area'}",
        "website_url": business.website_url,
        "phone": business.phone,
        "email": business.email,
        "address": business.address,
    }

    if evaluation:
        context["evaluation"] = {
            "performance_score": evaluation.performance_score,
            "seo_score": evaluation.seo_score,
            "accessibility_score": evaluation.accessibility_score,
            "aggregate_score": evaluation.aggregate_score,
        }

    return context


# Export main function
__all__ = ['generate_templates_for_business', 'TemplateGenerationError']
