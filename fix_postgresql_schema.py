#!/usr/bin/env python3
"""
Fix PostgreSQL database schema using SQLAlchemy
"""

from app import app, db
from models import StudentInfo
from sqlalchemy import text

def fix_postgresql_schema():
    with app.app_context():
        try:
            print("Connected to PostgreSQL database")
            
            # Create all tables if they don't exist
            db.create_all()
            print("All tables created/updated")
            
            # Check if we have any students
            students = StudentInfo.query.all()
            print(f"Found {len(students)} students in database")
            
            # If no students, create some sample data
            if len(students) == 0:
                print("Creating sample students...")
                
                # Create student
                student = StudentInfo(
                    name="Sean Chuah Shang En",
                    ic_number="0415",
                    pin_hash="pbkdf2:sha256:600000$abc123$def456",
                    password_hash="pbkdf2:sha256:600000$xyz789$ghi012",
                    role="student",
                    balance=50.0,
                    frozen=False,
                    total_points=100,
                    available_points=80
                )
                db.session.add(student)
                
                # Create staff
                staff = StudentInfo(
                    name="Ali",
                    ic_number="1234",
                    pin_hash="pbkdf2:sha256:600000$staff123$staff456",
                    password_hash="pbkdf2:sha256:600000$admin123$admin456",
                    role="staff",
                    balance=0.0,
                    frozen=False,
                    total_points=0,
                    available_points=0
                )
                db.session.add(staff)
                
                # Create admin
                admin = StudentInfo(
                    name="Admin/Teacher",
                    ic_number="9999",
                    pin_hash="pbkdf2:sha256:600000$admin123$admin456",
                    password_hash="pbkdf2:sha256:600000$admin123$admin456",
                    role="admin",
                    balance=0.0,
                    frozen=False,
                    total_points=0,
                    available_points=0
                )
                db.session.add(admin)
                
                db.session.commit()
                print("Sample students created successfully")
            
            # Show current students
            print("\nCurrent students in database:")
            students = StudentInfo.query.all()
            for student in students:
                print(f"  {student.name} (IC: {student.ic_number}, Role: {student.role})")
            
            print("\nPostgreSQL database schema fix completed successfully!")
            
        except Exception as e:
            print(f"Error fixing database schema: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_postgresql_schema()
