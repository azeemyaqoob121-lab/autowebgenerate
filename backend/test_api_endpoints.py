"""
Test the generate and regenerate API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
import requests
import json

def main():
    print("\n" + "="*80)
    print("TESTING GENERATE AND REGENERATE API ENDPOINTS")
    print("="*80)

    db = SessionLocal()

    try:
        # Get C.C Electrical business
        business = db.query(Business).filter(
            Business.name == "C.C Electrical & Sons"
        ).first()

        if not business:
            print("ERROR: Business not found")
            return False

        print(f"\nBusiness: {business.name}")
        print(f"Business ID: {business.id}")

        base_url = "http://localhost:8000"

        # Test 1: Get existing templates
        print("\n" + "-"*80)
        print("TEST 1: Get existing templates")
        print("-"*80)

        response = requests.get(f"{base_url}/api/businesses/{business.id}/templates")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} template(s)")
            if data['total'] > 0:
                for template in data['templates']:
                    print(f"  - Template {template['id']}: Variant {template['variant_number']}, {len(template['html_content'])} chars")
        else:
            print(f"ERROR: {response.text}")

        # Test 2: Try to generate (should fail if templates exist)
        print("\n" + "-"*80)
        print("TEST 2: Try to generate new templates (should fail if exist)")
        print("-"*80)

        response = requests.post(
            f"{base_url}/api/businesses/{business.id}/templates/generate",
            json={}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 400:
            print("EXPECTED: Cannot generate - templates already exist")
            print(f"Message: {response.json()['detail']}")
        elif response.status_code == 201:
            print("SUCCESS: Generated new templates")
            data = response.json()
            print(f"Generated {data['total']} template(s)")
        else:
            print(f"ERROR: {response.text}")

        # Test 3: Regenerate templates
        print("\n" + "-"*80)
        print("TEST 3: Regenerate templates (delete old, create new)")
        print("-"*80)
        print("This will take 30-60 seconds as AI generates new templates...")

        response = requests.post(
            f"{base_url}/api/businesses/{business.id}/templates/regenerate",
            json={},
            timeout=180  # 3 minute timeout
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Regenerated {data['total']} template(s)")
            for template in data['templates']:
                print(f"  - Template {template['id']}: Variant {template['variant_number']}, {len(template['html_content'])} chars")
        else:
            print(f"ERROR: {response.text}")

        # Test 4: Verify new templates
        print("\n" + "-"*80)
        print("TEST 4: Verify new templates exist")
        print("-"*80)

        response = requests.get(f"{base_url}/api/businesses/{business.id}/templates")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} template(s) after regeneration")
            if data['total'] > 0:
                for template in data['templates']:
                    html_len = len(template['html_content'])
                    has_tailwind = 'Yes' if '<script src="https://cdn.tailwindcss.com"' in template['html_content'] else 'NO - ERROR!'
                    has_doctype = 'Yes' if '<!DOCTYPE' in template['html_content'] else 'No'
                    print(f"  - Template {template['id']}:")
                    print(f"    Variant: {template['variant_number']}")
                    print(f"    HTML size: {html_len:,} characters")
                    print(f"    Has Tailwind: {has_tailwind}")
                    print(f"    Has DOCTYPE: {has_doctype}")
        else:
            print(f"ERROR: {response.text}")

        print("\n" + "="*80)
        print("API ENDPOINT TESTS COMPLETE!")
        print("="*80)

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    main()
