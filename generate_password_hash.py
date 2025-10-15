#!/usr/bin/env python3
"""
Script to generate password hashes for use in pgAdmin 4.
This helps you create the hashed values needed for direct database operations.
"""

from werkzeug.security import generate_password_hash

def generate_hashes():
    """Generate password hashes for database use"""
    print("🔐 PASSWORD HASH GENERATOR")
    print("=" * 35)
    print("This script generates hashed passwords for use in pgAdmin 4")
    print("Copy the generated hashes and use them in your SQL INSERT statements")
    print()
    
    while True:
        print("\nOptions:")
        print("1. Generate PIN hash")
        print("2. Generate password hash")
        print("3. Generate both for a student")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            pin = input("Enter PIN (4 digits): ").strip()
            if pin.isdigit() and len(pin) == 4:
                pin_hash = generate_password_hash(pin)
                print(f"\n✅ PIN Hash for '{pin}':")
                print(f"'{pin_hash}'")
                print("\n📋 SQL Usage:")
                print(f"INSERT INTO student_info (name, ic_number, role, balance, frozen, pin_hash) VALUES ('Student Name', '1001', 'student', 0, false, '{pin_hash}');")
            else:
                print("❌ PIN must be 4 digits")
        
        elif choice == '2':
            password = input("Enter password: ").strip()
            if password:
                password_hash = generate_password_hash(password)
                print(f"\n✅ Password Hash for '{password}':")
                print(f"'{password_hash}'")
                print("\n📋 SQL Usage:")
                print(f"UPDATE student_info SET password_hash = '{password_hash}' WHERE ic_number = '1001';")
            else:
                print("❌ Password cannot be empty")
        
        elif choice == '3':
            name = input("Enter student name: ").strip()
            ic = input("Enter IC number (4 digits): ").strip()
            pin = input("Enter PIN (4 digits): ").strip()
            role = input("Enter role (student/staff/admin): ").strip().lower()
            balance = input("Enter initial balance (default 0): ").strip()
            balance = int(balance) if balance.isdigit() else 0
            
            if not name or not ic.isdigit() or len(ic) != 4 or not pin.isdigit() or len(pin) != 4:
                print("❌ Invalid input")
                continue
            
            if role not in ['student', 'staff', 'admin']:
                print("❌ Role must be student, staff, or admin")
                continue
            
            pin_hash = generate_password_hash(pin)
            password_hash = None
            
            if role in ['staff', 'admin']:
                password = input(f"Enter password for {role}: ").strip()
                if password:
                    password_hash = generate_password_hash(password)
            
            print(f"\n✅ Complete SQL INSERT statement:")
            print("=" * 50)
            
            if password_hash:
                sql = f"""INSERT INTO student_info (name, ic_number, role, balance, frozen, pin_hash, password_hash)
VALUES ('{name}', '{ic}', '{role}', {balance}, false, '{pin_hash}', '{password_hash}');"""
            else:
                sql = f"""INSERT INTO student_info (name, ic_number, role, balance, frozen, pin_hash, password_hash)
VALUES ('{name}', '{ic}', '{role}', {balance}, false, '{pin_hash}', NULL);"""
            
            print(sql)
            print("=" * 50)
            print("📋 Copy this SQL and run it in pgAdmin 4 Query Tool")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    generate_hashes()
