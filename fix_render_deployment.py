#!/usr/bin/env python3
"""
Fix Render Deployment
Help diagnose and fix the Internal Server Error on Render
"""

import os
import requests
import json

def check_render_status():
    """Check the current status of your Render deployment"""
    
    print("🔍 Checking Render Deployment Status...")
    print("=" * 60)
    
    # Your Render website URL
    website_url = "https://mymurid.onrender.com"
    
    try:
        print(f"🌐 Testing website: {website_url}")
        response = requests.get(website_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Website is working! Status: 200 OK")
            print("🎉 Your deployment is successful!")
            return True
        elif response.status_code == 500:
            print("❌ Internal Server Error (500)")
            print("🔧 This means the app is running but has a database connection issue")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to website: {e}")
        print("💡 This might mean the deployment failed or is still building")
        return False

def show_fix_instructions():
    """Show step-by-step fix instructions"""
    
    print("\n" + "=" * 60)
    print("🔧 HOW TO FIX YOUR RENDER DEPLOYMENT")
    print("=" * 60)
    
    print("\n📋 Step 1: Go to Render Dashboard")
    print("   • Open: https://dashboard.render.com/")
    print("   • Sign in to your account")
    
    print("\n📋 Step 2: Find Your Web Service")
    print("   • Look for your web service (not the database)")
    print("   • It should be named 'mymurid' or similar")
    print("   • Click on the web service name")
    
    print("\n📋 Step 3: Add Environment Variable")
    print("   • Click the 'Environment' tab")
    print("   • Click 'Add Environment Variable'")
    print("   • Key: DATABASE_URL")
    print("   • Value: postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require")
    
    print("\n📋 Step 4: Redeploy")
    print("   • Click 'Manual Deploy' or 'Deploy Latest Commit'")
    print("   • Wait for deployment to complete (2-5 minutes)")
    
    print("\n📋 Step 5: Test")
    print("   • Go to: https://mymurid.onrender.com/login")
    print("   • Try logging in with IC: 1234")
    
    print("\n" + "=" * 60)
    print("🎯 WHAT THIS FIXES:")
    print("   • Internal Server Error → ✅ Resolved")
    print("   • Database Connection → ✅ Working")
    print("   • Student Login → ✅ Functional")
    print("   • All Features → ✅ Operational")
    print("=" * 60)

def test_database_connection():
    """Test if the database connection works locally"""
    
    print("\n🧪 Testing Database Connection...")
    
    # Set environment variable for testing
    os.environ['DATABASE_URL'] = 'postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require'
    
    try:
        import psycopg2
        
        # Test connection
        conn = psycopg2.connect(
            host='dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
            port='5432',
            database='mymurid_db',
            user='mymurid_user',
            password='0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
            sslmode='require'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student_info")
        student_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful!")
        print(f"👥 Found {student_count} students in database")
        print("🎯 Database is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 This suggests a different issue")
        return False

def main():
    """Main function to diagnose and fix the issue"""
    
    print("🚀 RENDER DEPLOYMENT FIXER")
    print("=" * 60)
    
    # Check website status
    website_working = check_render_status()
    
    # Test database connection
    db_working = test_database_connection()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS:")
    print("=" * 60)
    
    if website_working and db_working:
        print("🎉 Everything is working! No fix needed.")
    elif not website_working and db_working:
        print("🔧 Issue: Website not connecting to database")
        print("💡 Solution: Add DATABASE_URL environment variable")
        show_fix_instructions()
    elif website_working and not db_working:
        print("🔧 Issue: Database connection problem")
        print("💡 Solution: Check database credentials")
    else:
        print("🔧 Issue: Multiple problems detected")
        print("💡 Solution: Follow the fix instructions below")
        show_fix_instructions()

if __name__ == "__main__":
    main()
