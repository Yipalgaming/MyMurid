#!/usr/bin/env python3
"""
Script to update existing staff user password
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, StudentInfo

def update_staff_password():
    with app.app_context():
        try:
            # Find existing staff user
            staff_user = StudentInfo.query.filter_by(ic_number='9999').first()
            if not staff_user:
                print("❌ Staff user not found")
                return
            
            # Update password
            staff_user.set_password("adminpass")
            db.session.commit()
            
            print("✅ Staff user password updated successfully!")
            print(f"Name: {staff_user.name}")
            print("IC: 9999")
            print("PIN: 9999")
            print("Password: adminpass")
            print("Role: staff")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating staff user password: {e}")

if __name__ == "__main__":
    update_staff_password()
