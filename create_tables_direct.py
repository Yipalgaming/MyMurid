#!/usr/bin/env python3
"""
Direct PostgreSQL Table Creation Script
Creates tables directly in PostgreSQL without Flask
"""

import psycopg2
from psycopg2 import sql

def create_tables():
    """Create tables directly in PostgreSQL"""
    
    # Database connection
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'mymurid_db',
        'user': 'mymurid_user',
        'password': 'mymurid_password_2025',
        'sslmode': 'disable'
    }
    
    try:
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Create tables
        print("\n🏗️ Creating tables...")
        
        # Student Info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_info (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                ic_number VARCHAR(4) NOT NULL UNIQUE,
                pin VARCHAR(10) NOT NULL,
                password VARCHAR(255),
                role VARCHAR(20) DEFAULT 'student',
                balance DECIMAL(10,2) DEFAULT 0.00,
                card_frozen BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ student_info table created")
        
        # Menu Item table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50),
                description TEXT,
                image_filename VARCHAR(255),
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ menu_item table created")
        
        # Order table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "order" (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                menu_item_id INTEGER REFERENCES menu_item(id),
                quantity INTEGER DEFAULT 1,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_status VARCHAR(20) DEFAULT 'unpaid'
            );
        """)
        print("✅ order table created")
        
        # Transaction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                amount DECIMAL(10,2) NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                description TEXT,
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ transaction table created")
        
        # Top Up table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_up (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                amount DECIMAL(10,2) NOT NULL,
                top_up_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'completed'
            );
        """)
        print("✅ top_up table created")
        
        # Vote table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vote (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                food_item VARCHAR(100) NOT NULL,
                vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ vote table created")
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                message TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_response TEXT,
                response_time TIMESTAMP
            );
        """)
        print("✅ feedback table created")
        
        # Insert sample data
        print("\n👥 Inserting sample students...")
        cursor.execute("""
            INSERT INTO student_info (name, ic_number, pin, role, balance) VALUES
            ('Ahmad bin Ali', '1234', '1234', 'student', 50.00),
            ('Sean Chuah Shang En', '0415', '0415', 'student', 25.00),
            ('Admin Teacher', '9999', '9999', 'admin', 0.00)
            ON CONFLICT (ic_number) DO NOTHING;
        """)
        
        print("🍽️ Inserting sample menu items...")
        cursor.execute("""
            INSERT INTO menu_item (name, price, category, image_filename) VALUES
            ('Nasi Lemak', 3.50, 'Main Course', 'nasi_lemak.jpg'),
            ('Chicken Rice', 4.00, 'Main Course', 'chicken_rice.jpg'),
            ('Teh Tarik', 1.50, 'Beverages', 'teh_tarik.jpg'),
            ('Roti Canai', 1.20, 'Snacks', 'roti_canai.jpg'),
            ('Mee Goreng', 3.80, 'Main Course', 'mee_goreng.jpg')
            ON CONFLICT DO NOTHING;
        """)
        
        cursor.close()
        conn.close()
        
        print("\n🎉 All tables created successfully!")
        print("📊 You can now view your database tables!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tables()
