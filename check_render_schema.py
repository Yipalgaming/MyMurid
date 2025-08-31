#!/usr/bin/env python3
"""
Check Render Database Schema
Check the exact table structure to see what columns exist
"""

import os
import psycopg2

def check_schema():
    """Check the exact table structure"""
    
    print("🔍 CHECKING RENDER DATABASE SCHEMA")
    print("=" * 60)
    
    # Set environment variable for testing
    os.environ['DATABASE_URL'] = 'postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6be5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require'
    
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
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'student_info'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("📋 STUDENT_INFO TABLE STRUCTURE:")
        print("-" * 40)
        
        if columns:
            for col in columns:
                col_name, data_type, nullable, default_val = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"  {col_name}: {data_type} {nullable_str}{default_str}")
        else:
            print("  No columns found!")
        
        # Get sample data
        cursor.execute("SELECT * FROM student_info LIMIT 1")
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n📊 SAMPLE ROW:")
            print("-" * 40)
            print(f"  {sample}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS:")
        print("=" * 60)
        
        if columns:
            col_names = [col[0] for col in columns]
            print(f"Found columns: {', '.join(col_names)}")
            
            # Check what's missing
            expected_cols = ['id', 'name', 'ic_number', 'pin', 'password', 'role', 'balance', 'frozen']
            missing_cols = [col for col in expected_cols if col not in col_names]
            
            if missing_cols:
                print(f"\n❌ MISSING COLUMNS: {', '.join(missing_cols)}")
                print("🔧 Your database schema doesn't match your models!")
            else:
                print("\n✅ All expected columns found!")
                
        else:
            print("❌ No columns found - table might be empty or wrong name")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()
