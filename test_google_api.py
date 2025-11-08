#!/usr/bin/env python
"""Test Google PageSpeed Insights API directly"""
import requests
import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('backend/.env')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(f"Using Google API Key: {GOOGLE_API_KEY}")

# Test URL
TEST_URL = "https://www.google.com"

# PageSpeed Insights API endpoint
API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

print(f"\nTesting Google PageSpeed Insights API...")
print(f"Target URL: {TEST_URL}\n")

try:
    params = {
        "url": TEST_URL,
        "strategy": "mobile",
        "category": ["performance", "seo", "accessibility", "best-practices"]
    }

    if GOOGLE_API_KEY:
        params["key"] = GOOGLE_API_KEY
        print(f"Making request WITH API key...")
    else:
        print(f"Making request WITHOUT API key (may have lower rate limits)...")

    response = requests.get(API_URL, params=params, timeout=60)

    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        lighthouse_result = data.get("lighthouseResult", {})
        categories = lighthouse_result.get("categories", {})

        performance = categories.get("performance", {}).get("score", 0)
        seo = categories.get("seo", {}).get("score", 0)
        accessibility = categories.get("accessibility", {}).get("score", 0)
        best_practices = categories.get("best-practices", {}).get("score", 0)

        print(f"\n✅ SUCCESS! Google PageSpeed Insights API is working!")
        print(f"\nScores for {TEST_URL}:")
        print(f"  Performance:    {performance * 100:.0f}/100")
        print(f"  SEO:            {seo * 100:.0f}/100")
        print(f"  Accessibility:  {accessibility * 100:.0f}/100")
        print(f"  Best Practices: {best_practices * 100:.0f}/100")
        print(f"\nAggregate Score: {(performance + seo + accessibility + best_practices) / 4 * 100:.1f}/100")
    elif response.status_code == 403:
        print(f"\n❌ ERROR: 403 Forbidden")
        print(f"Response: {response.text[:500]}")
        print(f"\n🔑 The Google API key is NOT working!")
        print(f"\nTo fix this:")
        print(f"1. Go to: https://console.cloud.google.com/apis/dashboard")
        print(f"2. Enable 'PageSpeed Insights API'")
        print(f"3. Make sure the API key has permission to use this API")
        sys.exit(1)
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print(f"\n❌ ERROR: Request timed out")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
