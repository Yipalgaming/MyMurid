#!/usr/bin/env python3
"""
Script to add role column to online Render database
This script should be run on Render or with the Render DATABASE_URL
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def add_role_column_to_render_db():
    # Use Render DATABASE_URL from environment
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not found")
        print("Make sure you're running this on Render or have DATABASE_URL set")
        return
    
    print(f"Connecting to Render database...")
    print(f"Database URL: {DATABASE_URL[:50]}...")  # Show partial URL for security
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if role column exists
            result = connection.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='student_info' AND column_name='role'"))
            if result.fetchone():
                print("✅ Role column already exists in student_info table")
            else:
                # Add role column
                connection.execute(text("ALTER TABLE student_info ADD COLUMN role VARCHAR(50) DEFAULT 'student'"))
                connection.commit()
                print("✅ Added role column to student_info table")
            
            # Check current students
            result = connection.execute(text("SELECT id, name, ic_number, role FROM student_info"))
            students = result.fetchall()
            
            print(f"\nCurrent students in online database:")
            for student in students:
                print(f"  - ID: {student[0]}, Name: {student[1]}, IC: {student[2]}, Role: {student[3]}")
            
            # Update roles for existing students
            role_updates = [
                ("1234", "staff"),   # Ahmad Ali - staff
                ("0415", "student"), # Sean Chuah Shang En - student  
                ("9999", "admin")    # Admin/Teacher - admin
            ]
            
            for ic_number, role in role_updates:
                connection.execute(text(f"UPDATE student_info SET role = '{role}' WHERE ic_number = '{ic_number}'"))
                print(f"✅ Updated IC {ic_number} to role '{role}'")
            
            connection.commit()
            print("✅ All role updates committed successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()
        print("Database connection closed")

if __name__ == "__main__":
    add_role_column_to_render_db()
