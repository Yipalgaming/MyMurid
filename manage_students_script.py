#!/usr/bin/env python3
"""
Script to manage students in the database.
This allows you to add, update, or delete students programmatically.
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import StudentInfo

def add_student_interactive():
    """Add a new student interactively"""
    print("➕ ADDING NEW STUDENT")
    print("=" * 30)
    
    try:
        name = input("Enter student name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            return False
        
        ic_number = input("Enter IC number (4 digits): ").strip()
        if not ic_number.isdigit() or len(ic_number) != 4:
            print("❌ IC number must be 4 digits")
            return False
        
        pin = input("Enter PIN (4 digits): ").strip()
        if not pin.isdigit() or len(pin) != 4:
            print("❌ PIN must be 4 digits")
            return False
        
        print("\nSelect role:")
        print("1. Student")
        print("2. Staff")
        print("3. Admin")
        role_choice = input("Enter choice (1-3): ").strip()
        
        role_map = {'1': 'student', '2': 'staff', '3': 'admin'}
        role = role_map.get(role_choice, 'student')
        
        balance = input("Enter initial balance (default 0): ").strip()
        try:
            balance = int(balance) if balance else 0
        except ValueError:
            balance = 0
        
        password = None
        if role in ['staff', 'admin']:
            password = input(f"Enter password for {role}: ").strip()
            if not password:
                print("❌ Password required for staff/admin")
                return False
        
        # Check if IC already exists
        existing = StudentInfo.query.filter_by(ic_number=ic_number).first()
        if existing:
            print(f"❌ Student with IC {ic_number} already exists")
            return False
        
        # Create student
        new_student = StudentInfo(
            name=name,
            ic_number=ic_number,
            role=role,
            balance=balance,
            frozen=False
        )
        
        # Set PIN and password
        new_student.set_pin(pin)
        if password:
            new_student.set_password(password)
        
        db.session.add(new_student)
        db.session.commit()
        
        print(f"✅ Successfully added student: {name} (IC: {ic_number})")
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()
        return False

def update_student_interactive():
    """Update an existing student"""
    print("✏️ UPDATING STUDENT")
    print("=" * 25)
    
    try:
        ic_number = input("Enter IC number of student to update: ").strip()
        student = StudentInfo.query.filter_by(ic_number=ic_number).first()
        
        if not student:
            print(f"❌ Student with IC {ic_number} not found")
            return False
        
        print(f"\nCurrent student: {student.name}")
        print(f"Role: {student.role}")
        print(f"Balance: RM {student.balance}")
        print(f"Frozen: {student.frozen}")
        
        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. PIN")
        print("3. Password")
        print("4. Balance")
        print("5. Role")
        print("6. Freeze/Unfreeze status")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            new_name = input("Enter new name: ").strip()
            if new_name:
                student.name = new_name
        
        elif choice == '2':
            new_pin = input("Enter new PIN (4 digits): ").strip()
            if new_pin.isdigit() and len(new_pin) == 4:
                student.set_pin(new_pin)
            else:
                print("❌ Invalid PIN format")
                return False
        
        elif choice == '3':
            if student.role in ['staff', 'admin']:
                new_password = input("Enter new password: ").strip()
                if new_password:
                    student.set_password(new_password)
            else:
                print("❌ Only staff and admin have passwords")
                return False
        
        elif choice == '4':
            new_balance = input("Enter new balance: ").strip()
            try:
                student.balance = int(new_balance)
            except ValueError:
                print("❌ Invalid balance")
                return False
        
        elif choice == '5':
            print("1. Student")
            print("2. Staff")
            print("3. Admin")
            role_choice = input("Enter new role (1-3): ").strip()
            role_map = {'1': 'student', '2': 'staff', '3': 'admin'}
            new_role = role_map.get(role_choice, student.role)
            student.role = new_role
        
        elif choice == '6':
            student.frozen = not student.frozen
            status = "frozen" if student.frozen else "unfrozen"
            print(f"Student is now {status}")
        
        else:
            print("❌ Invalid choice")
            return False
        
        db.session.commit()
        print("✅ Student updated successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()
        return False

def list_students():
    """List all students"""
    print("📋 ALL STUDENTS")
    print("=" * 20)
    
    students = StudentInfo.query.order_by(StudentInfo.name).all()
    
    if not students:
        print("No students found.")
        return
    
    print(f"{'Name':<20} {'IC':<6} {'Role':<8} {'Balance':<8} {'Status':<8}")
    print("-" * 60)
    
    for student in students:
        status = "Frozen" if student.frozen else "Active"
        print(f"{student.name:<20} {student.ic_number:<6} {student.role:<8} RM{student.balance:<7} {status:<8}")

def delete_student_interactive():
    """Delete a student"""
    print("🗑️ DELETE STUDENT")
    print("=" * 20)
    
    try:
        ic_number = input("Enter IC number of student to delete: ").strip()
        student = StudentInfo.query.filter_by(ic_number=ic_number).first()
        
        if not student:
            print(f"❌ Student with IC {ic_number} not found")
            return False
        
        print(f"\nStudent to delete: {student.name} (IC: {ic_number})")
        confirm = input("Are you sure? Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            db.session.delete(student)
            db.session.commit()
            print("✅ Student deleted successfully!")
            return True
        else:
            print("❌ Deletion cancelled")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()
        return False

def bulk_add_students():
    """Add multiple students from a predefined list"""
    print("📦 BULK ADD STUDENTS")
    print("=" * 25)
    
    # Predefined students to add
    students_to_add = [
        {
            'name': 'John Doe',
            'ic_number': '1001',
            'pin': '1234',
            'role': 'student',
            'balance': 10,
            'password': None
        },
        {
            'name': 'Jane Smith',
            'ic_number': '1002',
            'pin': '5678',
            'role': 'student',
            'balance': 15,
            'password': None
        },
        {
            'name': 'Staff Member',
            'ic_number': '2001',
            'pin': '1111',
            'role': 'staff',
            'balance': 0,
            'password': 'staffpass'
        }
    ]
    
    try:
        added_count = 0
        for student_data in students_to_add:
            # Check if already exists
            existing = StudentInfo.query.filter_by(ic_number=student_data['ic_number']).first()
            if existing:
                print(f"ℹ️  Student {student_data['name']} already exists, skipping...")
                continue
            
            # Create student
            new_student = StudentInfo(
                name=student_data['name'],
                ic_number=student_data['ic_number'],
                role=student_data['role'],
                balance=student_data['balance'],
                frozen=False
            )
            
            new_student.set_pin(student_data['pin'])
            if student_data['password']:
                new_student.set_password(student_data['password'])
            
            db.session.add(new_student)
            added_count += 1
            print(f"✅ Added: {student_data['name']} (IC: {student_data['ic_number']})")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {added_count} students!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Main menu"""
    with app.app_context():
        while True:
            print("\n" + "=" * 50)
            print("👥 STUDENT MANAGEMENT SYSTEM")
            print("=" * 50)
            print("1. List all students")
            print("2. Add new student")
            print("3. Update student")
            print("4. Delete student")
            print("5. Bulk add students")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                list_students()
            elif choice == '2':
                add_student_interactive()
            elif choice == '3':
                update_student_interactive()
            elif choice == '4':
                delete_student_interactive()
            elif choice == '5':
                bulk_add_students()
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    load_dotenv()
    main()
