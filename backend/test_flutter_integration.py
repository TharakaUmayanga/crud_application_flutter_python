#!/usr/bin/env python3
"""
Test Flutter-Backend Integration
Tests the API from the Flutter frontend perspective
"""

import requests
import json

# Flutter frontend configuration (matching api_config.dart)
BASE_URL = "http://localhost:8000/api"
API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"
USERS_ENDPOINT = f"{BASE_URL}/users/"

def test_flutter_integration():
    """Test API calls that Flutter frontend would make"""
    
    # Headers matching Flutter's ApiConfig.headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'ApiKey {API_KEY}',
    }
    
    print("🔗 Testing Flutter-Backend Integration...")
    print("=" * 50)
    
    # Test 1: Get users list (matching Flutter's getUsers method)
    try:
        response = requests.get(f"{USERS_ENDPOINT}?page=1&page_size=10", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ GET Users List:")
            print(f"   Status: {response.status_code}")
            print(f"   Count: {data.get('count', 0)}")
            print(f"   Pages: {data.get('total_pages', 0)}")
            print(f"   Current Page: {data.get('current_page', 1)}")
        else:
            print(f"❌ GET Users List failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET Users List error: {e}")
    
    # Test 2: Create user (matching Flutter's createUser method)
    user_data = {
        "name": "Flutter Test User",
        "email": "flutter.test@example.com",
        "age": 25,
        "address": "Flutter Street 123"
    }
    
    try:
        response = requests.post(USERS_ENDPOINT, headers=headers, json=user_data, timeout=30)
        if response.status_code == 201:
            created_user = response.json()
            user_id = created_user.get('id')
            print("✅ POST Create User:")
            print(f"   Status: {response.status_code}")
            print(f"   Created ID: {user_id}")
            
            # Test 3: Get specific user (matching Flutter's getUser method)
            if user_id:
                response = requests.get(f"{USERS_ENDPOINT}{user_id}/", headers=headers, timeout=30)
                if response.status_code == 200:
                    user = response.json()
                    print("✅ GET Specific User:")
                    print(f"   Status: {response.status_code}")
                    print(f"   Name: {user.get('name')}")
                    print(f"   Email: {user.get('email')}")
                
                # Test 4: Update user (matching Flutter's updateUser method)
                update_data = {"name": "Flutter Updated User"}
                response = requests.patch(f"{USERS_ENDPOINT}{user_id}/", headers=headers, json=update_data, timeout=30)
                if response.status_code == 200:
                    print("✅ PATCH Update User:")
                    print(f"   Status: {response.status_code}")
                
                # Test 5: Delete user (matching Flutter's deleteUser method)
                response = requests.delete(f"{USERS_ENDPOINT}{user_id}/", headers=headers, timeout=30)
                if response.status_code == 204:
                    print("✅ DELETE User:")
                    print(f"   Status: {response.status_code}")
                    
        elif response.status_code == 400:
            error_data = response.json()
            if "email" in error_data.get("errors", {}):
                print("✅ POST Create User (email validation working):")
                print(f"   Status: {response.status_code}")
                print("   Email validation prevents duplicate")
            else:
                print(f"❌ POST Create User failed: {response.status_code}")
                print(f"   Error: {error_data}")
        else:
            print(f"❌ POST Create User failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST Create User error: {e}")
    
    # Test 6: API Key Info (matching Flutter's potential API key validation)
    try:
        response = requests.get(f"{BASE_URL}/users/api-key/info/", headers=headers, timeout=30)
        if response.status_code == 200:
            key_info = response.json()
            print("✅ GET API Key Info:")
            print(f"   Status: {response.status_code}")
            print(f"   Key Name: {key_info.get('key_name')}")
            print(f"   Rate Limit: {key_info.get('rate_limit')}")
            print(f"   Permissions: {key_info.get('permissions')}")
    except Exception as e:
        print(f"❌ GET API Key Info error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Flutter-Backend Integration Test Complete!")

if __name__ == "__main__":
    test_flutter_integration()
