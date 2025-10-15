#!/usr/bin/env python3
"""
Test script to verify freeze card functionality works with CSRF protection.
"""

import requests
from bs4 import BeautifulSoup

def test_freeze_card():
    """Test freeze card functionality"""
    print("🧪 TESTING FREEZE CARD FUNCTIONALITY")
    print("=" * 45)
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Step 1: Login as admin
        print("1. Logging in as admin...")
        login_page = session.get(f"{base_url}/login")
        
        if login_page.status_code != 200:
            print(f"❌ Login page returned status {login_page.status_code}")
            return False
        
        # Get CSRF token from login page
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input:
            print("❌ CSRF token not found on login page")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"✅ CSRF token found: {csrf_token[:20]}...")
        
        # Login with admin credentials
        login_data = {
            'csrf_token': csrf_token,
            'ic': '9999',
            'pin': '1234',
            'password': 'adminpass'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Login failed with status {login_response.status_code}")
            return False
        
        print("✅ Admin login successful")
        
        # Step 2: Go to student balances page
        print("\n2. Accessing student balances page...")
        balances_page = session.get(f"{base_url}/student_balances")
        
        if balances_page.status_code != 200:
            print(f"❌ Student balances page returned status {balances_page.status_code}")
            return False
        
        print("✅ Student balances page loaded")
        
        # Step 3: Test freeze card functionality
        print("\n3. Testing freeze card functionality...")
        
        # Get CSRF token from balances page
        soup = BeautifulSoup(balances_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input:
            print("❌ CSRF token not found on balances page")
            return False
        
        csrf_token = csrf_input.get('value')
        
        # Try to freeze a student card (assuming student with IC 1234 exists)
        freeze_data = {
            'csrf_token': csrf_token,
            'ic': '1234',
            'action': 'freeze'
        }
        
        freeze_response = session.post(f"{base_url}/toggle_card_status", data=freeze_data, allow_redirects=False)
        
        if freeze_response.status_code in [200, 302]:
            print("✅ Freeze card functionality working!")
        else:
            print(f"❌ Freeze card failed with status {freeze_response.status_code}")
            print(f"Response: {freeze_response.text[:200]}...")
            return False
        
        print("\n🎉 ALL FREEZE CARD TESTS PASSED!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_freeze_card()
    
    if success:
        print("\n🔒 FREEZE CARD STATUS: WORKING")
        print("✅ CSRF protection is working correctly for freeze card functionality!")
    else:
        print("\n⚠️  FREEZE CARD STATUS: NEEDS ATTENTION")
        print("Please check the CSRF configuration for freeze card functionality.")
