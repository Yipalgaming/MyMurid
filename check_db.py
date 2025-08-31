#!/usr/bin/env python3
"""
Check Database Status Script
"""

import psycopg2

def check_database():
    """Check database status"""
    
    try:
        # First, connect to postgres database to see what exists
        print("🔌 Checking PostgreSQL databases...")
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='postgres',
            user='postgres',
            password='postgres',
            sslmode='disable'
        )
        cursor = conn.cursor()
        
        # List all databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        
        print("📊 Available databases:")
        for db in databases:
            print(f"  • {db[0]}")
        
        cursor.close()
        conn.close()
        
        # Now try to connect to mymurid_db specifically
        print("\n🔌 Trying to connect to mymurid_db...")
        try:
            conn2 = psycopg2.connect(
                host='localhost',
                port='5432',
                database='mymurid_db',
                user='mymurid_user',
                password='mymurid_password_2025',
                sslmode='disable'
            )
            cursor2 = conn2.cursor()
            
            # Check if tables exist
            cursor2.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor2.fetchall()
            
            print(f"✅ Connected to mymurid_db!")
            print(f"📋 Tables found: {len(tables)}")
            
            if tables:
                print("Table names:")
                for table in tables:
                    print(f"  • {table[0]}")
            else:
                print("No tables found in public schema")
            
            cursor2.close()
            conn2.close()
            
        except Exception as e:
            print(f"❌ Could not connect to mymurid_db: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database()
