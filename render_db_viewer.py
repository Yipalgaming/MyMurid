#!/usr/bin/env python3
"""
Render Database Viewer
Connect to your Render PostgreSQL database and view tables
"""

import psycopg2

# Render Database Connection Details
DB_CONFIG = {
    'host': 'dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
    'port': '5432',
    'database': 'mymurid_db',
    'user': 'mymurid_user',
    'password': '0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
    'sslmode': 'require'  # Render requires SSL
}

def view_render_database():
    """View tables and data from Render database"""
    
    try:
        print("🔌 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully to Render database!")
        
        # Get table names
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  • {table[0]}")
        
        if not tables:
            print("\n❌ No tables found! The database is empty.")
            print("💡 You need to create the tables first.")
            return
        
        # Show table structure for each table
        print("\n" + "="*60)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 TABLE: {table_name}")
            
            # Get column information
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                col_name, data_type, nullable, default_val = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"    • {col_name}: {data_type} {nullable_str}{default_str}")
            
            # Try to get sample data
            try:
                cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 2;')
                rows = cursor.fetchall()
                if rows:
                    print(f"  Sample data ({len(rows)} rows):")
                    for row in rows:
                        print(f"    {row}")
                else:
                    print("  No data in table")
            except Exception as e:
                print(f"  Error reading data: {e}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_render_database()
