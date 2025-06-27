#!/usr/bin/env python3
"""
Comprehensive test script for input validation and sanitization
"""
import requests
import json
import base64
import io
from PIL import Image

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU"

# Headers with API key
headers = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json"
}

def test_valid_user_creation():
    """Test creating a user with valid data"""
    print("🧪 Testing valid user creation...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "address": "123 Main Street\nAnytown, USA 12345",
        "age": 30
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Valid user created successfully")
        data = response.json()
        print(f"Created user: {data.get('user', {}).get('name')}")
        return data.get('user', {}).get('id')
    else:
        print(f"❌ Failed: {response.text}")
    print()
    return None

def test_sql_injection_attempts():
    """Test SQL injection prevention"""
    print("🛡️  Testing SQL injection prevention...")
    
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "admin'; SELECT * FROM users WHERE '1'='1",
        "Robert'); DELETE FROM users; --",
        "' OR 1=1 --",
        "UNION SELECT password FROM auth_user --"
    ]
    
    for malicious_input in malicious_inputs:
        user_data = {
            "name": malicious_input,
            "email": "test@example.com",
            "age": 25
        }
        
        response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
        
        if response.status_code == 400:
            print(f"✅ SQL injection blocked: {malicious_input[:30]}...")
        else:
            print(f"❌ SQL injection not blocked: {malicious_input[:30]}...")
            print(f"Response: {response.status_code} - {response.text[:100]}")
    
    print()

def test_xss_prevention():
    """Test XSS attack prevention"""
    print("🛡️  Testing XSS prevention...")
    
    xss_inputs = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "{{7*7}}",
        "<svg onload=alert('XSS')>",
        "&#60;script&#62;alert('XSS')&#60;/script&#62;"
    ]
    
    for xss_input in xss_inputs:
        user_data = {
            "name": xss_input,
            "email": "xss.test@example.com",
            "age": 25
        }
        
        response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
        
        if response.status_code == 400 or (response.status_code == 201 and xss_input not in response.text):
            print(f"✅ XSS blocked/sanitized: {xss_input[:30]}...")
        else:
            print(f"❌ XSS not blocked: {xss_input[:30]}...")
            print(f"Response: {response.status_code} - {response.text[:100]}")
    
    print()

def test_input_length_limits():
    """Test input length restrictions"""
    print("📏 Testing input length limits...")
    
    # Test extremely long name
    long_name = "A" * 1000
    user_data = {
        "name": long_name,
        "email": "long.name@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    if response.status_code == 400:
        print("✅ Long name rejected")
    else:
        print(f"❌ Long name accepted: {response.status_code}")
    
    # Test extremely long email
    long_email = "a" * 300 + "@example.com"
    user_data = {
        "name": "Test User",
        "email": long_email
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    if response.status_code == 400:
        print("✅ Long email rejected")
    else:
        print(f"❌ Long email accepted: {response.status_code}")
    
    # Test extremely long address
    long_address = "Very long address " * 100
    user_data = {
        "name": "Test User",
        "email": "address.test@example.com",
        "address": long_address
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    if response.status_code == 400:
        print("✅ Long address rejected")
    else:
        print(f"❌ Long address accepted: {response.status_code}")
    
    print()

def test_email_validation():
    """Test email validation"""
    print("📧 Testing email validation...")
    
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "user@",
        "user..name@example.com",
        "user@example",
        "user@.example.com",
        "user@example..com",
        "",
        "user@tempmail.org",  # Blocked domain
        "user@10minutemail.com"  # Blocked domain
    ]
    
    for email in invalid_emails:
        user_data = {
            "name": "Test User",
            "email": email
        }
        
        response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
        if response.status_code == 400:
            print(f"✅ Invalid email rejected: {email}")
        else:
            print(f"❌ Invalid email accepted: {email}")
    
    print()

def test_age_validation():
    """Test age validation"""
    print("🎂 Testing age validation...")
    
    invalid_ages = [-1, 200, "abc", 999]
    
    for age in invalid_ages:
        user_data = {
            "name": "Test User",
            "email": f"age.test.{age}@example.com",
            "age": age
        }
        
        response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
        if response.status_code == 400:
            print(f"✅ Invalid age rejected: {age}")
        else:
            print(f"❌ Invalid age accepted: {age}")
    
    print()

def test_phone_validation():
    """Test phone number validation"""
    print("📞 Testing phone number validation...")
    
    invalid_phones = [
        "123",  # Too short
        "12345678901234567890",  # Too long
        "abc-def-ghij",  # Letters
        "123-456-7890-1234-5678",  # Too many parts
        "+",  # Just plus
        "++1234567890",  # Multiple plus signs
    ]
    
    for phone in invalid_phones:
        user_data = {
            "name": "Test User",
            "email": f"phone.test@example.com",
            "phone_number": phone
        }
        
        response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
        if response.status_code == 400:
            print(f"✅ Invalid phone rejected: {phone}")
        else:
            print(f"❌ Invalid phone accepted: {phone}")
    
    print()

def test_large_request_blocking():
    """Test blocking of oversized requests"""
    print("📦 Testing large request blocking...")
    
    # Create a very large JSON payload
    large_data = {
        "name": "Test User",
        "email": "large.request@example.com",
        "address": "A" * (1024 * 1024),  # 1MB address
        "extra_data": "B" * (1024 * 1024)  # Extra 1MB data
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=large_data)
    if response.status_code == 413 or response.status_code == 400:
        print("✅ Large request blocked")
    else:
        print(f"❌ Large request accepted: {response.status_code}")
    
    print()

def test_malicious_json_structure():
    """Test blocking of malicious JSON structures"""
    print("🔧 Testing malicious JSON structure blocking...")
    
    # Test deeply nested JSON
    nested_data = {"name": "Test User", "email": "nested@example.com"}
    for i in range(20):  # Create 20 levels of nesting
        nested_data = {"level": i, "data": nested_data}
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=nested_data)
    if response.status_code == 400:
        print("✅ Deeply nested JSON blocked")
    else:
        print(f"❌ Deeply nested JSON accepted: {response.status_code}")
    
    # Test JSON with too many keys
    many_keys_data = {
        "name": "Test User",
        "email": "many.keys@example.com"
    }
    for i in range(200):  # Add 200 extra keys
        many_keys_data[f"extra_field_{i}"] = f"value_{i}"
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=many_keys_data)
    if response.status_code == 400:
        print("✅ JSON with too many keys blocked")
    else:
        print(f"❌ JSON with too many keys accepted: {response.status_code}")
    
    print()

