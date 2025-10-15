#!/usr/bin/env python3
"""
Test script to verify CSRF protection is working correctly.
"""

import requests
from bs4 import BeautifulSoup

def test_csrf_protection():
    """Test that CSRF protection is working"""
    print("🧪 TESTING CSRF PROTECTION")
    print("=" * 35)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test 1: Get login page and check for CSRF token
        print("1. Testing login page CSRF token...")
        response = requests.get(f"{base_url}/login")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            
            if csrf_input and csrf_input.get('value'):
                print("✅ CSRF token found in login form")
                csrf_token = csrf_input.get('value')
            else:
                print("❌ CSRF token missing from login form")
                return False
        else:
            print(f"❌ Login page returned status {response.status_code}")
            return False
        
        # Test 2: Try to login without CSRF token (should fail)
        print("\n2. Testing login without CSRF token...")
        login_data = {
            'ic': '1234',
            'pin': '1234'
        }
        
        response = requests.post(f"{base_url}/login", data=login_data)
        
        if response.status_code == 400:
            print("✅ CSRF protection working - request rejected without token")
        else:
            print(f"❌ CSRF protection not working - status {response.status_code}")
            return False
        
        # Test 3: Try to login with CSRF token (should work)
        print("\n3. Testing login with CSRF token...")
        login_data_with_csrf = {
            'csrf_token': csrf_token,
            'ic': '1234',
            'pin': '1234'
        }
        
        response = requests.post(f"{base_url}/login", data=login_data_with_csrf, allow_redirects=False)
        
        if response.status_code in [200, 302]:
            print("✅ Login with CSRF token successful")
        else:
            print(f"❌ Login with CSRF token failed - status {response.status_code}")
            return False
        
        print("\n🎉 ALL CSRF TESTS PASSED!")
        print("✅ CSRF protection is working correctly")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_csrf_protection()
    
    if success:
        print("\n🔒 SECURITY STATUS: SECURE")
        print("Your application is now protected against CSRF attacks!")
    else:
        print("\n⚠️  SECURITY STATUS: NEEDS ATTENTION")
        print("Please check the CSRF configuration.")
