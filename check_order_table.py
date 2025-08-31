#!/usr/bin/env python3
"""
Check Order Table Structure
Check what columns exist in the order table
"""

import psycopg2

def check_order_table():
    """Check the order table structure"""
    
    print("🔍 CHECKING ORDER TABLE STRUCTURE")
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
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'order'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("📋 ORDER TABLE STRUCTURE:")
        print("-" * 40)
        
        if columns:
            for col in columns:
                col_name, data_type, nullable, default_val = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"  {col_name}: {data_type} {nullable_str}{default_str}")
        else:
            print("  No columns found!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_order_table()