def test_duplicate_email_prevention():
    """Test duplicate email prevention"""
    print("👥 Testing duplicate email prevention...")
    
    # First, create a user
    user_data = {
        "name": "Original User",
        "email": "duplicate.test@example.com"
    }
    
    response1 = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data)
    print(f"First user creation: {response1.status_code}")
    
    # Try to create another user with the same email
    user_data2 = {
        "name": "Duplicate User",
        "email": "duplicate.test@example.com"  # Same email
    }
    
    response2 = requests.post(f"{BASE_URL}/api/users/", headers=headers, json=user_data2)
    if response2.status_code == 400:
        print("✅ Duplicate email rejected")
    else:
        print(f"❌ Duplicate email accepted: {response2.status_code}")
    
    print()

def test_content_type_validation():
    """Test content type validation"""
    print("📄 Testing content type validation...")
    
    # Try to send data with wrong content type
    user_data = "name=Test&email=test@example.com"
    
    wrong_headers = {
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "text/plain"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/", headers=wrong_headers, data=user_data)
    if response.status_code == 400:
        print("✅ Invalid content type rejected")
    else:
        print(f"❌ Invalid content type accepted: {response.status_code}")
    
    print()

def cleanup_test_users():
    """Clean up test users"""
    print("🧹 Cleaning up test users...")
    
    # Get all users
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    if response.status_code == 200:
        users = response.json().get('results', [])
        
        # Delete test users
        for user in users:
            if 'test' in user.get('email', '').lower() or 'example.com' in user.get('email', ''):
                delete_response = requests.delete(
                    f"{BASE_URL}/api/users/{user['id']}/",
                    headers=headers
                )
                if delete_response.status_code == 200:
                    print(f"Deleted test user: {user.get('email')}")
    
    print()

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Input Validation Tests")
    print("=" * 60)
    
    try:
        # Run all validation tests
        test_valid_user_creation()
        test_sql_injection_attempts()
        test_xss_prevention()
        test_input_length_limits()
        test_email_validation()
        test_age_validation()
        test_phone_validation()
        test_large_request_blocking()
        test_malicious_json_structure()
        test_duplicate_email_prevention()
        test_content_type_validation()
        
        # Clean up
        cleanup_test_users()
        
        print("✅ All validation tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
