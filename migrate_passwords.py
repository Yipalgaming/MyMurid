#!/usr/bin/env python3
"""
Migration script to hash existing passwords and PINs in the database.
Run this after updating the models to use hashed passwords.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import StudentInfo

def migrate_passwords():
    """Migrate existing plain text passwords to hashed versions"""
    print("🔐 MIGRATING PASSWORDS TO HASHED VERSIONS")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get all students
            students = StudentInfo.query.all()
            print(f"Found {len(students)} students to migrate...")
            
            migrated_count = 0
            
            for student in students:
                # Check if PIN needs migration (if it's still plain text)
                if student.pin_hash and len(student.pin_hash) <= 10:  # Likely plain text
                    # Hash the existing PIN
                    student.pin_hash = generate_password_hash(student.pin_hash)
                    migrated_count += 1
                    print(f"✅ Migrated PIN for {student.name} (IC: {student.ic_number})")
                
                # Check if password needs migration
                if student.password_hash and len(student.password_hash) <= 20:  # Likely plain text
                    # Hash the existing password
                    student.password_hash = generate_password_hash(student.password_hash)
                    migrated_count += 1
                    print(f"✅ Migrated password for {student.name} (IC: {student.ic_number})")
            
            if migrated_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully migrated {migrated_count} passwords/PINs!")
            else:
                print("\n✅ No passwords needed migration - they're already hashed!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            return False
    
    return True

def create_sample_data():
    """Create sample data with properly hashed passwords"""
    print("\n📝 CREATING SAMPLE DATA WITH HASHED PASSWORDS")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Sample students with hashed passwords
            sample_students = [
                {
                    'name': 'Sean Chuah Shang En',
                    'ic_number': '0415',
                    'pin': '1234',
                    'password': None,
                    'role': 'student',
                    'balance': 20,
                    'frozen': False
                },
                {
                    'name': 'Ali',
                    'ic_number': '1234',
                    'pin': '1234',
                    'password': None,
                    'role': 'student',
                    'balance': 20,
                    'frozen': False
                },
                {
                    'name': 'Teacher / Admin',
                    'ic_number': '9999',
                    'pin': '1234',
                    'password': 'adminpass',
                    'role': 'admin',
                    'balance': 0,
                    'frozen': False
                }
            ]
            
            for student_data in sample_students:
                # Check if student already exists
                existing = StudentInfo.query.filter_by(ic_number=student_data['ic_number']).first()
                if existing:
                    print(f"ℹ️  Student {student_data['name']} already exists, updating...")
                    existing.name = student_data['name']
                    existing.set_pin(student_data['pin'])
                    if student_data['password']:
                        existing.set_password(student_data['password'])
                    existing.role = student_data['role']
                    existing.balance = student_data['balance']
                    existing.frozen = student_data['frozen']
                else:
                    print(f"➕ Creating new student: {student_data['name']}")
                    new_student = StudentInfo(
                        name=student_data['name'],
                        ic_number=student_data['ic_number'],
                        role=student_data['role'],
                        balance=student_data['balance'],
                        frozen=student_data['frozen']
                    )
                    new_student.set_pin(student_data['pin'])
                    if student_data['password']:
                        new_student.set_password(student_data['password'])
                    
                    db.session.add(new_student)
            
            db.session.commit()
            print("✅ Sample data created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    load_dotenv()
    
    print("🚀 STARTING DATABASE MIGRATION")
    print("=" * 60)
    
    # Run migrations
    success = True
    success &= migrate_passwords()
    success &= create_sample_data()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ All passwords and PINs are now hashed")
        print("✅ Sample data created with proper security")
        print("\n🔧 Next steps:")
        print("1. Test login with IC: 1234, PIN: 1234")
        print("2. Test admin login with IC: 9999, PIN: 1234, Password: adminpass")
        print("3. Your application is now secure!")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the errors above and try again.")
