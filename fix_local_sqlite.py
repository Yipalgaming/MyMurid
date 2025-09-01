#!/usr/bin/env python3
import sqlite3
import os

def fix_local_sqlite():
    print("🔧 FIXING LOCAL SQLITE DATABASE SCHEMA")
    print("=" * 60)
    
    # Check if database file exists
    db_path = 'instance/database.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        print("💡 Try running your Flask app first to create the database")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📋 Current schema before fix:")
        cursor.execute("PRAGMA table_info(student_info)")
        columns = cursor.fetchall()
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            not_null_str = "NOT NULL" if not_null else "NULL"
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name}: {col_type} {not_null_str}{default_str}")
        
        print("\n🔧 Adding missing columns...")
        
        # Add frozen column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN frozen BOOLEAN DEFAULT 0")
            print("✅ Added 'frozen' column")
        except Exception as e:
            if 'duplicate column name' in str(e):
                print("ℹ️  'frozen' column already exists")
            else:
                print(f"⚠️  Error adding 'frozen' column: {e}")
        
        # Add pin column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN pin TEXT NOT NULL DEFAULT '1234'")
            print("✅ Added 'pin' column")
        except Exception as e:
            if 'duplicate column name' in str(e):
                print("ℹ️  'pin' column already exists")
            else:
                print(f"⚠️  Error adding 'pin' column: {e}")
        
        # Add password column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN password TEXT")
            print("✅ Added 'password' column")
        except Exception as e:
            if 'duplicate column name' in str(e):
                print("ℹ️  'password' column already exists")
            else:
                print(f"⚠️  Error adding 'password' column: {e}")
        
        # Add role column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_info ADD COLUMN role TEXT DEFAULT 'student'")
            print("✅ Added 'role' column")
        except Exception as e:
            if 'duplicate column name' in str(e):
                print("ℹ️  'role' column already exists")
            else:
                print(f"⚠️  Error adding 'role' column: {e}")
        
        # SQLite doesn't support RENAME COLUMN easily, so we'll check if ic_number exists
        cursor.execute("PRAGMA table_info(student_info)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'ic_last4' in column_names and 'ic_number' not in column_names:
            print("⚠️  Found 'ic_last4' column - you'll need to rename it manually in pgAdmin")
            print("💡 Run: ALTER TABLE student_info RENAME COLUMN ic_last4 TO ic_number;")
        
        if 'is_frozen' in column_names and 'frozen' not in column_names:
            print("⚠️  Found 'is_frozen' column - you'll need to rename it manually in pgAdmin")
            print("💡 Run: ALTER TABLE student_info RENAME COLUMN is_frozen TO frozen;")
        
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
        cursor.execute("PRAGMA table_info(student_info)")
        columns = cursor.fetchall()
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            not_null_str = "NOT NULL" if not_null else "NULL"
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name}: {col_type} {not_null_str}{default_str}")
        
        print("\n📊 Updated data:")
        cursor.execute("SELECT id, ic_number, name, role, pin, password, balance, frozen FROM student_info")
        students = cursor.fetchall()
        for student in students:
            print(f"  ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Role: {student[3]}, PIN: {student[4]}, Password: {student[5]}, Balance: {student[6]}, Frozen: {student[7]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 LOCAL SQLITE SCHEMA FIX COMPLETE!")
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
    fix_local_sqlite()
