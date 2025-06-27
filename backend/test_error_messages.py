#!/usr/bin/env python3
"""
Test improved error messaging for frontend
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
USERS_ENDPOINT = f"{BASE_URL}/users/"
VALID_API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"

def test_error_messages():
    """Test that detailed error messages are properly sent to frontend"""
    
    headers = {"Authorization": f"ApiKey {VALID_API_KEY}", "Content-Type": "application/json"}
    
    print("🧪 Testing Improved Error Messages for Frontend")
    print("=" * 60)
    
    # Test 1: Invalid email format
    print("\n1️⃣ Testing invalid email format...")
    invalid_email_data = {
        "name": "Test User",
        "email": "invalid-email-format",
        "age": 25
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=invalid_email_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Error response structure:")
            print(f"   Success: {error_data.get('success')}")
            print(f"   Message: {error_data.get('message')}")
            print(f"   Errors: {error_data.get('errors')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Duplicate email
    print("\n2️⃣ Testing duplicate email...")
    duplicate_email_data = {
        "name": "Another User",
        "email": "test@example.com",  # This email likely already exists
        "age": 30
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=duplicate_email_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Error response structure:")
            print(f"   Success: {error_data.get('success')}")
            print(f"   Message: {error_data.get('message')}")
            print(f"   Errors: {error_data.get('errors')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Invalid domain TLD (like in the user's error log)
    print("\n3️⃣ Testing invalid domain TLD...")
    invalid_tld_data = {
        "name": "Test User",
        "email": "user@example.xyz",  # xyz TLD might not be supported
        "age": 25
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=invalid_tld_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Error response structure:")
            print(f"   Success: {error_data.get('success')}")
            print(f"   Message: {error_data.get('message')}")
            print(f"   Errors: {error_data.get('errors')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Multiple validation errors
    print("\n4️⃣ Testing multiple validation errors...")
    multi_error_data = {
        "name": "",  # Empty name
        "email": "invalid-email",  # Invalid email
        "age": -5  # Invalid age
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=multi_error_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Error response structure:")
            print(f"   Success: {error_data.get('success')}")
            print(f"   Message: {error_data.get('message')}")
            print(f"   Errors: {error_data.get('errors')}")
            print(f"   Number of error fields: {len(error_data.get('errors', {}))}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Successful creation (to test success response format)
    print("\n5️⃣ Testing successful creation...")
    import time
    unique_email = f"test.success.{int(time.time())}@example.com"
    success_data = {
        "name": "Success User",
        "email": unique_email,
        "age": 28
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=success_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            success_data = response.json()
            print("✅ Success response structure:")
            print(f"   Success: {success_data.get('success')}")
            print(f"   Message: {success_data.get('message')}")
            print(f"   Has Data: {'data' in success_data}")
            if 'data' in success_data:
                print(f"   User ID: {success_data['data'].get('id')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Error Message Testing Complete!")

if __name__ == "__main__":
    test_error_messages()
