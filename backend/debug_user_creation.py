#!/usr/bin/env python3
"""
Debug user creation endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
USERS_ENDPOINT = f"{BASE_URL}/users/"
VALID_API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"

print("🔍 Debugging User Creation...")

headers = {"Authorization": f"ApiKey {VALID_API_KEY}", "Content-Type": "application/json"}

valid_user = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "address": "123 Main St, City, Country"
}

try:
    response = requests.post(USERS_ENDPOINT, headers=headers, json=valid_user, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
