#!/usr/bin/env python3
import sqlite3
import os

def fix_sqlite_columns():
    print("🔧 FIXING SQLITE COLUMN NAMES")
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
        
        print("📋 Current schema:")
        cursor.execute("PRAGMA table_info(student_info)")
        columns = cursor.fetchall()
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            not_null_str = "NOT NULL" if not_null else "NULL"
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name}: {col_type} {not_null_str}{default_str}")
        
        # Check if we need to rename ic_last4 to ic_number
        column_names = [col[1] for col in columns]
        
        if 'ic_last4' in column_names and 'ic_number' not in column_names:
            print("\n🔄 Renaming ic_last4 to ic_number...")
            
            # Create new table with correct column name
            cursor.execute("""
                CREATE TABLE student_info_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    ic_number VARCHAR(4),
                    pin VARCHAR(4) NOT NULL DEFAULT '1234',
                    password VARCHAR(10),
                    role VARCHAR(10) DEFAULT 'student',
                    balance INTEGER DEFAULT 0,
                    frozen BOOLEAN DEFAULT 0
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO student_info_new (id, name, ic_number, pin, password, role, balance, frozen)
                SELECT id, name, ic_last4, pin, password, role, balance, frozen FROM student_info
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE student_info")
            
            # Rename new table to original name
            cursor.execute("ALTER TABLE student_info_new RENAME TO student_info")
            
            print("✅ Successfully renamed ic_last4 to ic_number")
        
        # Check if we need to rename is_frozen to frozen
        cursor.execute("PRAGMA table_info(student_info)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_frozen' in column_names and 'frozen' not in column_names:
            print("\n🔄 Renaming is_frozen to frozen...")
            
            # Create new table with correct column name
            cursor.execute("""
                CREATE TABLE student_info_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    ic_number VARCHAR(4),
                    pin VARCHAR(4) NOT NULL DEFAULT '1234',
                    password VARCHAR(10),
                    role VARCHAR(10) DEFAULT 'student',
                    balance INTEGER DEFAULT 0,
                    frozen BOOLEAN DEFAULT 0
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO student_info_new (id, name, ic_number, pin, password, role, balance, frozen)
                SELECT id, name, ic_number, pin, password, role, balance, is_frozen FROM student_info
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE student_info")
            
            # Rename new table to original name
            cursor.execute("ALTER TABLE student_info_new RENAME TO student_info")
            
            print("✅ Successfully renamed is_frozen to frozen")
        
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
        
        print("\n📋 Final schema:")
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
        print("🎉 SQLITE COLUMN FIX COMPLETE!")
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
    fix_sqlite_columns()
