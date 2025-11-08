#!/usr/bin/env python
"""Test authentication and evaluation flow"""
import requests
import sys

BASE_URL = "http://localhost:8000"

# Step 1: Register a new user
print("Step 1: Registering new user...")
register_data = {
    "email": "quicktest@example.com",
    "password": "password12345",
    "password_confirm": "password12345"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Register response: {response.status_code}")
    print(f"Register body: {response.text}")

    if response.status_code == 201:
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            print(f"OK User registered! Token: {access_token[:20]}...")
        else:
            print(f"ERROR: No access_token in response: {token_data}")
            sys.exit(1)
    else:
        # User might already exist, try login
        print(f"Registration failed ({response.status_code}), trying login...")
        login_data = {
            "email": "quicktest@example.com",
            "password": "password12345"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print(f"OK Logged in! Token: {access_token[:20]}...")
            else:
                print(f"ERROR: No access_token in login response: {token_data}")
                sys.exit(1)
        else:
            print(f"ERROR Login failed: {response.text}")
            sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test evaluation endpoint WITHOUT auth (should fail)
print("\nStep 2: Testing evaluation WITHOUT auth (should return 401/403)...")
business_id = "c250ddf4-cf33-4e5d-aa97-c49ceb083554"
response = requests.get(f"{BASE_URL}/api/businesses/{business_id}/evaluation")
print(f"Status: {response.status_code}, Response: {response.text[:100]}")

# Step 3: Test evaluation endpoint WITH auth (should work)
print("\nStep 3: Testing evaluation WITH auth (should work)...")
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/api/businesses/{business_id}/evaluation", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"SUCCESS! Evaluation retrieved:")
    print(f"  Aggregate Score: {data['aggregate_score']}")
    print(f"  Performance: {data['performance_score'] * 100}%")
    print(f"  SEO: {data['seo_score'] * 100}%")
    print(f"  Accessibility: {data['accessibility_score'] * 100}%")
else:
    print(f"FAILED: {response.status_code} - {response.text}")

print("\n" + "="*60)
print("SOLUTION: You need to LOGIN in the frontend!")
print("="*60)
print("1. Go to http://localhost:3000")
print("2. Click 'Login' or 'Register'")
print("3. Enter your credentials")
print("4. The frontend will save the JWT token to localStorage")
print("5. Then ALL API requests will include: Authorization: Bearer <token>")
print("6. And the evaluation endpoint will work!")
print("="*60)
