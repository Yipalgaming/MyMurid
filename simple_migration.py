#!/usr/bin/env python3
"""
Simple migration script to add password hashing columns with proper sizes.
"""

import os
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

def simple_migration():
    """Simple migration to add hash columns"""
    print("🔧 SIMPLE DATABASE MIGRATION")
    print("=" * 40)
    
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
        
        # Drop existing columns if they exist
        print("🗑️  Dropping existing hash columns...")
        try:
            cursor.execute("ALTER TABLE student_info DROP COLUMN IF EXISTS pin_hash")
            cursor.execute("ALTER TABLE student_info DROP COLUMN IF EXISTS password_hash")
            print("✅ Dropped existing columns")
        except Exception as e:
            print(f"ℹ️  No existing columns to drop: {e}")
        
        # Add new columns with proper size
        print("➕ Adding pin_hash column...")
        cursor.execute("ALTER TABLE student_info ADD COLUMN pin_hash VARCHAR(255)")
        print("✅ Added pin_hash column")
        
        print("➕ Adding password_hash column...")
        cursor.execute("ALTER TABLE student_info ADD COLUMN password_hash VARCHAR(255)")
        print("✅ Added password_hash column")
        
        # Migrate existing data
        print("\n🔐 MIGRATING EXISTING DATA")
        print("=" * 30)
        
        # Get all students
        cursor.execute("SELECT id, pin, password FROM student_info")
        students = cursor.fetchall()
        
        for student_id, pin, password in students:
            # Hash PIN
            if pin:
                pin_hash = generate_password_hash(pin)
                cursor.execute("UPDATE student_info SET pin_hash = %s WHERE id = %s", (pin_hash, student_id))
            
            # Hash password
            if password:
                password_hash = generate_password_hash(password)
                cursor.execute("UPDATE student_info SET password_hash = %s WHERE id = %s", (password_hash, student_id))
            
            print(f"✅ Migrated student ID {student_id}")
        
        # Create/update sample data
        print("\n📝 CREATING SAMPLE DATA")
        print("=" * 25)
        
        sample_data = [
            ('Sean Chuah Shang En', '0415', '1234', None, 'student', 20, False),
            ('Ali', '1234', '1234', None, 'student', 20, False),
            ('Teacher / Admin', '9999', '1234', 'adminpass', 'admin', 0, False)
        ]
        
        for name, ic, pin, password, role, balance, frozen in sample_data:
            # Check if exists
            cursor.execute("SELECT id FROM student_info WHERE ic_number = %s", (ic,))
            existing = cursor.fetchone()
            
            pin_hash = generate_password_hash(pin)
            password_hash = generate_password_hash(password) if password else None
            
            if existing:
                print(f"ℹ️  Updating {name}")
                cursor.execute("""
                    UPDATE student_info 
                    SET name = %s, pin_hash = %s, password_hash = %s, 
                        role = %s, balance = %s, frozen = %s
                    WHERE ic_number = %s
                """, (name, pin_hash, password_hash, role, balance, frozen, ic))
            else:
                print(f"➕ Creating {name}")
                cursor.execute("""
                    INSERT INTO student_info (name, ic_number, pin_hash, password_hash, role, balance, frozen)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, ic, pin_hash, password_hash, role, balance, frozen))
        
        # Commit all changes
        conn.commit()
        print("\n🎉 Migration completed successfully!")
        
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
    success = simple_migration()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ Database schema updated")
        print("✅ All passwords and PINs are now hashed")
        print("✅ Sample data created")
        print("\n🔧 Test your application now!")
    else:
        print("\n❌ MIGRATION FAILED!")
