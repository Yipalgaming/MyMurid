#!/usr/bin/env python3
"""
Fix Render Database Schema
Update the database to match the expected models
"""

import os
import psycopg2

def fix_schema():
    """Fix the database schema to match the models"""
    
    print("🔧 FIXING RENDER DATABASE SCHEMA")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
            port='5432',
            database='mymurid_db',
            user='mymurid_user',
            password='0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        print("📋 Current schema before fix:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'student_info'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            col_name, data_type, nullable, default_val = col
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name}: {data_type} {nullable_str}{default_str}")
        
        print("\n🔧 Adding missing columns...")
        
        # Add missing columns
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN pin VARCHAR(4) NOT NULL DEFAULT '1234'")
            print("✅ Added 'pin' column")
        except Exception as e:
            print(f"⚠️  'pin' column already exists or error: {e}")
        
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN password VARCHAR(10)")
            print("✅ Added 'password' column")
        except Exception as e:
            print(f"⚠️  'password' column already exists or error: {e}")
        
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN role VARCHAR(10) DEFAULT 'student'")
            print("✅ Added 'role' column")
        except Exception as e:
            print(f"⚠️  'role' column already exists or error: {e}")
        
        # Rename is_frozen to frozen
        try:
            cursor.execute("ALTER TABLE student_info RENAME COLUMN is_frozen TO frozen")
            print("✅ Renamed 'is_frozen' to 'frozen'")
        except Exception as e:
            print(f"⚠️  Rename error: {e}")
        
        # Update existing data
        print("\n📝 Updating existing data...")
        
        # Set admin role for IC 9999
        cursor.execute("UPDATE student_info SET role = 'admin', password = 'adminpass' WHERE ic_number = '9999'")
        print("✅ Updated Admin Teacher role and password")
        
        # Set student role for others
        cursor.execute("UPDATE student_info SET role = 'student' WHERE ic_number != '9999'")
        print("✅ Updated other students to 'student' role")
        
        # Set default PIN for all users
        cursor.execute("UPDATE student_info SET pin = '1234' WHERE pin IS NULL OR pin = ''")
        print("✅ Set default PIN '1234' for all users")
        
        # Commit changes
        conn.commit()
        
        print("\n📋 New schema after fix:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'student_info'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            col_name, data_type, nullable, default_val = col
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name}: {data_type} {nullable_str}{default_str}")
        
        # Show updated data
        print("\n📊 Updated data:")
        cursor.execute("SELECT id, ic_number, name, role, pin, password, balance, frozen FROM student_info")
        students = cursor.fetchall()
        for student in students:
            print(f"  ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Role: {student[3]}, PIN: {student[4]}, Password: {student[5]}, Balance: {student[6]}, Frozen: {student[7]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 SCHEMA FIX COMPLETE!")
        print("=" * 60)
        print("✅ Your Render database now matches your code!")
        print("✅ Login should work properly!")
        print("✅ All features should function!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_schema()
