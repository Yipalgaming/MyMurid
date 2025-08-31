#!/usr/bin/env python3
"""
Test Login Page
Test specific pages to find where the Internal Server Error occurs
"""

import requests
import time

def test_page(url, page_name):
    """Test a specific page and report the result"""
    
    try:
        print(f"🔍 Testing {page_name}: {url}")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ {page_name}: Working (200 OK)")
            return True
        elif response.status_code == 500:
            print(f"❌ {page_name}: Internal Server Error (500)")
            return False
        elif response.status_code == 404:
            print(f"⚠️  {page_name}: Not Found (404)")
            return False
        else:
            print(f"⚠️  {page_name}: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {page_name}: Connection Error - {e}")
        return False

def main():
    """Test all important pages"""
    
    print("🚀 TESTING RENDER WEBSITE PAGES")
    print("=" * 60)
    
    base_url = "https://mymurid.onrender.com"
    
    # Test different pages
    pages_to_test = [
        (f"{base_url}/", "Home Page"),
        (f"{base_url}/login", "Login Page"),
        (f"{base_url}/dashboard", "Dashboard (should redirect)"),
        (f"{base_url}/menu", "Menu Page"),
        (f"{base_url}/order", "Order Page"),
        (f"{base_url}/profile", "Profile Page"),
    ]
    
    results = []
    
    for url, page_name in pages_to_test:
        result = test_page(url, page_name)
        results.append((page_name, result))
        time.sleep(1)  # Wait between requests
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    working_pages = 0
    total_pages = len(results)
    
    for page_name, result in results:
        status = "✅ Working" if result else "❌ Failed"
        print(f"{page_name}: {status}")
        if result:
            working_pages += 1
    
    print(f"\n🎯 Overall: {working_pages}/{total_pages} pages working")
    
    if working_pages == total_pages:
        print("🎉 All pages are working! Your website is fully functional.")
        print("\n💡 If you're still seeing Internal Server Error:")
        print("   • Try refreshing the page")
        print("   • Clear your browser cache")
        print("   • Try a different browser")
    else:
        print("🔧 Some pages have issues. Check the details above.")
        print("\n💡 Common causes of Internal Server Error:")
        print("   • Database connection timeout")
        print("   • Missing environment variables")
        print("   • Code errors in specific routes")

if __name__ == "__main__":
    main()
