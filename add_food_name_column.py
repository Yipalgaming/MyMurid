#!/usr/bin/env python3
import psycopg2

def add_food_name_column():
    print("🔧 Adding food_name column to vote table...")
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
        try:
            cursor.execute("ALTER TABLE vote ADD COLUMN food_name VARCHAR(100)")
            print("✅ Added food_name column to vote")
        except Exception as e:
            if 'already exists' in str(e):
                print("ℹ️  vote.food_name already exists")
            else:
                print(f"⚠️  Error adding food_name to vote: {e}")
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 Done!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_food_name_column()
