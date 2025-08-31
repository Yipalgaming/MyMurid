#!/usr/bin/env python3
"""
View Database Tables Script for MyMurid
Shows all tables and their contents
"""

import psycopg2

def view_database():
    """View all tables and their contents"""
    
    # Database connection details
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'mymurid_db',
        'user': 'mymurid_user',
        'password': 'mymurid_password_2025',
        'sslmode': 'disable'
    }
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        print("\n🐘 MyMurid Database Viewer")
        print("=" * 50)
        
        # Get all table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Table: {table_name}")
            print("-" * 30)
            
            # Get table structure
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  • {col[0]} ({col[1]}) - {nullable}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Rows: {count}")
            
            # Show first 3 rows as sample
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
                if count > 3:
                    print(f"  ... and {count - 3} more rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the database 'mymurid_db' exists")
        print("3. Verify user 'mymurid_user' has access")

if __name__ == "__main__":
    view_database()
