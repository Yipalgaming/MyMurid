#!/usr/bin/env python3
"""
Fix database schema using SQLAlchemy
"""

from app import app, db
from models import StudentInfo
from sqlalchemy import text

def fix_database_schema():
    with app.app_context():
        try:
            print("Connected to database")
            
            # Check if pin_hash column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'pin_hash'
            """))
            
            if result.fetchone():
                print("pin_hash column already exists")
            else:
                print("Adding pin_hash column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN pin_hash VARCHAR(255)
                """))
                print("pin_hash column added successfully")
            
            # Check if password_hash column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'password_hash'
            """))
            
            if result.fetchone():
                print("password_hash column already exists")
            else:
                print("Adding password_hash column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN password_hash VARCHAR(255)
                """))
                print("password_hash column added successfully")
            
            # Check if role column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'role'
            """))
            
            if result.fetchone():
                print("role column already exists")
            else:
                print("Adding role column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN role VARCHAR(50) DEFAULT 'student'
                """))
                print("role column added successfully")
            
            # Check if frozen column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'frozen'
            """))
            
            if result.fetchone():
                print("frozen column already exists")
            else:
                print("Adding frozen column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN frozen BOOLEAN DEFAULT FALSE
                """))
                print("frozen column added successfully")
            
            # Check if total_points column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'total_points'
            """))
            
            if result.fetchone():
                print("total_points column already exists")
            else:
                print("Adding total_points column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN total_points INTEGER DEFAULT 0
                """))
                print("total_points column added successfully")
            
            # Check if available_points column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'student_info' AND column_name = 'available_points'
            """))
            
            if result.fetchone():
                print("available_points column already exists")
            else:
                print("Adding available_points column to student_info table...")
                db.session.execute(text("""
                    ALTER TABLE student_info 
                    ADD COLUMN available_points INTEGER DEFAULT 0
                """))
                print("available_points column added successfully")
            
            # Commit all changes
            db.session.commit()
            
            # Show current table structure
            print("\nCurrent student_info table structure:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'student_info'
                ORDER BY ordinal_position
            """))
            
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            
            print("\nDatabase schema fix completed successfully!")
            
        except Exception as e:
            print(f"Error fixing database schema: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_database_schema()
