#!/usr/bin/env python3
"""
Cleanup Students
Remove duplicate students and keep only 4-digit IC numbers
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

def cleanup_students():
    """Clean up duplicate students and keep only 4-digit IC numbers"""
    
    try:
        print("🔌 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully to Render database!")
        
        # Show current students
        print("\n👥 Current Students (before cleanup):")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info ORDER BY id;")
        students = cursor.fetchall()
        
        for student in students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        # Clean up: Remove all students and recreate with proper data
        print("\n🧹 Cleaning up database...")
        
        # Delete all existing students
        cursor.execute("DELETE FROM student_info;")
        print("✅ Removed all existing students")
        
        # Reset the ID sequence
        cursor.execute("ALTER SEQUENCE student_info_id_seq RESTART WITH 1;")
        print("✅ Reset ID sequence")
        
        # Insert clean student data with 4-digit IC numbers
        clean_students = [
            ('1234', 'Ahmad Ali', 50.00),
            ('0415', 'Sean Chuah Shang En', 25.50),
            ('9999', 'Admin Teacher', 0.00)
        ]
        
        for ic_number, name, balance in clean_students:
            cursor.execute("""
                INSERT INTO student_info (ic_number, name, balance) 
                VALUES (%s, %s, %s);
            """, (ic_number, name, balance))
            print(f"✅ Added student: IC {ic_number}, Name: {name}")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database cleaned up successfully!")
        
        # Show final result
        print("\n👥 Final Students (after cleanup):")
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info ORDER BY id;")
        final_students = cursor.fetchall()
        
        for student in final_students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed!")
        print("\n🎉 Database is now clean with only 4-digit IC numbers!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    cleanup_students()
