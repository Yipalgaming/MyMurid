#!/usr/bin/env python3
"""
Fix the hash column sizes in the database.
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_hash_columns():
    """Fix hash column sizes"""
    print("🔧 FIXING HASH COLUMN SIZES")
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
        
        # Increase column sizes
        print("➕ Increasing pin_hash column size...")
        cursor.execute("ALTER TABLE student_info ALTER COLUMN pin_hash TYPE VARCHAR(255)")
        print("✅ pin_hash column size increased")
        
        print("➕ Increasing password_hash column size...")
        cursor.execute("ALTER TABLE student_info ALTER COLUMN password_hash TYPE VARCHAR(255)")
        print("✅ password_hash column size increased")
        
        # Commit changes
        conn.commit()
        print("✅ Column sizes fixed!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_hash_columns()
    
    if success:
        print("\n🎉 COLUMN SIZES FIXED!")
        print("Now run: python migrate_database_schema.py")
    else:
        print("\n❌ FIX FAILED!")
