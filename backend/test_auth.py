#!/usr/bin/env python3
"""
Test script for API key authentication
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"

# Headers with API key
headers = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json"
}

def test_api_key_validation():
    """Test API key validation endpoint"""
    print("🔐 Testing API key validation...")
    response = requests.post(f"{BASE_URL}/api/users/api-key/validate/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_api_key_info():
    """Test API key info endpoint"""
    print("ℹ️  Testing API key info...")
    response = requests.get(f"{BASE_URL}/api/users/api-key/info/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_users_list():
    """Test users list endpoint with authentication"""
    print("👥 Testing users list with authentication...")
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_users_list_without_auth():
    """Test users list endpoint without authentication"""
    print("❌ Testing users list without authentication...")
    response = requests.get(f"{BASE_URL}/api/users/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_user():
    """Test creating a user with authentication"""
    print("➕ Testing user creation with authentication...")
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "address": "123 Test Street",
        "age": 25
    }
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("🚀 Starting API Authentication Tests")
    print("=" * 50)
    
    try:
        test_api_key_validation()
        test_api_key_info()
        test_users_list_without_auth()
        test_users_list()
        test_create_user()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
