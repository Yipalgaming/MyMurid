#!/usr/bin/env python3
"""
Script to remove pin_hash and password_hash columns from online database
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def remove_pin_password_columns():
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
            # Check current columns
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='student_info' ORDER BY column_name"))
            columns = [row[0] for row in result.fetchall()]
            print(f"\nCurrent columns in student_info table:")
            for col in columns:
                print(f"  - {col}")
            
            # Remove pin_hash column if it exists
            if 'pin_hash' in columns:
                print(f"\n🗑️  Removing pin_hash column...")
                connection.execute(text("ALTER TABLE student_info DROP COLUMN pin_hash"))
                print(f"✅ pin_hash column removed successfully")
            else:
                print(f"\n⚠️  pin_hash column not found")
            
            # Remove password_hash column if it exists
            if 'password_hash' in columns:
                print(f"\n🗑️  Removing password_hash column...")
                connection.execute(text("ALTER TABLE student_info DROP COLUMN password_hash"))
                print(f"✅ password_hash column removed successfully")
            else:
                print(f"\n⚠️  password_hash column not found")
            
            connection.commit()
            print(f"\n✅ All changes committed successfully")
            
            # Show updated columns
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='student_info' ORDER BY column_name"))
            columns = [row[0] for row in result.fetchall()]
            print(f"\nUpdated columns in student_info table:")
            for col in columns:
                print(f"  - {col}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    remove_pin_password_columns()
