"""
Check template quality for businesses with low design scores.
Identify what's "broken" about the generated HTML.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business, Template

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_html_quality(html: str) -> dict:
    """
    Analyze HTML quality and identify issues.

    Returns:
        Dictionary with quality metrics and issues
    """
    issues = []
    metrics = {}

    if not html:
        return {'issues': ['Empty HTML'], 'metrics': {}}

    html_lower = html.lower()

    # Check basic structure
    metrics['length'] = len(html)
    metrics['has_doctype'] = '<!doctype' in html_lower
    metrics['has_html_tag'] = '<html' in html_lower
    metrics['has_head_tag'] = '<head' in html_lower
    metrics['has_body_tag'] = '<body' in html_lower
    metrics['has_closing_html'] = '</html>' in html_lower
    metrics['has_closing_body'] = '</body>' in html_lower

    # Check for CSS
    metrics['has_style_tag'] = '<style' in html_lower
    metrics['has_inline_css'] = 'style=' in html_lower
    metrics['has_external_css'] = '<link' in html_lower and 'stylesheet' in html_lower

    # Check for JavaScript
    metrics['has_script_tag'] = '<script' in html_lower

    # Check for meta tags
    metrics['has_meta_viewport'] = 'viewport' in html_lower
    metrics['has_charset'] = 'charset' in html_lower

    # Check for semantic HTML5
    metrics['has_header'] = '<header' in html_lower
    metrics['has_footer'] = '<footer' in html_lower
    metrics['has_nav'] = '<nav' in html_lower
    metrics['has_section'] = '<section' in html_lower

    # Identify issues
    if not metrics['has_doctype']:
        issues.append('Missing DOCTYPE declaration')

    if not metrics['has_html_tag']:
        issues.append('Missing <html> tag')

    if not metrics['has_head_tag']:
        issues.append('Missing <head> section')

    if not metrics['has_body_tag']:
        issues.append('Missing <body> tag')

    if not metrics['has_closing_html'] or not metrics['has_closing_body']:
        issues.append('Missing closing tags (incomplete HTML)')

    if not (metrics['has_style_tag'] or metrics['has_inline_css'] or metrics['has_external_css']):
        issues.append('No CSS styling found')

    if not metrics['has_meta_viewport']:
        issues.append('Missing viewport meta tag (not mobile responsive)')

    if not metrics['has_charset']:
        issues.append('Missing charset declaration')

    if metrics['length'] < 1000:
        issues.append(f'HTML too short ({metrics["length"]} chars) - likely incomplete')

    # Check for modern HTML5 elements
    if not (metrics['has_header'] or metrics['has_footer'] or metrics['has_nav'] or metrics['has_section']):
        issues.append('No semantic HTML5 elements (not modern)')

    return {
        'issues': issues,
        'metrics': metrics
    }


def check_template_quality():
    """Check template quality for businesses with low scores"""
    db: Session = SessionLocal()

    try:
        logger.info("="*80)
        logger.info("CHECKING TEMPLATE QUALITY FOR LOW-SCORE BUSINESSES")
        logger.info("="*80)
        logger.info("")

        # Find businesses with score < 70
        low_score_businesses = db.query(Business).filter(
            Business.score < 70
        ).order_by(Business.created_at.desc()).limit(10).all()

        logger.info(f"Found {len(low_score_businesses)} businesses with score < 70")
        logger.info("")

        if not low_score_businesses:
            logger.info("No businesses with low scores found. Checking all recent businesses...")
            # Get most recent businesses
            low_score_businesses = db.query(Business).order_by(
                Business.created_at.desc()
            ).limit(10).all()

        for business in low_score_businesses:
            logger.info("="*80)
            logger.info(f"Business: {business.name}")
            logger.info(f"  ID: {business.id}")
            logger.info(f"  Score: {business.score}")
            logger.info(f"  Website URL: {business.website_url}")
            logger.info("")

            # Get templates for this business
            templates = db.query(Template).filter(
                Template.business_id == business.id
            ).all()

            if not templates:
                logger.warning(f"  ⚠️  No templates found for this business")
                logger.info("")
                continue

            logger.info(f"  Found {len(templates)} template(s)")
            logger.info("")

            for i, template in enumerate(templates, 1):
                logger.info(f"  Template #{i}:")
                logger.info(f"    Template ID: {template.id}")
                logger.info(f"    Variant: {template.variant_number}")
                logger.info(f"    Generated: {template.generated_at}")
                logger.info("")

                # Analyze HTML quality
                analysis = analyze_html_quality(template.html_content)

                logger.info(f"    📊 HTML Quality Metrics:")
                for key, value in analysis['metrics'].items():
                    status = "✅" if value else "❌"
                    logger.info(f"      {status} {key}: {value}")

                logger.info("")

                if analysis['issues']:
                    logger.error(f"    🔴 QUALITY ISSUES DETECTED ({len(analysis['issues'])} issues):")
                    for issue in analysis['issues']:
                        logger.error(f"      ❌ {issue}")
                else:
                    logger.info(f"    ✅ No major quality issues detected")

                logger.info("")

                # Show HTML preview
                preview_length = 500
                preview = template.html_content[:preview_length]
                logger.info(f"    📄 HTML Preview (first {preview_length} chars):")
                logger.info(f"    {repr(preview)}")
                logger.info("")

                # Show end of HTML too (to check if complete)
                if len(template.html_content) > preview_length:
                    end_preview = template.html_content[-300:]
                    logger.info(f"    📄 HTML End (last 300 chars):")
                    logger.info(f"    {repr(end_preview)}")
                    logger.info("")

        logger.info("="*80)
        logger.info("QUALITY CHECK COMPLETE")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    check_template_quality()
