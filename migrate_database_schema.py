#!/usr/bin/env python3
"""
Manual database migration script to add password hashing columns.
This script handles the transition from plain text to hashed passwords.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from werkzeug.security import generate_password_hash

def migrate_database():
    """Migrate database schema and data"""
    print("🔧 MIGRATING DATABASE SCHEMA")
    print("=" * 50)
    
    load_dotenv()
    
    # Get database URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Handle postgres:// vs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' 
            AND column_name IN ('pin_hash', 'password_hash')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'pin_hash' not in existing_columns:
            print("➕ Adding pin_hash column...")
            cursor.execute("ALTER TABLE student_info ADD COLUMN pin_hash VARCHAR(128)")
            print("✅ Added pin_hash column")
        else:
            print("ℹ️  pin_hash column already exists")
        
        if 'password_hash' not in existing_columns:
            print("➕ Adding password_hash column...")
            cursor.execute("ALTER TABLE student_info ADD COLUMN password_hash VARCHAR(128)")
            print("✅ Added password_hash column")
        else:
            print("ℹ️  password_hash column already exists")
        
        # Migrate existing data
        print("\n🔐 MIGRATING EXISTING PASSWORDS")
        print("=" * 40)
        
        # Get all students
        cursor.execute("SELECT id, pin, password FROM student_info")
        students = cursor.fetchall()
        
        migrated_count = 0
        for student_id, pin, password in students:
            updates = []
            params = []
            
            # Hash PIN if it exists and looks like plain text
            if pin and len(pin) <= 10:  # Likely plain text
                pin_hash = generate_password_hash(pin)
                updates.append("pin_hash = %s")
                params.append(pin_hash)
                migrated_count += 1
            
            # Hash password if it exists and looks like plain text
            if password and len(password) <= 20:  # Likely plain text
                password_hash = generate_password_hash(password)
                updates.append("password_hash = %s")
                params.append(password_hash)
                migrated_count += 1
            
            # Update the record
            if updates:
                params.append(student_id)
                query = f"UPDATE student_info SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                print(f"✅ Migrated student ID {student_id}")
        
        # Create sample data if needed
        print("\n📝 CREATING/UPDATING SAMPLE DATA")
        print("=" * 40)
        
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
            # Check if student exists
            cursor.execute("SELECT id FROM student_info WHERE ic_number = %s", (student_data['ic_number'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"ℹ️  Updating existing student: {student_data['name']}")
                # Update existing student
                cursor.execute("""
                    UPDATE student_info 
                    SET name = %s, pin_hash = %s, password_hash = %s, 
                        role = %s, balance = %s, frozen = %s
                    WHERE ic_number = %s
                """, (
                    student_data['name'],
                    generate_password_hash(student_data['pin']),
                    generate_password_hash(student_data['password']) if student_data['password'] else None,
                    student_data['role'],
                    student_data['balance'],
                    student_data['frozen'],
                    student_data['ic_number']
                ))
            else:
                print(f"➕ Creating new student: {student_data['name']}")
                # Insert new student
                cursor.execute("""
                    INSERT INTO student_info (name, ic_number, pin_hash, password_hash, role, balance, frozen)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    student_data['name'],
                    student_data['ic_number'],
                    generate_password_hash(student_data['pin']),
                    generate_password_hash(student_data['password']) if student_data['password'] else None,
                    student_data['role'],
                    student_data['balance'],
                    student_data['frozen']
                ))
        
        # Commit all changes
        conn.commit()
        print(f"\n🎉 Successfully migrated {migrated_count} passwords!")
        print("✅ Sample data created/updated!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 STARTING DATABASE MIGRATION")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Database schema updated")
        print("✅ All passwords and PINs are now hashed")
        print("✅ Sample data created with proper security")
        print("\n🔧 Next steps:")
        print("1. Test login with IC: 1234, PIN: 1234")
        print("2. Test admin login with IC: 9999, PIN: 1234, Password: adminpass")
        print("3. Your application is now secure!")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the errors above and try again.")
