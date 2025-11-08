"""Business Type Classification System

Automatically detects business type from category field and website content
to enable niche-specific template generation.

Based on brainstorming session results: docs/brainstorming-session-results-2025-11-06.md
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

# 12 Business Categories with Detection Keywords
CATEGORY_KEYWORDS = {
    "restaurant": {
        "primary": ["restaurant", "cafe", "dining", "food", "cuisine", "menu", "chef", "bistro", "eatery"],
        "secondary": ["pizza", "italian", "chinese", "indian", "thai", "sushi", "japanese", "mexican", "burger", "barbecue", "bbq", "steakhouse", "seafood", "vegan", "vegetarian"]
    },
    "professional": {
        "primary": ["lawyer", "attorney", "legal", "accountant", "accounting", "consultant", "consulting", "financial", "advisor", "cpa", "tax"],
        "secondary": ["law firm", "bookkeeping", "audit", "litigation", "contract", "business consulting", "strategy"]
    },
    "home_services": {
        "primary": ["plumber", "plumbing", "electrician", "electrical", "hvac", "heating", "cooling", "carpenter", "carpentry", "locksmith", "handyman"],
        "secondary": ["repair", "installation", "maintenance", "emergency", "24/7", "licensed", "insured"]
    },
    "health_medical": {
        "primary": ["dentist", "dental", "doctor", "physician", "clinic", "medical", "therapy", "therapist", "chiropractor", "physiotherapy"],
        "secondary": ["healthcare", "wellness", "treatment", "patient", "diagnosis", "surgery", "orthodontic", "pediatric"]
    },
    "beauty_wellness": {
        "primary": ["salon", "spa", "massage", "barber", "nails", "manicure", "pedicure", "beauty", "hair", "hairstylist"],
        "secondary": ["facial", "waxing", "makeup", "cosmetic", "skincare", "relaxation", "aromatherapy"]
    },
    "fitness": {
        "primary": ["gym", "fitness", "yoga", "pilates", "personal training", "crossfit", "workout", "exercise"],
        "secondary": ["weight loss", "muscle", "cardio", "strength", "wellness", "health club", "boxing", "martial arts"]
    },
    "retail": {
        "primary": ["shop", "store", "boutique", "retail", "products", "merchandise", "clothing", "apparel", "fashion"],
        "secondary": ["ecommerce", "shopping", "buy", "sale", "discount", "online store", "marketplace"]
    },
    "real_estate": {
        "primary": ["realtor", "real estate", "property", "homes", "houses", "apartments", "estate agent", "realty"],
        "secondary": ["buying", "selling", "rental", "lease", "commercial", "residential", "investment", "listing"]
    },
    "automotive": {
        "primary": ["mechanic", "auto repair", "car service", "automotive", "garage", "vehicle", "auto shop"],
        "secondary": ["oil change", "brake", "transmission", "engine", "tire", "inspection", "diagnostic", "body shop"]
    },
    "education": {
        "primary": ["school", "training", "courses", "tutoring", "education", "learning", "academy", "institute"],
        "secondary": ["teaching", "lessons", "class", "workshop", "certification", "online learning", "coaching"]
    },
    "creative": {
        "primary": ["photographer", "photography", "designer", "design", "agency", "studio", "creative", "artist"],
        "secondary": ["graphic design", "web design", "branding", "marketing", "advertising", "video", "production"]
    },
    "hospitality": {
        "primary": ["hotel", "motel", "accommodation", "bnb", "bed and breakfast", "resort", "inn", "lodging"],
        "secondary": ["rooms", "booking", "stay", "guest", "vacation", "travel", "amenities", "hospitality"]
    }
}

# Confidence indicators from website content/structure
CONFIDENCE_INDICATORS = {
    "restaurant": ["menu page", "reservation", "delivery", "takeout", "hours", "food photos"],
    "professional": ["credentials", "case studies", "consultation", "practice areas", "attorney", "certified"],
    "home_services": ["service area", "emergency", "licensed", "insured", "free quote", "24/7"],
    "health_medical": ["appointment", "insurance", "patients", "services", "doctors", "treatments"],
    "beauty_wellness": ["services", "pricing", "booking", "before/after", "gallery", "testimonials"],
    "fitness": ["classes", "schedule", "membership", "trainers", "facilities", "programs"],
    "retail": ["products", "cart", "checkout", "shipping", "returns", "catalog"],
    "real_estate": ["listings", "properties", "search", "agents", "mls", "sold"],
    "automotive": ["services", "appointment", "diagnostics", "warranty", "certified", "repairs"],
    "education": ["courses", "enrollment", "tuition", "curriculum", "instructors", "certification"],
    "creative": ["portfolio", "work", "clients", "packages", "projects", "gallery"],
    "hospitality": ["rooms", "availability", "check-in", "amenities", "location", "rates"]
}

# Secondary tags for more specific classification
SECONDARY_TAGS = {
    "restaurant": {
        "italian": ["italian", "pasta", "pizza", "romano"],
        "chinese": ["chinese", "dim sum", "wok", "asian"],
        "mexican": ["mexican", "taco", "burrito", "salsa"],
        "fast_food": ["fast food", "quick service", "drive-thru"],
        "fine_dining": ["fine dining", "upscale", "gourmet", "michelin"],
        "casual": ["casual", "family", "friendly", "neighborhood"],
        "cafe": ["cafe", "coffee", "bakery", "breakfast"]
    },
    "home_services": {
        "emergency": ["emergency", "24/7", "24 hour", "urgent"],
        "residential": ["residential", "home", "house"],
        "commercial": ["commercial", "business", "industrial"]
    },
    "beauty_wellness": {
        "hair": ["hair", "salon", "barber", "hairstylist"],
        "nails": ["nails", "manicure", "pedicure"],
        "spa": ["spa", "massage", "facial", "relaxation"]
    }
}


def classify_business(category: str, website_text: str = "", business_name: str = "") -> Dict:
    """
    Classify business type from category field and website content.

    Args:
        category: Business category field from database
        website_text: Scraped website content (optional, improves accuracy)
        business_name: Business name (optional, can contain type hints)

    Returns:
        {
            "primary_type": "restaurant",
            "confidence": 0.95,
            "secondary_tags": ["italian", "fine_dining"],
            "matched_keywords": ["restaurant", "cuisine", "chef"]
        }
    """

    # Combine all text sources for analysis
    search_text = f"{category} {business_name} {website_text}".lower()

    # Score each category
    category_scores = {}
    matched_keywords_by_category = {}

    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        matched = []

        # Check primary keywords (higher weight)
        for keyword in keywords["primary"]:
            if keyword in search_text:
                score += 10
                matched.append(keyword)

        # Check secondary keywords (lower weight)
        for keyword in keywords["secondary"]:
            if keyword in search_text:
                score += 3
                matched.append(keyword)

        # Check confidence indicators from website structure
        if website_text:
            for indicator in CONFIDENCE_INDICATORS.get(cat_name, []):
                if indicator in search_text:
                    score += 5

        category_scores[cat_name] = score
        matched_keywords_by_category[cat_name] = matched

    # Find best match
    if not category_scores or max(category_scores.values()) == 0:
        logger.warning(f"No category match found for: {category}")
        return {
            "primary_type": "general",
            "confidence": 0.0,
            "secondary_tags": [],
            "matched_keywords": [],
            "warning": "Could not classify business type"
        }

    primary_type = max(category_scores, key=category_scores.get)
    max_score = category_scores[primary_type]

    # Calculate confidence (0.0 to 1.0)
    # Score >= 30 = high confidence (0.9+)
    # Score 20-29 = good confidence (0.7-0.89)
    # Score 10-19 = medium confidence (0.5-0.69)
    # Score < 10 = low confidence (< 0.5)
    if max_score >= 30:
        confidence = min(0.95, 0.7 + (max_score - 30) * 0.01)
    elif max_score >= 20:
        confidence = 0.7 + (max_score - 20) * 0.02
    elif max_score >= 10:
        confidence = 0.5 + (max_score - 10) * 0.02
    else:
        confidence = max_score * 0.05

    # Detect secondary tags
    secondary_tags = []
    if primary_type in SECONDARY_TAGS:
        for tag, tag_keywords in SECONDARY_TAGS[primary_type].items():
            for keyword in tag_keywords:
                if keyword in search_text:
                    secondary_tags.append(tag)
                    break

    result = {
        "primary_type": primary_type,
        "confidence": round(confidence, 2),
        "secondary_tags": list(set(secondary_tags)),  # Remove duplicates
        "matched_keywords": matched_keywords_by_category[primary_type][:5]  # Top 5
    }

    logger.info(f"Classified as {primary_type} with {confidence:.0%} confidence")

    return result


def get_business_type_display_name(business_type: str) -> str:
    """Convert internal business type to display name"""
    display_names = {
        "restaurant": "Restaurant/Cafe",
        "professional": "Professional Services",
        "home_services": "Home Services",
        "health_medical": "Health/Medical",
        "beauty_wellness": "Beauty/Wellness",
        "fitness": "Fitness",
        "retail": "Retail/Shop",
        "real_estate": "Real Estate",
        "automotive": "Automotive",
        "education": "Education",
        "creative": "Creative Services",
        "hospitality": "Hospitality",
        "general": "General Business"
    }
    return display_names.get(business_type, business_type.replace("_", " ").title())


def get_all_business_types() -> List[str]:
    """Get list of all supported business types"""
    return list(CATEGORY_KEYWORDS.keys())


def get_category_keywords(business_type: str) -> Dict[str, List[str]]:
    """Get keywords for a specific business type"""
    return CATEGORY_KEYWORDS.get(business_type, {"primary": [], "secondary": []})
