#!/usr/bin/env python3
"""
Script to create a staff user for local testing
Run this script to create a staff user with IC: 9999, PIN: 9999
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, StudentInfo
from werkzeug.security import generate_password_hash

def create_staff_user():
    with app.app_context():
        try:
            # Check if staff user already exists
            existing_staff = StudentInfo.query.filter_by(ic_number='9999').first()
            if existing_staff:
                print(f"Staff user already exists: {existing_staff.name}")
                return
            
            # Create new staff user
            staff_user = StudentInfo(
                name="Staff User",
                ic_number="9999",
                role="staff",
                balance=1000.00,
                frozen=False,
                total_points=0,
                available_points=0
            )
            
            # Set PIN
            staff_user.set_pin("9999")
            
            # Set password (for staff login)
            staff_user.set_password("adminpass")
            
            # Add to database
            db.session.add(staff_user)
            db.session.commit()
            
            print("✅ Staff user created successfully!")
            print("IC: 9999")
            print("PIN: 9999")
            print("Password: adminpass")
            print("Role: staff")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating staff user: {e}")

if __name__ == "__main__":
    create_staff_user()
