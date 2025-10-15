#!/usr/bin/env python3
"""
Fix parent-related database and model issues
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_parent_issues():
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
        
        # Check if parent_child table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'parent_child'
        """)
        
        if cursor.fetchone():
            print("parent_child table exists")
            
            # Check if child_id column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'parent_child' AND column_name = 'child_id'
            """)
            
            if cursor.fetchone():
                print("child_id column exists")
            else:
                print("Adding child_id column to parent_child table...")
                cursor.execute("""
                    ALTER TABLE parent_child 
                    ADD COLUMN child_id INTEGER
                """)
                print("child_id column added successfully")
        else:
            print("Creating parent_child table...")
            cursor.execute("""
                CREATE TABLE parent_child (
                    id SERIAL PRIMARY KEY,
                    parent_id INTEGER NOT NULL,
                    child_id INTEGER NOT NULL,
                    relationship VARCHAR(50) DEFAULT 'child',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("parent_child table created successfully")
        
        # Check if parent table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'parent'
        """)
        
        if cursor.fetchone():
            print("parent table exists")
            
            # Check if role column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'parent' AND column_name = 'role'
            """)
            
            if cursor.fetchone():
                print("role column exists in parent table")
            else:
                print("Adding role column to parent table...")
                cursor.execute("""
                    ALTER TABLE parent 
                    ADD COLUMN role VARCHAR(50) DEFAULT 'parent'
                """)
                print("role column added successfully")
        else:
            print("Creating parent table...")
            cursor.execute("""
                CREATE TABLE parent (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'parent',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            print("parent table created successfully")
        
        # Create sample parent if none exists
        cursor.execute("SELECT COUNT(*) FROM parent")
        parent_count = cursor.fetchone()[0]
        
        if parent_count == 0:
            print("Creating sample parent...")
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash("password123")
            
            cursor.execute("""
                INSERT INTO parent (name, email, phone, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            """, ("Parent User", "parent@example.com", "0123456789", password_hash, "parent"))
            print("Sample parent created successfully")
        
        # Show current tables
        print("\nCurrent tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}")
        
        cursor.close()
        conn.close()
        print("\nParent issues fix completed successfully!")
        
    except Exception as e:
        print(f"Error fixing parent issues: {e}")

if __name__ == "__main__":
    fix_parent_issues()
