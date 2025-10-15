#!/usr/bin/env python3
"""
Fix missing pin_hash column in student_info table
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_pin_hash_column():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="canteen_db",
            user="postgres",
            password="password"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # Check if pin_hash column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'pin_hash'
        """)
        
        if cursor.fetchone():
            print("pin_hash column already exists")
        else:
            print("Adding pin_hash column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN pin_hash VARCHAR(255)
            """)
            print("pin_hash column added successfully")
        
        # Check if password_hash column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'password_hash'
        """)
        
        if cursor.fetchone():
            print("password_hash column already exists")
        else:
            print("Adding password_hash column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN password_hash VARCHAR(255)
            """)
            print("password_hash column added successfully")
        
        # Check if role column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'role'
        """)
        
        if cursor.fetchone():
            print("role column already exists")
        else:
            print("Adding role column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN role VARCHAR(50) DEFAULT 'student'
            """)
            print("role column added successfully")
        
        # Check if frozen column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'frozen'
        """)
        
        if cursor.fetchone():
            print("frozen column already exists")
        else:
            print("Adding frozen column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN frozen BOOLEAN DEFAULT FALSE
            """)
            print("frozen column added successfully")
        
        # Check if total_points column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'total_points'
        """)
        
        if cursor.fetchone():
            print("total_points column already exists")
        else:
            print("Adding total_points column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN total_points INTEGER DEFAULT 0
            """)
            print("total_points column added successfully")
        
        # Check if available_points column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' AND column_name = 'available_points'
        """)
        
        if cursor.fetchone():
            print("available_points column already exists")
        else:
            print("Adding available_points column to student_info table...")
            cursor.execute("""
                ALTER TABLE student_info 
                ADD COLUMN available_points INTEGER DEFAULT 0
            """)
            print("available_points column added successfully")
        
        # Show current table structure
        print("\nCurrent student_info table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'student_info'
            ORDER BY ordinal_position
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        cursor.close()
        conn.close()
        print("\nDatabase schema fix completed successfully!")
        
    except Exception as e:
        print(f"Error fixing database schema: {e}")

if __name__ == "__main__":
    fix_pin_hash_column()
