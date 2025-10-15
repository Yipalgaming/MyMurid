#!/usr/bin/env python3
"""
Add missing columns to PostgreSQL student_info table
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def add_missing_columns():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="mymurid_db",
            user="mymurid_user",
            password="mymurid_password_2025"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # Add missing columns one by one
        columns_to_add = [
            ("pin_hash", "VARCHAR(255)"),
            ("password_hash", "VARCHAR(255)"),
            ("role", "VARCHAR(50) DEFAULT 'student'"),
            ("frozen", "BOOLEAN DEFAULT FALSE"),
            ("total_points", "INTEGER DEFAULT 0"),
            ("available_points", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                # Check if column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'student_info' AND column_name = %s
                """, (column_name,))
                
                if cursor.fetchone():
                    print(f"Column {column_name} already exists")
                else:
                    print(f"Adding column {column_name}...")
                    cursor.execute(f"""
                        ALTER TABLE student_info 
                        ADD COLUMN {column_name} {column_type}
                    """)
                    print(f"Column {column_name} added successfully")
                    
            except Exception as e:
                print(f"Error adding column {column_name}: {e}")
        
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
    add_missing_columns()
