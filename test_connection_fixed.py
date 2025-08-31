#!/usr/bin/env python3
"""
Test Render Connection - Fixed Version
Test if the app can connect to the Render database
"""

import os

# Set environment variables BEFORE importing anything else
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

def test_connection():
    """Test database connection"""
    
    print("🧪 Testing Render Database Connection...")
    print(f"🔧 DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    # Create Flask app
    app = Flask(__name__)
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    print(f"📊 Configuration: {config_name}")
    print(f"🔗 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize database
    db = SQLAlchemy(app)
    
    try:
        with app.app_context():
            # Test connection
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            print("✅ Database connection successful!")
            
            # Test query
            result = db.session.execute(db.text("SELECT COUNT(*) FROM student_info")).fetchone()
            student_count = result[0]
            print(f"👥 Found {student_count} students in database")
            
            # Show students
            result = db.session.execute(db.text("SELECT ic_number, name, balance FROM student_info ORDER BY id")).fetchall()
            print("\n📋 Students in database:")
            for student in result:
                print(f"  IC: {student[0]}, Name: {student[1]}, Balance: RM{student[2]}")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Connection test passed! Your app should work on Render.")
        print("\n📋 To fix your Render deployment:")
        print("1. Go to your Render dashboard")
        print("2. Click on your web service")
        print("3. Go to 'Environment' tab")
        print("4. Add this environment variable:")
        print("   DATABASE_URL=postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require")
        print("5. Redeploy your service")
    else:
        print("\n💥 Connection test failed! Check your environment variables.")
