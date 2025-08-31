#!/usr/bin/env python3
"""
Detailed Render Test
Test the Render deployment with more detailed diagnostics
"""

import requests
import time
import json

def test_render_deployment():
    """Test Render deployment with detailed diagnostics"""
    
    print("🔍 DETAILED RENDER DEPLOYMENT TEST")
    print("=" * 60)
    
    base_url = "https://mymurid.onrender.com"
    
    # Test 1: Basic page loading
    print("📋 Test 1: Basic Page Loading")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/", timeout=15)
        print(f"✅ Home page: Status {response.status_code}")
        
        if response.status_code == 200:
            print("   Content length:", len(response.text))
            if "login" in response.text.lower():
                print("   ✅ Login link found in content")
            else:
                print("   ⚠️  Login link not found")
    except Exception as e:
        print(f"❌ Home page error: {e}")
    
    # Test 2: Login page
    print("\n📋 Test 2: Login Page")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/login", timeout=15)
        print(f"✅ Login page: Status {response.status_code}")
        
        if response.status_code == 200:
            print("   Content length:", len(response.text))
            if "ic_number" in response.text.lower():
                print("   ✅ IC number input field found")
            else:
                print("   ⚠️  IC number input field not found")
    except Exception as e:
        print(f"❌ Login page error: {e}")
    
    # Test 3: Try to log in with student
    print("\n📋 Test 3: Student Login Attempt")
    print("-" * 40)
    
    try:
        login_data = {
            'ic_number': '1234',
            'password': 'student123'
        }
        
        response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False, timeout=15)
        print(f"✅ Login POST: Status {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Login successful (redirect)")
            print(f"   Redirect to: {response.headers.get('Location', 'None')}")
        elif response.status_code == 200:
            print("   ⚠️  Login returned 200 (might be error page)")
            # Check for error messages
            if "error" in response.text.lower():
                print("   ❌ Error message detected")
            elif "invalid" in response.text.lower():
                print("   ❌ Invalid credentials message")
            else:
                print("   ✅ No error messages found")
        elif response.status_code == 500:
            print("   ❌ Internal Server Error!")
            print("   🔧 This means the DATABASE_URL environment variable is not working")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 4: Check response headers
    print("\n📋 Test 4: Response Headers")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/", timeout=15)
        print("Response headers:")
        for key, value in response.headers.items():
            if key.lower() in ['server', 'x-powered-by', 'content-type', 'date']:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Header check error: {e}")
    
    # Test 5: Check if it's a caching issue
    print("\n📋 Test 5: Cache Bypass Test")
    print("-" * 40)
    
    try:
        # Add cache-busting parameter
        cache_bust_url = f"{base_url}/login?t={int(time.time())}"
        response = requests.get(cache_bust_url, timeout=15)
        print(f"✅ Cache-busting test: Status {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page loads with cache-busting")
        else:
            print(f"   ⚠️  Still getting status {response.status_code}")
    except Exception as e:
        print(f"❌ Cache-busting error: {e}")

def show_troubleshooting_steps():
    """Show troubleshooting steps"""
    
    print("\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING STEPS")
    print("=" * 60)
    
    print("\n📋 If DATABASE_URL is set but still getting 500 errors:")
    print("1. ✅ Verify environment variable is exactly:")
    print("   DATABASE_URL=postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require")
    
    print("\n2. 🔄 Force a complete redeploy:")
    print("   • Go to Render dashboard")
    print("   • Click 'Manual Deploy'")
    print("   • Wait for full deployment (5+ minutes)")
    
    print("\n3. 🗑️  Clear any cached environment variables:")
    print("   • Delete the DATABASE_URL variable")
    print("   • Save changes")
    print("   • Add it back")
    print("   • Redeploy")
    
    print("\n4. 🔍 Check deployment logs:")
    print("   • Look for any error messages")
    print("   • Check if environment variables are loaded")
    
    print("\n5. 🧪 Test with a simple database connection:")
    print("   • The issue might be in the app code, not the connection")

def main():
    """Run the detailed test"""
    
    test_render_deployment()
    show_troubleshooting_steps()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Run this test to see detailed results")
    print("2. Check your Render environment variables")
    print("3. Force a complete redeploy")
    print("4. If still failing, check deployment logs")

if __name__ == "__main__":
    main()
