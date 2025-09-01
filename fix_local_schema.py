#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

def fix_local_schema():
    print("🔧 FIXING LOCAL DATABASE SCHEMA")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/canteen_kiosk')
    
    try:
        # Parse database URL
        if database_url.startswith('postgresql://'):
            # Extract connection details from URL
            url_parts = database_url.replace('postgresql://', '').split('@')
            auth_part = url_parts[0].split(':')
            host_part = url_parts[1].split('/')
            
            user = auth_part[0]
            password = auth_part[1]
            host = host_part[0].split(':')[0]
            port = host_part[0].split(':')[1] if ':' in host_part[0] else '5432'
            database = host_part[1]
        else:
            # Default values
            user = 'postgres'
            password = 'password'
            host = 'localhost'
            port = '5432'
            database = 'canteen_kiosk'
        
        print(f"🔗 Connecting to: {host}:{port}/{database}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
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
        
        # Add frozen column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN frozen BOOLEAN DEFAULT FALSE")
            print("✅ Added 'frozen' column")
        except Exception as e:
            if 'already exists' in str(e):
                print("ℹ️  'frozen' column already exists")
            else:
                print(f"⚠️  Error adding 'frozen' column: {e}")
        
        # Add pin column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN pin VARCHAR(4) NOT NULL DEFAULT '1234'")
            print("✅ Added 'pin' column")
        except Exception as e:
            if 'already exists' in str(e):
                print("ℹ️  'pin' column already exists")
            else:
                print(f"⚠️  Error adding 'pin' column: {e}")
        
        # Add password column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN password VARCHAR(10)")
            print("✅ Added 'password' column")
        except Exception as e:
            if 'already exists' in str(e):
                print("ℹ️  'password' column already exists")
            else:
                print(f"⚠️  Error adding 'password' column: {e}")
        
        # Add role column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN role VARCHAR(10) DEFAULT 'student'")
            print("✅ Added 'role' column")
        except Exception as e:
            if 'already exists' in str(e):
                print("ℹ️  'role' column already exists")
            else:
                print(f"⚠️  Error adding 'role' column: {e}")
        
        # Rename ic_last4 to ic_number if it exists
        try:
            cursor.execute("ALTER TABLE student_info RENAME COLUMN ic_last4 TO ic_number")
            print("✅ Renamed 'ic_last4' to 'ic_number'")
        except Exception as e:
            if 'does not exist' in str(e):
                print("ℹ️  'ic_last4' column doesn't exist (already renamed or never existed)")
            else:
                print(f"⚠️  Error renaming column: {e}")
        
        # Rename is_frozen to frozen if it exists
        try:
            cursor.execute("ALTER TABLE student_info RENAME COLUMN is_frozen TO frozen")
            print("✅ Renamed 'is_frozen' to 'frozen'")
        except Exception as e:
            if 'does not exist' in str(e):
                print("ℹ️  'is_frozen' column doesn't exist (already renamed or never existed)")
            else:
                print(f"⚠️  Error renaming column: {e}")
        
        print("\n📝 Updating existing data...")
        
        # Update role for admin user
        cursor.execute("UPDATE student_info SET role = 'admin', password = 'adminpass' WHERE ic_number = '9999'")
        print("✅ Updated Admin Teacher role and password")
        
        # Update other students to 'student' role
        cursor.execute("UPDATE student_info SET role = 'student' WHERE ic_number != '9999'")
        print("✅ Updated other students to 'student' role")
        
        # Set default PIN for all users
        cursor.execute("UPDATE student_info SET pin = '1234' WHERE pin IS NULL OR pin = ''")
        print("✅ Set default PIN '1234' for all users")
        
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
        
        print("\n📊 Updated data:")
        cursor.execute("SELECT id, ic_number, name, role, pin, password, balance, frozen FROM student_info")
        students = cursor.fetchall()
        for student in students:
            print(f"  ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Role: {student[3]}, PIN: {student[4]}, Password: {student[5]}, Balance: {student[6]}, Frozen: {student[7]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 LOCAL SCHEMA FIX COMPLETE!")
        print("=" * 60)
        print("✅ Your local database now matches your code!")
        print("✅ Login should work properly!")
        print("✅ All features should function!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_local_schema()
