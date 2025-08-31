#!/usr/bin/env python3
"""
Setup Render Database
Create all necessary tables in your Render PostgreSQL database
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

def setup_render_database():
    """Create all necessary tables in Render database"""
    
    try:
        print("🔌 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully to Render database!")
        
        # Create tables
        print("\n🏗️ Creating tables...")
        
        # Student Info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_info (
                id SERIAL PRIMARY KEY,
                ic_number VARCHAR(4) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                balance DECIMAL(10,2) DEFAULT 0.00,
                is_frozen BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created student_info table")
        
        # Menu Item table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50),
                image_path VARCHAR(255),
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created menu_item table")
        
        # Order table (quoted because 'order' is reserved)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "order" (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                menu_item_id INTEGER REFERENCES menu_item(id),
                quantity INTEGER NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_status VARCHAR(20) DEFAULT 'unpaid'
            );
        """)
        print("✅ Created order table")
        
        # Transaction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                type VARCHAR(20) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created transaction table")
        
        # Top Up table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_up (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                amount DECIMAL(10,2) NOT NULL,
                method VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                top_up_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created top_up table")
        
        # Vote table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vote (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                menu_item_name VARCHAR(100) NOT NULL,
                vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created vote table")
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                subject VARCHAR(200),
                message TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                admin_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP
            );
        """)
        print("✅ Created feedback table")
        
        # Insert sample data
        print("\n📝 Inserting sample data...")
        
        # Sample students
        cursor.execute("""
            INSERT INTO student_info (ic_number, name, balance) VALUES
            ('1234', 'Ahmad Ali', 50.00),
            ('0415', 'Sean Chuah Shang En', 25.50),
            ('9999', 'Admin Teacher', 0.00)
            ON CONFLICT (ic_number) DO NOTHING;
        """)
        print("✅ Added sample students")
        
        # Sample menu items
        cursor.execute("""
            INSERT INTO menu_item (name, description, price, category) VALUES
            ('Nasi Lemak', 'Traditional coconut rice with sambal', 3.50, 'Main Course'),
            ('Mee Goreng', 'Stir-fried noodles with vegetables', 4.00, 'Main Course'),
            ('Teh Tarik', 'Pulled tea with condensed milk', 1.50, 'Beverage')
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Added sample menu items")
        
        # Commit changes
        conn.commit()
        print("\n✅ All changes committed successfully!")
        
        # Verify tables were created
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database now contains {len(tables)} tables:")
        for table in tables:
            print(f"  • {table[0]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed!")
        print("\n🎉 Your Render database is now ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    setup_render_database()
