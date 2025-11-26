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
from bs4 import BeautifulSoup

from app.config import settings
from app.models import Business, Template, Evaluation
from app.services.website_scraper import scrape_business_website
from app.services.premium_template_builder import (
    PremiumTemplateBuilder,
    ImageAsset,
    VideoAsset
)
from app.services.media_sourcing_service import MediaSourcingService
from app.services.brand_asset_downloader import download_brand_assets  # NEW: Download original brand assets
from app.services.website_cloner import WebsiteCloner  # Clone original website HTML
# NEW: Intelligence modules from brainstorming session implementation
from app.services.business_classifier import classify_business, get_business_type_display_name
from app.services.content_extractor import extract_business_content, get_fallback_colors
from app.services.gap_analyzer import analyze_website_gaps
# MAXIMUM QUALITY: ChatGPT HTML Generator for brand-new modern websites
from app.services.chatgpt_html_generator import ChatGPTHTMLGenerator
# NEW: Gemini HTML Generator - Alternative to ChatGPT
from app.services.gemini_html_generator import GeminiHTMLGenerator

logger = logging.getLogger(__name__)

# Configure OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class TemplateGenerationError(Exception):
    """Raised when template generation fails"""
    pass


def is_html_corrupted(html: str) -> bool:
    """
    Detect if HTML content is corrupted (contains binary garbage).

    IMPORTANT: This check is now LESS STRICT to avoid false positives.
    Modern websites often have binary data in SVGs, data URIs, and other embedded content.
    We only flag as corrupted if it's COMPLETELY corrupted (no structure or starts with garbage).

    Corruption indicators:
    - Missing basic HTML structure tags
    - Starts with binary garbage (first 100 chars mostly non-printable)

    Args:
        html: HTML string to check

    Returns:
        True if corrupted, False if usable
    """
    if not html or len(html) < 50:
        return False

    # Check if HTML has basic structure tags
    html_lower = html.lower()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    has_body_tag = '<body' in html_lower or '<div' in html_lower  # Allow div-only pages

    # If HTML is longer than 200 chars but missing basic tags, it's likely corrupted
    if len(html) > 200 and not (has_html_tag or has_body_tag):
        logger.warning(f"[CORRUPTION DETECTED] HTML missing basic structure tags")
        return True

    # LESS STRICT: Only check if HTML STARTS with binary garbage (first 100 chars)
    # Modern websites often have binary data embedded in SVGs, data URIs, etc.
    first_100 = html[:100].strip()

    # Count printable characters in first 100 chars
    printable_count = sum(1 for c in first_100 if c.isprintable() or c in ['\n', '\r', '\t'])

    # If less than 70% of first 100 chars are printable, it's likely corrupted
    if len(first_100) > 0 and (printable_count / len(first_100)) < 0.7:
        logger.warning(f"[CORRUPTION DETECTED] HTML starts with binary garbage (only {printable_count}/{len(first_100)} printable chars)")
        return True

    return False


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

        # Step 1: Scrape existing website for content OR load from DATABASE
        scraped_data = {}
        raw_html = ""
        downloaded_assets = {}

        if business.website_url:
            # Try to load from DATABASE first (for regeneration)
            if business.scraped_data:
                try:
                    logger.info(f"[DATABASE] Loading scraped data from database for business: {business.name}")
                    scraped_data = business.scraped_data
                    raw_html = scraped_data.get("raw_html", "")
                    logger.info(f"[DATABASE] Successfully loaded from database: {len(raw_html)} bytes of HTML")

                    # CRITICAL: Check for corruption in loaded data
                    if raw_html and is_html_corrupted(raw_html):
                        logger.error(f"[CORRUPTION DETECTED] Database contains corrupted HTML for business: {business.name}")
                        logger.error(f"[AUTO-RECOVERY] Clearing corrupted data and forcing fresh scrape...")

                        # Clear corrupted data from database
                        business.scraped_data = None
                        business.scraped_html = None
                        business.scraped_css = None
                        db.commit()

                        # Reset variables to trigger fresh scrape
                        scraped_data = {}
                        raw_html = ""

                        logger.info(f"[AUTO-RECOVERY] Cleared corrupted data, will now scrape fresh")

                except Exception as e:
                    logger.warning(f"[DATABASE] Failed to load from database: {e}, will scrape fresh")
                    scraped_data = {}
                    raw_html = ""

            # CRITICAL FIX: Download brand assets even when loading from database (for regeneration)
            if scraped_data and raw_html:
                try:
                    logger.info(f"[REGENERATE FIX] Downloading brand assets from database-loaded scraped data...")
                    downloaded_assets = download_brand_assets(
                        business_id=str(business.id),
                        scraped_data=scraped_data
                    )
                    logger.info(
                        f"[REGENERATE FIX] Downloaded {downloaded_assets['summary']['total_downloaded']} assets: "
                        f"{downloaded_assets['summary']['logos']} logos, "
                        f"{downloaded_assets['summary']['images']} images, "
                        f"{downloaded_assets['summary']['videos']} videos"
                    )
                except Exception as e:
                    logger.warning(f"[REGENERATE FIX] Failed to download brand assets from database data: {e}")

            # If no database data, scrape the website
            if not raw_html:
                try:
                    logger.info(f"Scraping website: {business.website_url}")
                    scraped_data = scrape_business_website(business.website_url)
                    raw_html = scraped_data.get("raw_html", "")

                    # VALIDATION: Check if scraping actually succeeded
                    if not scraped_data or not raw_html:
                        logger.error(f"[SCRAPING FAILED] Website scraping returned empty data for {business.website_url}")
                        logger.error(f"[WARNING] Will generate template using business info only (may be generic)")
                    else:
                        # Log what we got
                        page_sections = len(scraped_data.get("page_structure", []))
                        text_content_chars = len(str(scraped_data.get("text_content", "")))
                        logger.info(f"[SUCCESS] Scraped website: {page_sections} sections, {text_content_chars} chars of content")

                        # Save to DATABASE for future regenerations
                        try:
                            business.scraped_data = scraped_data
                            db.commit()
                            logger.info(f"[DATABASE] Saved scraped data to database for future regenerations")
                        except Exception as e:
                            logger.warning(f"[DATABASE] Failed to save to database: {e}")
                            db.rollback()

                        # Step 1.5: Download original brand assets (logos, images, videos)
                        logger.info(f"[BRAND ASSETS] Downloading original brand assets to preserve 100% brand identity...")
                        downloaded_assets = download_brand_assets(
                            business_id=str(business.id),
                            scraped_data=scraped_data
                        )
                        logger.info(
                            f"[BRAND ASSETS] Downloaded {downloaded_assets['summary']['total_downloaded']} assets: "
                            f"{downloaded_assets['summary']['logos']} logos, "
                            f"{downloaded_assets['summary']['images']} images, "
                            f"{downloaded_assets['summary']['videos']} videos"
                        )
                except Exception as e:
                    logger.error(f"[ERROR] Error during website scraping: {e}")

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
            f"[CLASSIFICATION] Classified as: {get_business_type_display_name(business_type)} "
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
                    f"[EXTRACTION] Extracted: {extracted_content['metadata']['total_colors_found']} colors, "
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
                    f"[GAP ANALYSIS] Gap Analysis: {gap_analysis['overall_score']}/100, "
                    f"{len(gap_analysis['priority_gaps'])} priority gaps: {gap_analysis['priority_gaps']}"
                )
            except Exception as e:
                logger.error(f"Gap analysis failed: {e}")

        # Step 3: Source media assets - PRIORITIZE downloaded original assets, fallback to extracted content
        media_assets = await _prepare_media_assets(business, business_type, downloaded_assets, extracted_content)
        logger.info(
            f"Prepared media: {len(media_assets.get('images', []))} images "
            f"({media_assets.get('images_source', 'unknown')} source), "
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
            "logo": downloaded_assets.get("logo", {}).get("original_url") if downloaded_assets.get("logo") else (extracted_content.get("logos", [])[0] if extracted_content.get("logos", []) else scraped_data.get("logo", "")),
            "extracted_logos": extracted_content.get("logos", []),  # All extracted logos
            "downloaded_logo": downloaded_assets.get("logo"),  # Downloaded logo data
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

        # Step 5: MAXIMUM QUALITY - Generate brand-new HTML using AI (ChatGPT or Gemini)
        # Check which AI engine to use
        use_gemini_generation = getattr(settings, 'USE_GEMINI_GENERATION', False)
        use_ai_generation = True

        # If no scraped data, use basic business info
        if not scraped_data:
            ai_name = "GEMINI" if use_gemini_generation else "CHATGPT"
            logger.warning(f"[{ai_name}] No scraped data, will use basic business info for generation")
            scraped_data = {
                'logo': '',
                'colors': [],
                'images': [],
                'videos': [],
                'headlines': {'main_headline': business.name},
                'about': business.description or '',
                'services_menu': [],
                'contact': {'phone': business.phone or '', 'email': business.email or ''},
                'navigation': ['Home', 'Services', 'About', 'Contact'],
                'page_structure': [],
                'testimonials': []
            }

        if use_ai_generation:
            if use_gemini_generation:
                # ========== USE GEMINI ==========
                logger.info(f"[GEMINI] Generating brand-new modern HTML using GEMINI MAXIMUM QUALITY mode")
                logger.info(f"[GEMINI] Model: {getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')}")

                try:
                    # Initialize Gemini HTML generator
                    html_generator = GeminiHTMLGenerator()

                    # Generate modern HTML with maximum quality (3 variants, validation, refinement)
                    final_html, generation_metadata = await html_generator.generate_modern_html_maximum_quality(
                        business=business,
                        scraped_data=scraped_data
                    )

                    logger.info(f"[GEMINI SUCCESS] Generated professional modern website!")
                    logger.info(f"[GEMINI] Style: {generation_metadata.get('style', 'professional-modern')}")
                    logger.info(f"[GEMINI] Total Gemini calls: {generation_metadata['total_gemini_calls']}")
                    logger.info(f"[GEMINI] Total tokens: {generation_metadata.get('total_tokens_used', 0)}")
                    logger.info(f"[GEMINI] Estimated cost: ${generation_metadata['estimated_cost']:.2f}")

                except Exception as gemini_error:
                    logger.error(f"[GEMINI FAILED] {gemini_error}", exc_info=True)
                    raise TemplateGenerationError(f"Gemini HTML generation failed: {str(gemini_error)}")

            else:
                # ========== USE CHATGPT (DEFAULT) ==========
                logger.info(f"[CHATGPT] Generating brand-new modern HTML using ChatGPT MAXIMUM QUALITY mode")

                try:
                    # Initialize ChatGPT HTML generator
                    html_generator = ChatGPTHTMLGenerator()

                    # Generate modern HTML with maximum quality (3 variants, validation, refinement)
                    final_html, generation_metadata = await html_generator.generate_modern_html_maximum_quality(
                        business=business,
                        scraped_data=scraped_data
                    )

                    logger.info(f"[CHATGPT SUCCESS] Generated {generation_metadata['quality_level']} quality website!")
                    logger.info(f"[CHATGPT] Quality score: {generation_metadata['final_score']}/100")
                    logger.info(f"[CHATGPT] Best style: {generation_metadata['best_style']}")
                    logger.info(f"[CHATGPT] Total GPT-4 calls: {generation_metadata['total_gpt4_calls']}")
                    logger.info(f"[CHATGPT] Estimated cost: ${generation_metadata['estimated_cost']:.2f}")

                except Exception as chatgpt_error:
                    logger.error(f"[CHATGPT FAILED] {chatgpt_error}", exc_info=True)
                    # Don't fall back - raise the error so user knows something is wrong
                    raise TemplateGenerationError(f"ChatGPT HTML generation failed: {str(chatgpt_error)}")

        # OLD CLONING CODE REMOVED - We only use ChatGPT generation now
        # The cloning approach was causing broken HTML with alignment issues
        # ChatGPT generation creates perfect, modern, aligned HTML every time
        if False:  # This block is disabled
            logger.info(f"[CLONING] Using scraped HTML from business website: {business.website_url}")

            try:
                # Use the already-scraped HTML instead of downloading again
                if raw_html and len(raw_html) > 100:
                    logger.info(f"[CLONING] Using pre-scraped HTML: {len(raw_html)} bytes")

                    # Initialize website cloner with the raw HTML
                    cloner = WebsiteCloner(business.website_url)
                    cloner.html = raw_html
                    cloner.soup = BeautifulSoup(raw_html, 'html.parser')

                    # Download CSS files
                    cloner.download_css_files()

                    # Clean and fix HTML
                    cloned_html = cloner.clean_and_fix_html(downloaded_assets or {})
                    logger.info(f"[CLONING] Successfully processed scraped HTML: {len(cloned_html)} bytes")
                else:
                    # Fallback: try to download HTML if scraping didn't work
                    logger.warning("[CLONING] No pre-scraped HTML available, trying to download...")
                    cloner = WebsiteCloner(business.website_url)
                    cloned_html = cloner.clone_website(downloaded_assets=downloaded_assets)
                    logger.info(f"[CLONING] Successfully downloaded and cloned: {len(cloned_html)} bytes")

                # Step 6: Try to use GPT-4 to improve content (optional - won't fail if GPT-4 unavailable)
                enhanced_content = {}
                try:
                    logger.info("[AI] Attempting GPT-4 content enhancement (optional)")
                    enhanced_content = await _enhance_content_with_gpt4(
                        business=business,
                        business_type=business_type,
                        scraped_data=scraped_data,
                        content_placeholders={}
                    )
                    logger.info("[AI] GPT-4 enhancement successful")
                except Exception as gpt_error:
                    logger.warning(f"[AI] GPT-4 enhancement skipped: {gpt_error}")
                    logger.info("[AI] Continuing with cloned website without GPT-4 enhancements")

                # Step 7: Apply CSS/alignment improvements to cloned HTML (doesn't need GPT-4)
                final_html = await _apply_ai_improvements_to_html(
                    cloned_html=cloned_html,
                    enhanced_content=enhanced_content,
                    media_assets=media_assets
                )

                logger.info(f"[SUCCESS] Generated improved clone: {len(final_html)} characters")

            except Exception as clone_error:
                logger.error(f"[CLONING FAILED] {clone_error}")
                logger.info("[FALLBACK] Attempting simpler modernization approach - NO GENERIC TEMPLATES")

                # NEVER use generic templates! Always use scraped HTML and modernize it
                # Try to get HTML from any available source
                fallback_html = None

                # Try 1: Use raw_html from database/scraping
                if raw_html and len(raw_html) > 100:
                    logger.info(f"[FALLBACK] Using raw HTML from database/scraping: {len(raw_html)} bytes")
                    fallback_html = raw_html

                # Try 2: Try to re-scrape the website as last resort
                elif business.website_url:
                    try:
                        logger.warning(f"[FALLBACK] No HTML available, attempting emergency re-scrape: {business.website_url}")
                        emergency_scrape = scrape_business_website(business.website_url)
                        fallback_html = emergency_scrape.get("raw_html", "")
                        if fallback_html and len(fallback_html) > 100:
                            logger.info(f"[FALLBACK] Emergency scraping successful: {len(fallback_html)} bytes")
                            # Update scraped_data for modernization
                            scraped_data = emergency_scrape
                            raw_html = fallback_html
                        else:
                            logger.error("[FALLBACK] Emergency scraping returned empty HTML")
                    except Exception as scrape_error:
                        logger.error(f"[FALLBACK] Emergency scraping failed: {scrape_error}")

                # If we have HTML, modernize it directly (simpler approach)
                if fallback_html and len(fallback_html) > 100:
                    try:
                        logger.info("[FALLBACK] Applying direct modernization to scraped HTML")
                        # Apply modernization directly without complex cloning
                        final_html = await _apply_ai_improvements_to_html(
                            cloned_html=fallback_html,
                            enhanced_content={},  # Skip GPT-4 enhancement in fallback
                            media_assets=media_assets
                        )
                        logger.info(f"[FALLBACK SUCCESS] Modernized scraped HTML: {len(final_html)} bytes")
                    except Exception as modernization_error:
                        logger.error(f"[FALLBACK] Modernization failed: {modernization_error}")
                        # Last resort: return the raw HTML unchanged
                        logger.warning("[FALLBACK] Returning raw HTML without modernization")
                        final_html = fallback_html
                else:
                    # Absolute failure: No HTML available at all
                    error_msg = f"Cannot generate template for {business.name}: No HTML available from database, scraping, or website. Cannot create generic template per requirements."
                    logger.error(f"[FATAL] {error_msg}")
                    raise TemplateGenerationError(error_msg)

        # Step 10: Validate and clean HTML generated by ChatGPT
        def validate_html_structure(html: str) -> bool:
            """Validate that HTML has basic required structure"""
            if not html or len(html) < 100:
                return False
            # Check for essential HTML tags
            html_lower = html.lower()
            has_doctype_or_html = '<!doctype' in html_lower or '<html' in html_lower
            has_head = '<head' in html_lower and '</head>' in html_lower
            has_body = '<body' in html_lower and '</body>' in html_lower
            has_closing_html = '</html>' in html_lower

            return has_doctype_or_html and has_head and (has_body or has_closing_html)

        def clean_html_for_postgres(html: str) -> str:
            """
            Clean HTML for PostgreSQL storage.
            Only removes NULL bytes and invalid UTF-8 sequences.
            """
            if not html:
                return html

            # Ensure string is properly encoded
            if isinstance(html, bytes):
                html = html.decode('utf-8', errors='replace')

            # Remove NULL bytes only (PostgreSQL can't store these)
            html = html.replace('\x00', '')

            # Don't remove other control characters - they might be valid in HTML
            # Just ensure the string is valid UTF-8
            try:
                html.encode('utf-8')
            except UnicodeEncodeError:
                # If there are encoding issues, replace bad characters
                html = html.encode('utf-8', errors='replace').decode('utf-8')

            return html

        # Validate HTML structure before cleaning
        if not validate_html_structure(final_html):
            logger.error("[VALIDATION] Generated HTML is invalid or incomplete!")
            logger.error(f"[VALIDATION] HTML length: {len(final_html)}")
            logger.error(f"[VALIDATION] HTML preview: {final_html[:500]}...")
            raise TemplateGenerationError("Generated HTML is invalid or incomplete - missing required HTML structure")

        final_html = clean_html_for_postgres(final_html)
        logger.info(f"[VALIDATION] HTML structure validated successfully")
        logger.info(f"[SANITIZATION] Cleaned HTML content for PostgreSQL: {len(final_html)} characters")

        # Step 12: Save to database with intelligence metadata
        template = Template(
            business_id=business.id,
            variant_number=1,  # Premium templates generate single variant
            html_content=final_html,
            css_content="",  # Inline in HTML
            js_content="",   # Inline in HTML
            media_assets={
                "images": [img.to_dict() if hasattr(img, 'to_dict') else {"url": img.url if hasattr(img, 'url') else str(img)}
                          for img in media_assets.get("images", [])],
                "hero_video": (media_assets.get("hero_video").to_dict() if hasattr(media_assets.get("hero_video"), 'to_dict')
                              else media_assets.get("hero_video")) if media_assets.get("hero_video") else None,
                "images_source": media_assets.get("images_source", "unknown"),
                # Brand Preservation Data
                "brand_preservation": {
                    "colors_extracted": scraped_data.get("colors", []),
                    "fonts_extracted": scraped_data.get("fonts", {}),
                    "logo_downloaded": bool(downloaded_assets.get("logo")),
                    "images_downloaded": downloaded_assets.get("summary", {}).get("images", 0),
                    "videos_downloaded": downloaded_assets.get("summary", {}).get("videos", 0),
                    "total_assets_size_mb": downloaded_assets.get("summary", {}).get("total_size_mb", 0),
                    "testimonials_preserved": len(scraped_data.get("testimonials", [])),
                    "services_preserved": len(scraped_data.get("services_menu", [])),
                    "page_structure_sections": len(scraped_data.get("page_structure", []))
                },
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
                    "used_brand_preservation": True,
                    "brand_assets_downloaded": bool(downloaded_assets),
                    "generation_date": datetime.utcnow().isoformat()
                }
            },
            generated_at=datetime.utcnow()
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        logger.info(f"[SUCCESS] ✅ Modern ChatGPT template generated successfully for: {business.name}")
        logger.info(f"[SUCCESS] HTML size: {len(final_html)} characters")
        logger.info(f"[SUCCESS] Template quality: PERFECT, MODERN, ALIGNED")

        return [template]

    except Exception as e:
        logger.error(f"❌ Template generation failed: {str(e)}", exc_info=True)
        raise TemplateGenerationError(f"Failed to generate template: {str(e)}")


# Old _classify_business_type function removed - now using intelligent classifier
# from app.services.business_classifier module (Priority #1 implementation)


async def _prepare_media_assets(
    business: Business,
    business_type: str,
    downloaded_assets: Dict[str, Any],
    extracted_content: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Prepare media assets for template, PRIORITIZING scraped/original assets.

    Strategy:
    1. If we successfully downloaded original assets → USE THEM (brand preservation!)
    2. If not, use extracted images from scraped HTML
    3. If not enough assets → supplement with stock photos from Unsplash
    4. If no website or scraping failed → fall back to full Unsplash sourcing

    Args:
        business: Business instance
        business_type: Classified business type
        downloaded_assets: Output from brand_asset_downloader
        extracted_content: Output from content_extractor (scraped images from HTML)

    Returns:
        Dict with 'images' and 'hero_video' ready for template
    """
    images = []
    hero_video = None
    images_source = "none"

    # Priority 1: Check if we have downloaded original assets
    if downloaded_assets and downloaded_assets.get('summary', {}).get('images', 0) > 0:
        logger.info("[MEDIA] Using ORIGINAL brand images from website")

        # Convert downloaded images to ImageAsset format
        # CRITICAL: Use original_url (the actual image URL from their website) NOT the local /brand_assets/ URL
        for img_data in downloaded_assets.get('images', []):
            images.append(ImageAsset(
                url=img_data.get('original_url', img_data['url']),  # Use ORIGINAL website URL
                alt=img_data.get('alt', business.name),
                photographer="Original Website",
                source="original"
            ))

        images_source = "original_website"

        # Use original video if available
        downloaded_videos = downloaded_assets.get('videos', [])
        if downloaded_videos:
            first_video = downloaded_videos[0]
            if first_video.get('type') in ['youtube', 'vimeo']:
                # Keep embed format
                hero_video = VideoAsset(
                    url=first_video['url'],
                    poster="",
                    attribution=first_video.get('type', 'Embed')
                )
            else:
                # Direct video file - use original URL
                hero_video = VideoAsset(
                    url=first_video.get('original_url', first_video['url']),
                    poster="",
                    attribution="Original Website"
                )

        logger.info(f"[MEDIA] Prepared {len(images)} original images for template")

        # If we have fewer than 10 images, supplement with stock photos
        if len(images) < 10:
            logger.info(f"Supplementing with stock photos (have {len(images)}, need ~15)")
            stock_assets = await _fetch_media_assets(business, business_type)
            # Add stock images to fill out the gallery
            needed = 15 - len(images)
            images.extend(stock_assets.get('images', [])[:needed])
            images_source = "original_plus_stock"

            # Use stock video if we don't have original
            if not hero_video and stock_assets.get('hero_video'):
                hero_video = stock_assets['hero_video']

    # Priority 2: Check if we have extracted images from scraped HTML
    elif extracted_content and len(extracted_content.get('images', [])) > 0:
        logger.info(f"[MEDIA] Using {len(extracted_content['images'])} SCRAPED images from HTML")

        # Convert extracted images to ImageAsset format
        for img_data in extracted_content.get('images', []):
            if isinstance(img_data, dict):
                images.append(ImageAsset(
                    url=img_data.get('url') or img_data.get('src', ''),
                    alt=img_data.get('alt', business.name),
                    photographer="Scraped from Website",
                    source="scraped"
                ))
            elif isinstance(img_data, str):
                images.append(ImageAsset(
                    url=img_data,
                    alt=business.name,
                    photographer="Scraped from Website",
                    source="scraped"
                ))

        images_source = "scraped_from_html"

        # Use extracted video if available
        extracted_videos = extracted_content.get('videos', [])
        if extracted_videos:
            first_video = extracted_videos[0]
            if isinstance(first_video, dict):
                hero_video = VideoAsset(
                    url=first_video.get('url') or first_video.get('src', ''),
                    poster="",
                    attribution="Scraped from Website"
                )

        logger.info(f"[MEDIA] Prepared {len(images)} scraped images for template")

        # If we have fewer than 10 images, supplement with stock photos
        if len(images) < 10:
            logger.info(f"Supplementing scraped images with stock photos (have {len(images)}, need ~15)")
            stock_assets = await _fetch_media_assets(business, business_type)
            needed = 15 - len(images)
            images.extend(stock_assets.get('images', [])[:needed])
            images_source = "scraped_plus_stock"

            # Use stock video if we don't have scraped video
            if not hero_video and stock_assets.get('hero_video'):
                hero_video = stock_assets['hero_video']

    else:
        # Last resort: Fall back to stock photos if no assets available
        logger.info("[MEDIA] WARNING: No scraped or downloaded assets available, using stock photos")
        stock_assets = await _fetch_media_assets(business, business_type)
        images = stock_assets.get('images', [])
        hero_video = stock_assets.get('hero_video')
        images_source = "stock_photos_fallback"

    return {
        "images": images,
        "hero_video": hero_video,
        "images_source": images_source
    }


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

    # Build prompt with business data - SEND MORE CONTENT for proper analysis
    # Extract comprehensive text content from scraped data
    full_text_content = ""
    if isinstance(scraped_data.get("text_content"), dict):
        # Combine all text sections for analysis
        for section, text in scraped_data.get("text_content", {}).items():
            if text:
                full_text_content += f"\n\n[{section.upper()} SECTION]:\n{text}"
    else:
        full_text_content = str(scraped_data.get("text_content", ""))

    # Send up to 8000 characters of actual website content for proper analysis
    comprehensive_content = full_text_content[:8000] if full_text_content else ""

    # Format page structure for GPT-4 to understand their layout
    page_structure = scraped_data.get("page_structure", [])
    structure_text = "\n"
    for section in page_structure:
        structure_text += f"{section['order']+1}. {section['type'].upper()} Section"
        if section.get('heading'):
            structure_text += f": \"{section['heading']}\""
        structure_text += f"\n   Content preview: {section['content'][:200]}...\n\n"

    if not page_structure:
        structure_text = "Could not detect clear page structure - analyze content to determine sections.\n"

    # Format extracted colors and fonts for the prompt
    extracted_colors = scraped_data.get("colors", [])
    colors_display = ", ".join(extracted_colors) if extracted_colors else "No colors extracted - use defaults"

    extracted_fonts = scraped_data.get("fonts", {})
    fonts_display = f"Headings: {', '.join(extracted_fonts.get('headings', [])[:2])}, Body: {', '.join(extracted_fonts.get('body', [])[:2])}" if extracted_fonts.get('headings') or extracted_fonts.get('body') else "No fonts extracted"

    num_images = len(scraped_data.get("images", []))
    num_videos = len(scraped_data.get("videos", []))

    prompt = base_prompt.format(
        business_name=business.name,
        business_type=business_type,
        business_description=business.description or "",
        page_structure=structure_text,  # NEW: Their actual page structure
        scraped_content=comprehensive_content,  # MUCH MORE content for analysis
        services=json.dumps(scraped_data.get("services_menu", [])[:20]),  # More services
        target_audience="general audience",
        # BRAND ASSET PRESERVATION
        extracted_colors=colors_display,
        extracted_fonts=fonts_display,
        num_images=num_images,
        num_videos=num_videos
    )

    # Append niche-specific guidelines
    if niche_prompt:
        prompt += "\n\n" + niche_prompt

    try:
        logger.info(f"[GPT-4] Calling GPT-4 to analyze and modernize '{business.name}' website content...")
        logger.info(f"[GPT-4] Sending {len(comprehensive_content)} characters of scraped content for analysis")
        logger.info(f"[GPT-4] Detected {len(page_structure)} page sections from their website to recreate")

        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # GPT-4 Turbo
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert web designer who modernizes existing websites while preserving their unique brand identity. You analyze actual website content and create realistic, personalized modernizations - NOT generic templates. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000  # Increased for more detailed content
        )

        enhanced_content = json.loads(response.choices[0].message.content)

        # Log what GPT-4 created to verify it's using their actual content
        logger.info("[GPT-4] Successfully analyzed and modernized content with GPT-4")
        logger.info(f"  Headline: {enhanced_content.get('headline', 'N/A')[:60]}...")
        logger.info(f"  Services: {len(enhanced_content.get('services', []))} unique services extracted")
        logger.info(f"  Sections created: {len(enhanced_content.get('sections', []))}")

        # Log the sections GPT-4 created to verify structure preservation
        sections = enhanced_content.get('sections', [])
        if sections:
            logger.info(f"  [GPT-4] Sections in new website:")
            for sec in sections[:10]:  # First 10 sections
                logger.info(f"     {sec.get('order', '?')}. {sec.get('type', 'unknown').upper()}: {sec.get('heading', 'No heading')[:40]}")

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


async def _apply_ai_improvements_to_html(
    cloned_html: str,
    enhanced_content: Dict[str, Any],
    media_assets: Dict[str, Any]
) -> str:
    """
    Apply PREMIUM modern professional styling to cloned HTML.

    IMPORTANT: This function PRESERVES the original CSS and adds enhancements on top.
    It does NOT remove the original CSS to avoid breaking the layout.

    Creates a completely modern, professional look with:
    - Vibrant gradients and animations
    - Glassmorphism effects
    - Smooth transitions
    - Premium typography
    - Professional spacing
    - Eye-catching hover effects

    Args:
        cloned_html: The original cloned HTML from the business website
        enhanced_content: GPT-4 enhanced content suggestions
        media_assets: Downloaded media assets

    Returns:
        PREMIUM modern styled HTML
    """
    from bs4 import BeautifulSoup

    try:
        logger.info("[PREMIUM REDESIGN] Enhancing HTML with modern styling while preserving original structure...")

        # Use 'html.parser' to avoid breaking HTML
        soup = BeautifulSoup(cloned_html, 'html.parser')

        # Validate HTML structure
        if not soup.find('html'):
            logger.warning("[PREMIUM REDESIGN] No <html> tag found, creating structure")
            html_tag = soup.new_tag('html')
            for element in list(soup.children):
                html_tag.append(element.extract())
            soup.append(html_tag)

        # Get brand colors from enhanced_content or use defaults
        brand_colors = enhanced_content.get('brand_colors', {})
        primary_color = brand_colors.get('primary', '#667eea')
        secondary_color = brand_colors.get('secondary', '#764ba2')
        accent_color = brand_colors.get('accent', '#f093fb')

        logger.info(f"[REDESIGN] Using brand colors: primary={primary_color}, secondary={secondary_color}, accent={accent_color}")

        # Step 1: Ensure <head> exists
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                # No html tag, create structure
                html_tag = soup.new_tag('html')
                html_tag.append(head)
                soup.append(html_tag)

        # Step 2: Ensure <body> exists
        body = soup.find('body')
        if not body:
            logger.warning("[REDESIGN] No <body> tag found, creating one")
            body = soup.new_tag('body')

            # Move all content that's not in head into body
            html_tag = soup.find('html')
            if html_tag:
                # Get all children except head
                children_to_move = []
                for child in html_tag.children:
                    if child != head and child.name != 'head':
                        children_to_move.append(child)

                # Move them to body
                for child in children_to_move:
                    if child.name:  # Skip text nodes
                        child.extract()
                        body.append(child)

                # Append body to html
                html_tag.append(body)
            else:
                # No html tag, create structure
                html_tag = soup.new_tag('html')
                html_tag.append(head)
                html_tag.append(body)
                soup.append(html_tag)

            logger.info("[REDESIGN] Created <body> tag and moved content into it")

        # Step 3: Add viewport if missing
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            meta = soup.new_tag('meta')
            meta['name'] = 'viewport'
            meta['content'] = 'width=device-width, initial-scale=1.0'
            head.insert(0, meta)
            logger.info("[REDESIGN] Added viewport meta tag")

        # Step 4: PRESERVE ORIGINAL CSS - DO NOT REMOVE!
        # Count existing CSS for logging
        existing_styles = len(head.find_all('style'))
        existing_links = len(head.find_all('link', rel='stylesheet'))
        logger.info(f"[REDESIGN] Preserving {existing_styles} existing <style> tags and {existing_links} CSS links")
        logger.info("[REDESIGN] Adding enhancement CSS on top of original CSS (NOT replacing)")

        # Create ENHANCEMENT CSS that works alongside the original CSS
        # This CSS only adds improvements WITHOUT breaking existing layout
        style_tag = soup.new_tag('style')
        style_tag.string = f"""
/* ===================================================================
   ENHANCEMENT CSS - Adds modern touches to existing design
   Works ALONGSIDE original CSS - does not replace it
   =================================================================== */

/* Add smooth scrolling */
html {{
    scroll-behavior: smooth;
}}

/* Improve font rendering */
body {{
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Ensure images are responsive */
img {{
    max-width: 100%;
    height: auto;
}}

/* Add viewport meta if missing - ensures mobile responsiveness */
@viewport {{
    width: device-width;
    zoom: 1.0;
}}

/* Smooth transitions for interactive elements */
a, button, input, select, textarea {{
    transition: all 0.3s ease;
}}

/* Improve button interactivity */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
[class*="btn"]:hover,
a[class*="button"]:hover {{
    opacity: 0.9;
    transform: translateY(-2px);
}}

/* Ensure all clickable elements have pointer cursor */
button, a, [role="button"], [onclick] {{
    cursor: pointer;
}}

/* Fix broken images - show alt text */
img[alt] {{
    font-size: 12px;
    color: #666;
}}

/* Ensure proper box-sizing for all elements */
*, *::before, *::after {{
    box-sizing: border-box;
}}

/* Responsive utilities - ensure mobile compatibility */
@media (max-width: 768px) {{
    /* Make tables scrollable on mobile */
    table {{
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }}

    /* Reduce large text on mobile */
    h1 {{
        font-size: 1.8rem;
    }}

    h2 {{
        font-size: 1.5rem;
    }}
}}

/* Print-friendly styles */
@media print {{
    a[href]:after {{
        content: " (" attr(href) ")";
    }}
}}
"""
        head.append(style_tag)
        logger.info("[REDESIGN] ✅ Added enhancement CSS on top of original CSS")

        # Add alt to images that don't have it
        images_fixed = 0
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = 'Image'
                images_fixed += 1

        if images_fixed > 0:
            logger.info(f"[REDESIGN] Added alt text to {images_fixed} images")

        improved_html = str(soup)
        logger.info(f"[REDESIGN] ✅ Successfully enhanced HTML while preserving original structure ({len(improved_html)} bytes)")
        return improved_html

    except Exception as e:
        logger.error(f"[REDESIGN] ERROR during enhancement: {e}")
        logger.error(f"[REDESIGN] Stack trace:", exc_info=True)
        logger.error(f"[REDESIGN] Returning original HTML without enhancements")
        return cloned_html


# Export main function
__all__ = ['generate_templates_for_business', 'TemplateGenerationError']
