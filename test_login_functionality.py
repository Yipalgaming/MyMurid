#!/usr/bin/env python3
"""
Test Login Functionality
Test the actual login process to see if that's where the error occurs
"""

import requests
import time

def test_login_process():
    """Test the login process step by step"""
    
    print("🔐 TESTING LOGIN FUNCTIONALITY")
    print("=" * 60)
    
    base_url = "https://mymurid.onrender.com"
    session = requests.Session()
    
    # Step 1: Get the login page
    print("📋 Step 1: Getting login page...")
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page loaded successfully")
        else:
            print(f"❌ Login page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting login page: {e}")
        return False
    
    # Step 2: Try to log in with a student IC
    print("\n📋 Step 2: Testing student login...")
    try:
        login_data = {
            'ic_number': '1234',  # Ahmad Ali's IC
            'password': 'student123'  # Default password
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✅ Student login successful (redirected)")
            print(f"   Redirect location: {response.headers.get('Location', 'None')}")
        elif response.status_code == 200:
            print("⚠️  Login returned 200 (might be showing error message)")
            # Check if there's an error message in the response
            if "error" in response.text.lower() or "invalid" in response.text.lower():
                print("   ❌ Login failed - error message detected")
            else:
                print("   ✅ Login might be working")
        elif response.status_code == 500:
            print("❌ Internal Server Error during login!")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False
    
    # Step 3: Try to access dashboard after login
    print("\n📋 Step 3: Testing dashboard access...")
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible after login")
        elif response.status_code == 302:
            print("⚠️  Dashboard redirecting (might be to login)")
        elif response.status_code == 404:
            print("⚠️  Dashboard not found (404)")
        elif response.status_code == 500:
            print("❌ Internal Server Error accessing dashboard!")
            return False
        else:
            print(f"⚠️  Dashboard status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return False
    
    # Step 4: Test admin login
    print("\n📋 Step 4: Testing admin login...")
    try:
        admin_data = {
            'ic_number': '9999',  # Admin Teacher's IC
            'password': 'adminpass'  # Admin password
        }
        
        response = session.post(f"{base_url}/login", data=admin_data, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Admin login successful (redirected)")
        elif response.status_code == 200:
            print("⚠️  Admin login returned 200")
        elif response.status_code == 500:
            print("❌ Internal Server Error during admin login!")
            return False
        else:
            print(f"⚠️  Admin login status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 LOGIN TEST COMPLETE")
    print("=" * 60)
    
    return True

def main():
    """Run the login functionality test"""
    
    success = test_login_process()
    
    if success:
        print("✅ Login functionality test completed successfully!")
        print("\n💡 If you're still seeing Internal Server Error:")
        print("   • The error might be intermittent")
        print("   • Try logging in multiple times")
        print("   • Check if it happens on specific actions")
        print("   • Clear browser cache and cookies")
    else:
        print("❌ Login functionality test failed!")
        print("\n🔧 This suggests the Internal Server Error is in the login process")

if __name__ == "__main__":
    main()
