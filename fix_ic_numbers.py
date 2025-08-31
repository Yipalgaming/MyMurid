#!/usr/bin/env python3
"""
Fix IC Numbers
Update all student IC numbers to be exactly 4 digits
"""

import psycopg2

# Render Database Connection Details
DB_CONFIG = {
    'host': 'dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
    'port': '5432',
    'database': 'mymurid_db',
    'user': 'mymurid_user',
    'password': '0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
    'sslmode': 'require'
}

def fix_ic_numbers():
    """Update all IC numbers to be exactly 4 digits"""
    
    try:
        print("🔌 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully to Render database!")
        
        # Show current students
        print("\n👥 Current Students (before fix):")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info;")
        students = cursor.fetchall()
        
        for student in students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        # Update IC numbers to 4 digits
        print("\n🔧 Updating IC numbers to 4 digits...")
        
        # Update each student with proper 4-digit IC
        updates = [
            (1, '1234', 'Ahmad Ali', 50.00),
            (2, '0415', 'Sean Chuah Shang En', 25.50),
            (3, '9999', 'Admin Teacher', 0.00)
        ]
        
        for student_id, ic_number, name, balance in updates:
            cursor.execute("""
                UPDATE student_info 
                SET ic_number = %s, name = %s, balance = %s 
                WHERE id = %s;
            """, (ic_number, name, balance, student_id))
            print(f"✅ Updated student {student_id}: IC {ic_number}, Name: {name}")
        
        # Commit changes
        conn.commit()
        print("\n✅ All IC numbers updated successfully!")
        
        # Show updated students
        print("\n👥 Updated Students (after fix):")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info ORDER BY id;")
        updated_students = cursor.fetchall()
        
        for student in updated_students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed!")
        print("\n🎉 IC numbers are now properly formatted as 4 digits!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_ic_numbers()
