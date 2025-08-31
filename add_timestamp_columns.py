#!/usr/bin/env python3
"""
Add timestamp column to feedback and vote tables if not exists
"""
import psycopg2

def add_timestamp_columns():
    print("🔧 Adding timestamp columns to feedback and vote tables...")
    try:
        conn = psycopg2.connect(
            host='dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
            port='5432',
            database='mymurid_db',
            user='mymurid_user',
            password='0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
            sslmode='require'
        )
        cursor = conn.cursor()
        for table in ['feedback', 'vote']:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print(f"✅ Added timestamp column to {table}")
            except Exception as e:
                if 'already exists' in str(e):
                    print(f"ℹ️  {table}.timestamp already exists")
                else:
                    print(f"⚠️  Error adding timestamp to {table}: {e}")
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 Done!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_timestamp_columns()
