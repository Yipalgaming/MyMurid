#!/usr/bin/env python3
"""
Add Missing Student
Add the missing Admin Teacher student to the Render database
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

def add_missing_student():
    """Add the missing Admin Teacher student"""
    
    try:
        print("🔌 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully to Render database!")
        
        # Show current students
        print("\n👥 Current Students:")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info ORDER BY id;")
        students = cursor.fetchall()
        
        for student in students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        # Add missing Admin Teacher
        print("\n➕ Adding missing Admin Teacher...")
        cursor.execute("""
            INSERT INTO student_info (ic_number, name, balance) 
            VALUES (%s, %s, %s);
        """, ('9999', 'Admin Teacher', 0.00))
        
        conn.commit()
        print("✅ Added Admin Teacher: IC 9999")
        
        # Show updated students
        print("\n👥 Updated Students:")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info ORDER BY id;")
        updated_students = cursor.fetchall()
        
        for student in updated_students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed!")
        print("\n🎉 All students are now in the database!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    add_missing_student()
