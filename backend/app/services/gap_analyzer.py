"""Gap Analysis Module

Analyzes old business websites to identify weaknesses and gaps.
Results guide new template generation to explicitly address each weakness.

Based on brainstorming session: docs/brainstorming-session-results-2025-11-06.md
Critical Insight #5: "Gap Analysis" approach - Analyze old site → Identify weaknesses → Generate improved site

Common small business website weaknesses identified:
- Not mobile responsive
- Old styling/outdated design
- Poor SEO (missing meta tags, headings)
- Weak/inappropriate colors
- Slow loading speed
- Missing key sections (testimonials, clear CTAs, contact forms)
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


def check_mobile_responsiveness(html_content: str) -> Dict[str, any]:
    """
    Check if website has mobile responsive design.

    Args:
        html_content: Raw HTML content

    Returns:
        Dictionary with mobile responsiveness analysis
    """
    issues = []
    score = 100

    # Check for viewport meta tag
    has_viewport = bool(re.search(
        r'<meta[^>]+name=["\']viewport["\'][^>]*>',
        html_content,
        re.IGNORECASE
    ))

    if not has_viewport:
        issues.append("Missing viewport meta tag for mobile devices")
        score -= 40

    # Check for media queries (responsive CSS)
    has_media_queries = bool(re.search(
        r'@media[^{]+\([^)]*\)',
        html_content,
        re.IGNORECASE
    ))

    if not has_media_queries:
        issues.append("No CSS media queries detected (likely not responsive)")
        score -= 30

    # Check for mobile-specific classes/frameworks
    has_mobile_framework = any([
        'bootstrap' in html_content.lower(),
        'tailwind' in html_content.lower(),
        'foundation' in html_content.lower(),
        'mobile' in html_content.lower(),
        'responsive' in html_content.lower()
    ])

    if not has_mobile_framework:
        issues.append("No mobile-friendly CSS framework detected")
        score -= 20

    return {
        "score": max(0, score),
        "has_viewport": has_viewport,
        "has_media_queries": has_media_queries,
        "has_mobile_framework": has_mobile_framework,
        "issues": issues,
        "severity": "critical" if score < 40 else "high" if score < 70 else "medium"
    }


def check_design_modernity(html_content: str) -> Dict[str, any]:
    """
    Analyze design modernity and styling.

    Args:
        html_content: Raw HTML content

    Returns:
        Dictionary with design modernity analysis
    """
    issues = []
    score = 100
    modern_indicators = 0
    outdated_indicators = 0

    # Check for modern design indicators
    modern_features = {
        "flexbox": r'display:\s*flex',
        "grid": r'display:\s*grid',
        "css_variables": r'var\(--[^)]+\)',
        "modern_fonts": r'font-family:[^;]*(sans-serif|roboto|open\s+sans|lato|montserrat)',
        "modern_colors": r'rgba?\s*\(',
        "transitions": r'transition:',
        "animations": r'@keyframes|animation:'
    }

    for feature, pattern in modern_features.items():
        if re.search(pattern, html_content, re.IGNORECASE):
            modern_indicators += 1

    # Check for outdated indicators
    outdated_features = {
        "tables_layout": r'<table[^>]*>\s*<tr[^>]*>\s*<td[^>]*>.*?layout|design',
        "frames": r'<frame|<frameset',
        "flash": r'\.swf|flash',
        "marquee": r'<marquee',
        "font_tags": r'<font[^>]*>',
        "inline_styles_heavy": len(re.findall(r'style=["\']', html_content)) > 50,
        "comic_sans": r'comic\s+sans' in html_content.lower()
    }

    for feature, pattern in outdated_features.items():
        if isinstance(pattern, bool):
            if pattern:
                outdated_indicators += 1
                issues.append(f"Outdated: {feature.replace('_', ' ')}")
        elif re.search(pattern, html_content, re.IGNORECASE):
            outdated_indicators += 1
            issues.append(f"Outdated: {feature.replace('_', ' ')}")

    # Calculate score
    score = (modern_indicators * 10) - (outdated_indicators * 15)
    score = max(0, min(100, score))

    if modern_indicators < 2:
        issues.append("Very few modern CSS features detected")

    if outdated_indicators == 0 and modern_indicators < 3:
        issues.append("Design appears basic/minimal (not necessarily bad, but could be enhanced)")

    return {
        "score": score,
        "modern_indicators": modern_indicators,
        "outdated_indicators": outdated_indicators,
        "issues": issues,
        "severity": "critical" if score < 30 else "high" if score < 60 else "medium" if score < 80 else "low"
    }


def check_seo_basics(html_content: str, business_name: str = "") -> Dict[str, any]:
    """
    Check basic SEO elements.

    Args:
        html_content: Raw HTML content
        business_name: Business name for validation

    Returns:
        Dictionary with SEO analysis
    """
    issues = []
    score = 100

    # Check for title tag
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
    has_title = bool(title_match)
    title_text = title_match.group(1) if title_match else ""

    if not has_title or len(title_text.strip()) < 10:
        issues.append("Missing or too-short title tag")
        score -= 20
    elif len(title_text) > 60:
        issues.append("Title tag too long (>60 chars)")
        score -= 5

    # Check for meta description
    has_meta_description = bool(re.search(
        r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']{20,})["\']',
        html_content,
        re.IGNORECASE
    ))

    if not has_meta_description:
        issues.append("Missing meta description")
        score -= 20

    # Check for heading structure (H1, H2, etc.)
    h1_count = len(re.findall(r'<h1[^>]*>', html_content, re.IGNORECASE))

    if h1_count == 0:
        issues.append("No H1 heading found")
        score -= 15
    elif h1_count > 1:
        issues.append("Multiple H1 headings (should be only one)")
        score -= 5

    has_h2 = bool(re.search(r'<h2[^>]*>', html_content, re.IGNORECASE))
    if not has_h2:
        issues.append("No H2 headings found (poor content structure)")
        score -= 10

    # Check for alt attributes on images
    images_without_alt = len(re.findall(
        r'<img(?![^>]*alt=)[^>]*>',
        html_content,
        re.IGNORECASE
    ))

    if images_without_alt > 3:
        issues.append(f"{images_without_alt} images missing alt attributes")
        score -= 15

    # Check for schema.org markup
    has_schema = bool(re.search(
        r'schema\.org|itemtype=|@type',
        html_content,
        re.IGNORECASE
    ))

    if not has_schema:
        issues.append("No schema.org structured data found")
        score -= 15

    return {
        "score": max(0, score),
        "has_title": has_title,
        "has_meta_description": has_meta_description,
        "h1_count": h1_count,
        "has_schema": has_schema,
        "images_without_alt": images_without_alt,
        "issues": issues,
        "severity": "high" if score < 50 else "medium" if score < 75 else "low"
    }


def check_performance_indicators(html_content: str) -> Dict[str, any]:
    """
    Estimate performance based on page size and resource loading.

    Args:
        html_content: Raw HTML content

    Returns:
        Dictionary with performance analysis
    """
    issues = []
    score = 100

    # Estimate page size
    page_size_kb = len(html_content) / 1024

    if page_size_kb > 500:
        issues.append(f"Large HTML size ({page_size_kb:.0f}KB)")
        score -= 20
    elif page_size_kb > 200:
        issues.append(f"Moderate HTML size ({page_size_kb:.0f}KB)")
        score -= 10

    # Count external resources
    script_count = len(re.findall(r'<script[^>]+src=', html_content, re.IGNORECASE))
    stylesheet_count = len(re.findall(r'<link[^>]+rel=["\']stylesheet["\']', html_content, re.IGNORECASE))

    if script_count > 10:
        issues.append(f"Many external scripts ({script_count})")
        score -= 15

    if stylesheet_count > 5:
        issues.append(f"Many external stylesheets ({stylesheet_count})")
        score -= 10

    # Check for lazy loading
    has_lazy_loading = bool(re.search(
        r'loading=["\']lazy["\']|lazy-load',
        html_content,
        re.IGNORECASE
    ))

    if not has_lazy_loading:
        issues.append("No lazy loading detected for images")
        score -= 10

    # Check for minification indicators
    is_minified = (
        '<!--' not in html_content[:1000] and  # No comments in first 1000 chars
        '\n\n' not in html_content[:1000]  # No double line breaks
    )

    if not is_minified:
        issues.append("HTML not minified (contains comments/excess whitespace)")
        score -= 10

    return {
        "score": max(0, score),
        "page_size_kb": round(page_size_kb, 1),
        "script_count": script_count,
        "stylesheet_count": stylesheet_count,
        "has_lazy_loading": has_lazy_loading,
        "is_minified": is_minified,
        "issues": issues,
        "severity": "high" if score < 50 else "medium" if score < 75 else "low"
    }


def check_missing_sections(html_content: str, business_type: str) -> Dict[str, any]:
    """
    Identify missing important sections for business type.

    Args:
        html_content: Raw HTML content
        business_type: Classified business type

    Returns:
        Dictionary with missing sections analysis
    """
    issues = []
    score = 100

    # Universal sections (all businesses should have)
    universal_sections = {
        "contact_form": r'<form[^>]*>.*?(?:email|phone|name|message)',
        "testimonials": r'testimonial|review|customer\s+says|feedback',
        "about": r'about\s+us|who\s+we\s+are|our\s+story|our\s+team',
        "call_to_action": r'<button|<a[^>]+class=["\'][^"\']*btn[^"\']*["\']',
    }

    for section, pattern in universal_sections.items():
        if not re.search(pattern, html_content, re.IGNORECASE | re.DOTALL):
            issues.append(f"Missing {section.replace('_', ' ')}")
            score -= 15

    # Business-specific sections
    business_specific = {
        "restaurant": {
            "menu": r'menu|food|dishes|cuisine',
            "reservation": r'reserv|book\s+table|book\s+now',
            "location_map": r'google.*map|map.*embed|location'
        },
        "home_services": {
            "service_area": r'service\s+area|we\s+serve|coverage',
            "emergency_contact": r'emergency|24/?7|urgent',
            "certifications": r'licensed|insured|certified|accredited'
        },
        "professional": {
            "credentials": r'education|degree|certified|licensed|bar\s+admission',
            "case_studies": r'case\s+study|case\s+studies|portfolio|work|results',
            "consultation": r'consultation|free\s+consult|schedule\s+appointment'
        }
    }

    if business_type in business_specific:
        for section, pattern in business_specific[business_type].items():
            if not re.search(pattern, html_content, re.IGNORECASE):
                issues.append(f"Missing business-specific: {section.replace('_', ' ')}")
                score -= 10

    return {
        "score": max(0, score),
        "missing_sections": len(issues),
        "issues": issues,
        "severity": "high" if score < 50 else "medium" if score < 75 else "low"
    }


def analyze_website_gaps(
    html_content: str,
    business_name: str = "",
    business_type: str = "general"
) -> Dict:
    """
    Comprehensive gap analysis of old website.

    Main interface for gap analysis.

    Args:
        html_content: Raw HTML content from old website
        business_name: Business name
        business_type: Classified business type

    Returns:
        Complete gap analysis report:
        {
            "overall_score": 62,
            "priority_gaps": ["mobile responsiveness", "SEO basics"],
            "mobile": {...},
            "design": {...},
            "seo": {...},
            "performance": {...},
            "missing_sections": {...},
            "recommendations": [...]
        }
    """

    logger.info(f"Analyzing website gaps for {business_name} ({business_type})")

    # Run all checks
    mobile = check_mobile_responsiveness(html_content)
    design = check_design_modernity(html_content)
    seo = check_seo_basics(html_content, business_name)
    performance = check_performance_indicators(html_content)
    missing = check_missing_sections(html_content, business_type)

    # Calculate overall score (weighted average)
    overall_score = int(
        mobile["score"] * 0.30 +  # 30% weight - most important
        design["score"] * 0.20 +  # 20% weight
        seo["score"] * 0.25 +     # 25% weight
        performance["score"] * 0.15 +  # 15% weight
        missing["score"] * 0.10    # 10% weight
    )

    # Identify priority gaps (critical/high severity with low scores)
    priority_gaps = []
    if mobile["severity"] in ["critical", "high"]:
        priority_gaps.append("mobile_responsiveness")
    if design["severity"] in ["critical", "high"]:
        priority_gaps.append("modern_design")
    if seo["severity"] == "high":
        priority_gaps.append("seo_optimization")
    if performance["severity"] == "high":
        priority_gaps.append("performance")
    if missing["severity"] == "high":
        priority_gaps.append("key_sections")

    # Generate recommendations
    recommendations = []
    if "mobile_responsiveness" in priority_gaps:
        recommendations.append("Implement mobile-first responsive design with proper viewport and media queries")
    if "modern_design" in priority_gaps:
        recommendations.append("Modernize design with flexbox/grid layouts, contemporary colors, and smooth animations")
    if "seo_optimization" in priority_gaps:
        recommendations.append("Add proper meta tags, structured headings, schema.org markup, and image alt text")
    if "performance" in priority_gaps:
        recommendations.append("Optimize loading speed with lazy loading, minification, and reduced external resources")
    if "key_sections" in priority_gaps:
        recommendations.append(f"Add missing sections important for {business_type} businesses")

    # Always recommend these if scores are below 100
    if mobile["score"] < 100 and "mobile_responsiveness" not in priority_gaps:
        recommendations.append("Minor mobile responsiveness improvements needed")
    if seo["score"] < 100 and "seo_optimization" not in priority_gaps:
        recommendations.append("Minor SEO enhancements recommended")

    result = {
        "overall_score": overall_score,
        "priority_gaps": priority_gaps,
        "mobile": mobile,
        "design": design,
        "seo": seo,
        "performance": performance,
        "missing_sections": missing,
        "recommendations": recommendations,
        "gap_count": len(priority_gaps),
        "total_issues": sum([
            len(mobile["issues"]),
            len(design["issues"]),
            len(seo["issues"]),
            len(performance["issues"]),
            len(missing["issues"])
        ])
    }

    logger.info(f"Gap analysis complete: {overall_score}/100, {len(priority_gaps)} priority gaps identified")

    return result
