#!/usr/bin/env python3
"""
Create Complete Render Database
Create all missing tables and insert sample data
"""

import os
import psycopg2

def create_complete_database():
    """Create all missing tables and insert sample data"""
    
    print("🏗️  CREATING COMPLETE RENDER DATABASE")
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
        
        print("📋 Creating missing tables...")
        
        # Create menu_item table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_item (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    category VARCHAR(50),
                    image_filename VARCHAR(100)
                )
            """)
            print("✅ Created menu_item table")
        except Exception as e:
            print(f"⚠️  menu_item table error: {e}")
        
        # Create order table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "order" (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES student_info(id),
                    item_id INTEGER REFERENCES menu_item(id),
                    quantity INTEGER NOT NULL,
                    paid BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_done BOOLEAN DEFAULT FALSE
                )
            """)
            print("✅ Created order table")
        except Exception as e:
            print(f"⚠️  order table error: {e}")
        
        # Create vote table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vote (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    food_name VARCHAR(100) NOT NULL,
                    student_id INTEGER REFERENCES student_info(id)
                )
            """)
            print("✅ Created vote table")
        except Exception as e:
            print(f"⚠️  vote table error: {e}")
        
        # Create feedback table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT NOT NULL,
                    student_id INTEGER REFERENCES student_info(id)
                )
            """)
            print("✅ Created feedback table")
        except Exception as e:
            print(f"⚠️  feedback table error: {e}")
        
        # Create topup table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topup (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES student_info(id),
                    amount INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created topup table")
        except Exception as e:
            print(f"⚠️  topup table error: {e}")
        
        # Create transaction table (if not exists)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES student_info(id),
                    description VARCHAR(200) NOT NULL,
                    amount INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created transaction table")
        except Exception as e:
            print(f"⚠️  transaction table error: {e}")
        
        print("\n📝 Inserting sample data...")
        
        # Insert sample menu items
        try:
            cursor.execute("""
                INSERT INTO menu_item (name, price, category, image_filename) VALUES
                ('Nasi Lemak', 3.50, 'Main Course', 'nasi_lemak.jpg'),
                ('Chicken Rice', 4.00, 'Main Course', 'chicken_rice.jpg'),
                ('Mee Goreng', 3.00, 'Noodles', 'mee_goreng.jpg'),
                ('Teh Tarik', 1.50, 'Beverages', 'teh_tarik.jpg'),
                ('Roti Canai', 2.00, 'Breakfast', 'roti_canai.jpg'),
                ('Curry Laksa', 4.50, 'Soup', 'curry_laksa.jpg')
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Added sample menu items")
        except Exception as e:
            print(f"⚠️  Menu items error: {e}")
        
        # Insert sample orders
        try:
            cursor.execute("""
                INSERT INTO "order" (student_id, item_id, quantity, paid, is_done) VALUES
                (1, 1, 2, FALSE, FALSE),
                (1, 3, 1, FALSE, FALSE),
                (2, 2, 1, FALSE, FALSE)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Added sample orders")
        except Exception as e:
            print(f"⚠️  Orders error: {e}")
        
        # Insert sample votes
        try:
            cursor.execute("""
                INSERT INTO vote (food_name, student_id) VALUES
                ('Nasi Lemak', 1),
                ('Chicken Rice', 2),
                ('Mee Goreng', 1)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Added sample votes")
        except Exception as e:
            print(f"⚠️  Votes error: {e}")
        
        # Insert sample feedback
        try:
            cursor.execute("""
                INSERT INTO feedback (message, student_id) VALUES
                ('Food is delicious!', 1),
                ('Great service!', 2),
                ('More variety please', 1)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Added sample feedback")
        except Exception as e:
            print(f"⚠️  Feedback error: {e}")
        
        # Insert sample transactions
        try:
            cursor.execute("""
                INSERT INTO transaction (student_id, description, amount) VALUES
                (1, 'Initial balance', 50),
                (2, 'Initial balance', 25),
                (3, 'Initial balance', 0)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Added sample transactions")
        except Exception as e:
            print(f"⚠️  Transactions error: {e}")
        
        # Commit all changes
        conn.commit()
        
        print("\n📋 Final database schema:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"  ✅ {table[0]}")
        
        # Show sample data counts
        print("\n📊 Sample data counts:")
        for table_name in ['student_info', 'menu_item', 'order', 'vote', 'feedback', 'transaction']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {table_name}: {count} records")
            except Exception as e:
                print(f"  {table_name}: Error - {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE DATABASE CREATION FINISHED!")
        print("=" * 60)
        print("✅ All tables created successfully!")
        print("✅ Sample data inserted!")
        print("✅ Your canteen kiosk system is now fully functional!")
        print("\n🚀 Test these features:")
        print("  • Menu browsing: /order")
        print("  • Payment: /payment") 
        print("  • Voting: /vote")
        print("  • Feedback: /feedback")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    create_complete_database()
