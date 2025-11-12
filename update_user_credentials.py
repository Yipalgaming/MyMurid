"""
Script to update student IC/PIN and admin/staff passwords
Supports Unicode characters including Chinese, symbols, and emojis
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import StudentInfo

def validate_ic_format(value):
    """Validate IC format - allows Unicode characters, symbols, etc."""
    if not value:
        return False, "IC cannot be empty"
    if len(value) < 1 or len(value) > 50:
        return False, "IC must be between 1 and 50 characters"
    if not value.strip():
        return False, "IC cannot be only whitespace"
    return True, None

def validate_pin_format(value):
    """Validate PIN format - must be exactly 4 digits"""
    if not value:
        return False, "PIN cannot be empty"
    if not value.isdigit():
        return False, "PIN must contain only digits"
    if len(value) != 4:
        return False, "PIN must be exactly 4 digits"
    return True, None

def update_student_ic_pin():
    """Update IC number and PIN for a student"""
    print("\n" + "="*60)
    print("UPDATE STUDENT IC AND PIN")
    print("="*60)
    print("Note: IC and PIN can now contain symbols, Chinese characters, etc.")
    print("(1-50 characters, cannot be empty or only whitespace)")
    
    # List all students
    students = StudentInfo.query.filter_by(role='student').all()
    if not students:
        print("No students found in the database.")
        return
    
    print("\nCurrent Students:")
    print("-" * 60)
    for i, student in enumerate(students, 1):
        print(f"{i}. ID: {student.id} | Name: {student.name} | IC: {student.ic_number}")
    
    try:
        choice = input("\nEnter student ID to update (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        student_id = int(choice)
        student = StudentInfo.query.get(student_id)
        
        if not student:
            print(f"❌ Student with ID {student_id} not found.")
            return
        
        if student.role != 'student':
            print(f"❌ User {student_id} is not a student (role: {student.role}).")
            return
        
        print(f"\nCurrent details for {student.name}:")
        print(f"  IC Number: {student.ic_number}")
        print(f"  PIN: (hidden)")
        
        # Update IC
        new_ic = input("\nEnter new IC number (1-50 chars, can include symbols/Chinese, or press Enter to skip): ").strip()
        if new_ic:
            is_valid, error_msg = validate_ic_format(new_ic)
            if not is_valid:
                print(f"❌ {error_msg}")
                return
            
            # Check if IC already exists
            existing = StudentInfo.query.filter_by(ic_number=new_ic).first()
            if existing and existing.id != student_id:
                print(f"❌ IC number '{new_ic}' is already taken by {existing.name}.")
                return
            
            student.ic_number = new_ic
            print(f"✅ IC number updated to '{new_ic}'")
        
        # Update PIN
        new_pin = input("Enter new PIN (must be exactly 4 digits, or press Enter to skip): ").strip()
        if new_pin:
            is_valid, error_msg = validate_pin_format(new_pin)
            if not is_valid:
                print(f"❌ {error_msg}")
                return
            
            student.set_pin(new_pin)
            print("✅ PIN updated")
        
        if new_ic or new_pin:
            db.session.commit()
            print(f"\n✅ Successfully updated {student.name}'s credentials!")
        else:
            print("\n⚠️ No changes made.")
            
    except ValueError:
        print("❌ Invalid input. Please enter a valid student ID number.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")

def update_admin_staff_password():
    """Update password for admin or staff"""
    print("\n" + "="*60)
    print("UPDATE ADMIN/STAFF PASSWORD")
    print("="*60)
    
    # List all admin/staff
    admins = StudentInfo.query.filter(StudentInfo.role.in_(['admin', 'staff'])).all()
    if not admins:
        print("No admin or staff users found in the database.")
        return
    
    print("\nCurrent Admin/Staff Users:")
    print("-" * 60)
    for i, admin in enumerate(admins, 1):
        print(f"{i}. ID: {admin.id} | Name: {admin.name} | IC: {admin.ic_number} | Role: {admin.role}")
    
    try:
        choice = input("\nEnter user ID to update password (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        user_id = int(choice)
        user = StudentInfo.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return
        
        if user.role not in ['admin', 'staff']:
            print(f"❌ User {user_id} is not an admin or staff (role: {user.role}).")
            return
        
        print(f"\nUpdating password for {user.name} ({user.role})")
        print(f"Current IC: {user.ic_number}")
        
        # Get new password
        new_password = input("\nEnter new password (or press Enter to skip): ").strip()
        if not new_password:
            print("⚠️ No password entered. Skipping.")
            return
        
        # Confirm password
        confirm_password = input("Confirm new password: ").strip()
        if new_password != confirm_password:
            print("❌ Passwords do not match!")
            return
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        print(f"\n✅ Successfully updated password for {user.name}!")
            
    except ValueError:
        print("❌ Invalid input. Please enter a valid user ID number.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")

def bulk_update_students():
    """Bulk update multiple students"""
    print("\n" + "="*60)
    print("BULK UPDATE STUDENTS")
    print("="*60)
    print("This will allow you to update IC and PIN for multiple students.")
    print("Format: student_id,new_ic,new_pin (one per line, or 'done' to finish)")
    print("Example: 1,你好,世界!")
    print("Note: IC and PIN can contain symbols, Chinese characters, etc.")
    print("-" * 60)
    
    updates = []
    while True:
        line = input("Enter update (student_id,new_ic,new_pin) or 'done': ").strip()
        if line.lower() == 'done':
            break
        
        try:
            # Split by comma, but handle commas in the IC/PIN values
            # Simple approach: split into max 3 parts
            parts = line.split(',', 2)
            if len(parts) != 3:
                print("❌ Invalid format. Use: student_id,new_ic,new_pin")
                continue
            
            student_id, new_ic, new_pin = int(parts[0]), parts[1].strip(), parts[2].strip()
            
            # Validate IC
            is_valid, error_msg = validate_ic_pin_format(new_ic)
            if not is_valid:
                print(f"❌ Invalid IC for student {student_id}: {error_msg}")
                continue
            
            # Validate PIN
            is_valid, error_msg = validate_ic_pin_format(new_pin)
            if not is_valid:
                print(f"❌ Invalid PIN for student {student_id}: {error_msg}")
                continue
            
            updates.append((student_id, new_ic, new_pin))
            print(f"✅ Queued update for student {student_id}")
            
        except ValueError:
            print("❌ Invalid format. Use: student_id,new_ic,new_pin")
    
    if not updates:
        print("No updates to process.")
        return
    
    print(f"\nProcessing {len(updates)} updates...")
    success_count = 0
    
    for student_id, new_ic, new_pin in updates:
        try:
            student = StudentInfo.query.get(student_id)
            if not student:
                print(f"❌ Student {student_id} not found. Skipping.")
                continue
            
            if student.role != 'student':
                print(f"❌ User {student_id} is not a student. Skipping.")
                continue
            
            # Check if IC is already taken
            existing = StudentInfo.query.filter_by(ic_number=new_ic).first()
            if existing and existing.id != student_id:
                print(f"❌ IC '{new_ic}' already taken by {existing.name}. Skipping student {student_id}.")
                continue
            
            student.ic_number = new_ic
            student.set_pin(new_pin)
            success_count += 1
            print(f"✅ Updated student {student_id} ({student.name})")
            
        except Exception as e:
            print(f"❌ Error updating student {student_id}: {str(e)}")
    
    if success_count > 0:
        db.session.commit()
        print(f"\n✅ Successfully updated {success_count} student(s)!")
    else:
        print("\n⚠️ No students were updated.")

def main():
    """Main menu"""
    with app.app_context():
        while True:
            print("\n" + "="*60)
            print("USER CREDENTIALS UPDATE TOOL")
            print("="*60)
            print("1. Update Student IC and PIN")
            print("2. Update Admin/Staff Password")
            print("3. Bulk Update Students (IC and PIN)")
            print("4. Exit")
            print("-" * 60)
            
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                update_student_ic_pin()
            elif choice == '2':
                update_admin_staff_password()
            elif choice == '3':
                bulk_update_students()
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 1-4.")

if __name__ == '__main__':
    main()

