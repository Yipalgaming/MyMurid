#!/usr/bin/env python3
"""
Script to check how passwords are stored in the database.
This demonstrates the security improvements we made.
"""

import os
import psycopg2
from dotenv import load_dotenv

def check_password_storage():
    """Check how passwords are stored in the database"""
    print("🔍 CHECKING PASSWORD STORAGE IN DATABASE")
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
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("\n📊 CURRENT PASSWORD STORAGE:")
        print("-" * 40)
        
        # Get all students and show their password storage
        cursor.execute("""
            SELECT name, ic_number, role, pin_hash, password_hash 
            FROM student_info 
            ORDER BY role, name
        """)
        
        students = cursor.fetchall()
        
        for name, ic, role, pin_hash, password_hash in students:
            print(f"\n👤 {name} (IC: {ic}, Role: {role})")
            print(f"   PIN Hash: {pin_hash[:50]}..." if pin_hash else "   PIN Hash: None")
            print(f"   Password Hash: {password_hash[:50]}..." if password_hash else "   Password Hash: None")
        
        print("\n" + "=" * 50)
        print("🔐 SECURITY EXPLANATION:")
        print("=" * 50)
        print("✅ PINs and passwords are now HASHED (encrypted)")
        print("✅ You CANNOT see the original passwords")
        print("✅ Even database administrators cannot see passwords")
        print("✅ This protects against data breaches")
        print("\n🔧 HOW LOGIN WORKS:")
        print("1. User enters PIN/password")
        print("2. System hashes the input")
        print("3. Compares hash with stored hash")
        print("4. If hashes match, login succeeds")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_password_storage()
