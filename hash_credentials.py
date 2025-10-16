#!/usr/bin/env python3
"""
Script to hash PINs and passwords for existing users
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, StudentInfo

def hash_existing_credentials():
    with app.app_context():
        try:
            print("Hashing PINs and passwords for existing users...")
            print("=" * 50)
            
            # Get all users
            users = StudentInfo.query.all()
            
            if not users:
                print("No users found in database")
                return
            
            print(f"Found {len(users)} users:")
            
            for user in users:
                print(f"\n👤 Processing {user.name} (IC: {user.ic_number}, Role: {user.role})")
                
                # Set default PIN if not already hashed
                if not user.pin_hash:
                    user.set_pin("1234")  # Default PIN
                    print(f"   ✅ Set PIN hash for {user.name}")
                else:
                    print(f"   ℹ️  PIN already hashed")
                
                # Set default password for admin/staff if not already hashed
                if user.role in ['admin', 'staff'] and not user.password_hash:
                    user.set_password("adminpass")  # Default password
                    print(f"   ✅ Set password hash for {user.name}")
                elif user.role in ['admin', 'staff'] and user.password_hash:
                    print(f"   ℹ️  Password already hashed")
                else:
                    print(f"   ℹ️  Student role - no password needed")
            
            # Commit all changes
            db.session.commit()
            print(f"\n✅ All PINs and passwords hashed successfully!")
            
            # Verify the hashing worked
            print(f"\n🔍 Verification:")
            for user in users:
                pin_test = user.check_pin("1234")
                print(f"   {user.name}: PIN '1234' check = {pin_test}")
                
                if user.role in ['admin', 'staff']:
                    password_test = user.check_password("adminpass")
                    print(f"   {user.name}: Password 'adminpass' check = {password_test}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    hash_existing_credentials()
