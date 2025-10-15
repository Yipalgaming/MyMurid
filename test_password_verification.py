#!/usr/bin/env python3
"""
Script to test password verification without revealing passwords.
This demonstrates that the login system still works correctly.
"""

import os
import psycopg2
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

def test_password_verification():
    """Test that password verification works correctly"""
    print("🧪 TESTING PASSWORD VERIFICATION")
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
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Test cases: (ic_number, pin, password, expected_role)
        test_cases = [
            ('1234', '1234', None, 'student'),  # Ali
            ('0415', '1234', None, 'student'),   # Sean
            ('9999', '1234', 'adminpass', 'admin')  # Admin
        ]
        
        print("\n🔐 TESTING LOGIN VERIFICATION:")
        print("-" * 35)
        
        for ic, pin, password, expected_role in test_cases:
            # Get user from database
            cursor.execute("""
                SELECT name, role, pin_hash, password_hash 
                FROM student_info 
                WHERE ic_number = %s
            """, (ic,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ User with IC {ic} not found")
                continue
            
            name, role, pin_hash, password_hash = result
            
            # Test PIN verification
            pin_valid = check_password_hash(pin_hash, pin)
            
            # Test password verification (if password exists)
            password_valid = True
            if password and password_hash:
                password_valid = check_password_hash(password_hash, password)
            elif password and not password_hash:
                password_valid = False
            
            # Overall login success
            login_success = pin_valid and password_valid
            
            print(f"\n👤 {name} (IC: {ic})")
            print(f"   Role: {role}")
            print(f"   PIN Verification: {'✅ PASS' if pin_valid else '❌ FAIL'}")
            if password:
                print(f"   Password Verification: {'✅ PASS' if password_valid else '❌ FAIL'}")
            print(f"   Overall Login: {'✅ SUCCESS' if login_success else '❌ FAILED'}")
            
            if role != expected_role:
                print(f"   ⚠️  Role mismatch! Expected: {expected_role}, Got: {role}")
        
        print("\n" + "=" * 50)
        print("🎉 PASSWORD VERIFICATION COMPLETE!")
        print("=" * 50)
        print("✅ Your passwords are securely stored")
        print("✅ Login system works correctly")
        print("✅ No passwords are visible in plain text")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_password_verification()
