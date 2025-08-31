#!/usr/bin/env python3
"""
Simple database setup script for MyMurid
Creates sample data for testing the system
"""

from app import app, db
from models import StudentInfo, MenuItem, Order, Vote, Feedback
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if data already exists
        if StudentInfo.query.first():
            print("✅ Database already has data. Skipping sample data creation.")
            return
        
        print("🚀 Creating sample data...")
        
        # Create sample students
        students = [
            StudentInfo(
                name="Ahmad bin Ali",
                ic_number="1234",
                pin="1234",
                role="student",
                balance=50
            ),
            StudentInfo(
                name="Sean Chuah Shang En",
                ic_number="0415",
                pin="0415",
                role="student",
                balance=25
            ),
            StudentInfo(
                name="Admin Teacher",
                ic_number="9999",
                pin="9999",
                password="adminpass",
                role="admin",
                balance=0
            )
        ]
        
        for student in students:
            db.session.add(student)
        
        # Create sample menu items
        menu_items = [
            MenuItem(
                name="Nasi Lemak",
                price=3.50,
                category="Main Course",
                image_filename="nasi_lemak.jpg"
            ),
            MenuItem(
                name="Chicken Rice",
                price=4.00,
                category="Main Course",
                image_filename="chicken_rice.jpg"
            ),
            MenuItem(
                name="Teh Tarik",
                price=1.50,
                category="Beverages",
                image_filename="teh_tarik.jpg"
            ),
            MenuItem(
                name="Roti Canai",
                price=1.20,
                category="Snacks",
                image_filename="roti_canai.jpg"
            )
        ]
        
        for item in menu_items:
            db.session.add(item)
        
        # Commit all data
        db.session.commit()
        
        print("✅ Sample data created successfully!")
        print("\n📋 Sample Login Credentials:")
        print("Student 1: IC: 1234, PIN: 1234")
        print("Student 2: IC: 0415, PIN: 0415")
        print("Admin: IC: 9999, PIN: 9999, Password: adminpass")
        print("\n🍽️ Sample Menu Items:")
        for item in menu_items:
            print(f"- {item.name}: RM{item.price} ({item.category})")

def check_database():
    """Check database status"""
    with app.app_context():
        try:
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Database tables: {', '.join(tables)}")
            
            # Check data counts
            student_count = StudentInfo.query.count()
            menu_count = MenuItem.query.count()
            print(f"👥 Students: {student_count}")
            print(f"🍽️ Menu items: {menu_count}")
            
        except Exception as e:
            print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🚀 MyMurid Database Setup")
    print("=" * 40)
    
    try:
        check_database()
        print("\n" + "=" * 40)
        create_sample_data()
        print("\n" + "=" * 40)
        check_database()
        
        print("\n🎉 Setup complete! You can now:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Login with sample credentials above")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
