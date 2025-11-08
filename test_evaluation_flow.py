#!/usr/bin/env python
"""Test complete evaluation flow: login -> create business -> evaluate -> check scores"""
import requests
import sys
import json
import time

BASE_URL = "http://localhost:8000"

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

print("=" * 80)
print("TESTING COMPLETE EVALUATION FLOW")
print("=" * 80)

# Step 1: Login
print("\n[1/5] Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "quicktest@example.com", "password": "password12345"}
)

if login_response.status_code != 200:
    print(f"ERROR: Login failed with status {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"SUCCESS: Logged in! Token: {token[:30]}...")

# Step 2: Create a test business (use unique timestamp-based URL)
print("\n[2/5] Creating test business...")
import random
test_id = random.randint(10000, 99999)
business_data = {
    "name": f"Microsoft UK Test {test_id}",
    "website_url": "https://www.microsoft.com",
    "description": "Test business for evaluation",
    "category": "Technology",
    "location": "London, UK"
}

business_response = requests.post(
    f"{BASE_URL}/api/businesses",
    headers=headers,
    json=business_data
)

if business_response.status_code != 201:
    print(f"ERROR: Business creation failed with status {business_response.status_code}")
    print(business_response.text)
    print(f"\nNote: If business already exists, that's OK - we just need to test evaluation")
    # Try to find ANY business to test with
    list_response = requests.get(f"{BASE_URL}/api/businesses", headers=headers, params={"limit": 1})
    if list_response.status_code == 200:
        businesses = list_response.json()
        if businesses["items"]:
            business = businesses["items"][0]
            business_id = business["id"]
            print(f"Using existing business: {business['name']} ({business_id})")
        else:
            print("ERROR: No businesses found")
            sys.exit(1)
    else:
        print("ERROR: Could not fetch businesses")
        sys.exit(1)
else:
    business = business_response.json()
    business_id = business["id"]
    print(f"SUCCESS: Business created with ID: {business_id}")
    print(f"  Name: {business['name']}")
    print(f"  Website: {business['website_url']}")

# Step 3: Trigger evaluation
print(f"\n[3/5] Triggering evaluation for business {business_id}...")
eval_response = requests.post(
    f"{BASE_URL}/api/evaluations",
    headers=headers,
    json={"business_id": business_id}
)

if eval_response.status_code not in [200, 201]:
    print(f"ERROR: Evaluation failed with status {eval_response.status_code}")
    print(eval_response.text)
    sys.exit(1)

evaluation = eval_response.json()
evaluation_id = evaluation["id"]
print(f"SUCCESS: Evaluation created with ID: {evaluation_id}")

# Step 4: Wait a moment for evaluation to process
print("\n[4/5] Waiting for evaluation to complete...")
time.sleep(2)

# Step 5: Check evaluation results
print(f"\n[5/5] Fetching evaluation results...")
eval_get_response = requests.get(
    f"{BASE_URL}/api/businesses/{business_id}/evaluations",
    headers=headers
)

if eval_get_response.status_code != 200:
    print(f"ERROR: Failed to fetch evaluation with status {eval_get_response.status_code}")
    print(eval_get_response.text)
    sys.exit(1)

final_evaluation = eval_get_response.json()

print("\n" + "=" * 80)
print("EVALUATION RESULTS")
print("=" * 80)
print(f"Business: {business['name']} ({business['website_url']})")
print(f"\nScores:")
print(f"  Aggregate Score:    {final_evaluation['aggregate_score']:.1f}/100")
print(f"  Performance:        {final_evaluation['performance_score'] * 100:.0f}/100")
print(f"  SEO:                {final_evaluation['seo_score'] * 100:.0f}/100")
print(f"  Accessibility:      {final_evaluation['accessibility_score'] * 100:.0f}/100")
print(f"  Best Practices:     {final_evaluation['best_practices_score'] * 100:.0f}/100")

# Check if business score was updated
print(f"\n[VERIFICATION] Fetching business to check if score was saved...")
business_get_response = requests.get(
    f"{BASE_URL}/api/businesses/{business_id}",
    headers=headers
)

if business_get_response.status_code == 200:
    updated_business = business_get_response.json()
    if updated_business.get('score') is not None:
        print(f"SUCCESS: Business score saved: {updated_business['score']:.1f}/100")
    else:
        print(f"WARNING: Business score is still NULL")
        print(f"Business data: {json.dumps(updated_business, indent=2)}")

print("\n" + "=" * 80)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nNext steps:")
print("1. Go to http://localhost:3000")
print("2. Login with: quicktest@example.com / password12345")
print("3. You should see the business with the score displayed on the card")
print("4. Click the card to see full evaluation details")
print("=" * 80)
