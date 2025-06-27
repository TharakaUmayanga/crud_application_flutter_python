#!/usr/bin/env python3
"""
Debug API responses to understand the 400 errors
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
USERS_ENDPOINT = f"{BASE_URL}/users/"
VALID_API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"

print("🔍 Debugging API Responses...")

# Test 1: Valid API key with detailed response
headers = {"Authorization": f"ApiKey {VALID_API_KEY}"}
try:
    response = requests.get(USERS_ENDPOINT, headers=headers, timeout=10)
    print(f"\n📍 Valid API Key Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check API health
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"\n📍 API Root Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Check user list without API key
try:
    response = requests.get(USERS_ENDPOINT, timeout=10)
    print(f"\n📍 No API Key Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Check API key info endpoint
try:
    response = requests.get(f"{BASE_URL}/users/api-key/info/", headers=headers, timeout=10)
    print(f"\n📍 API Key Info Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
