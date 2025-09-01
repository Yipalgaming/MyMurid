#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv
import getpass

def setup_local_postgres():
    print("🔧 SETTING UP LOCAL POSTGRESQL DATABASE")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Database connection details
    host = 'localhost'
    port = '5432'
    user = 'postgres'  # Default PostgreSQL user
    
    # Get password from user
    print("🔐 Enter your PostgreSQL password:")
    password = getpass.getpass("Password: ")
    
    database = 'canteen_kiosk'
    
    try:
        # First, connect to default 'postgres' database to create our database
        print("🔗 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Connect to default database first
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print(f"📦 Creating database '{database}'...")
        try:
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"✅ Created database '{database}'")
        except Exception as e:
            if 'already exists' in str(e):
                print(f"ℹ️  Database '{database}' already exists")
            else:
                print(f"⚠️  Error creating database: {e}")
        
        cursor.close()
        conn.close()
        
        # Now connect to our specific database
        print(f"🔗 Connecting to database '{database}'...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("📋 Creating tables...")
        
        # Create student_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_info (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                ic_number VARCHAR(4) UNIQUE,
                pin VARCHAR(4) NOT NULL DEFAULT '1234',
                password VARCHAR(10),
                role VARCHAR(10) DEFAULT 'student',
                balance INTEGER DEFAULT 0,
                frozen BOOLEAN DEFAULT FALSE
            )
        """)
        print("✅ Created student_info table")
        
        # Create menu_item table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                description TEXT,
                price NUMERIC(10, 2),
                category VARCHAR(50),
                image_path VARCHAR(100),
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created menu_item table")
        
        # Create order table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "order" (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                menu_item_id INTEGER REFERENCES menu_item(id),
                quantity INTEGER,
                total_price NUMERIC(10, 2),
                status VARCHAR(20) DEFAULT 'pending',
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_status VARCHAR(20) DEFAULT 'unpaid'
            )
        """)
        print("✅ Created order table")
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                student_id INTEGER REFERENCES student_info(id)
            )
        """)
        print("✅ Created feedback table")
        
        # Create vote table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vote (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                food_name VARCHAR(100),
                student_id INTEGER REFERENCES student_info(id)
            )
        """)
        print("✅ Created vote table")
        
        # Create topup table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topup (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES student_info(id),
                amount INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created topup table")
        
        print("\n📝 Inserting sample data...")
        
        # Insert sample students
        students_data = [
            ('Sean Chuah Shang En', '0415', '1234', None, 'student', 20, False),
            ('Ali', '1234', '1234', None, 'student', 20, False),
            ('Teacher / Admin', '9999', '1234', 'adminpass', 'admin', 0, False)
        ]
        
        for student in students_data:
            cursor.execute("""
                INSERT INTO student_info (name, ic_number, pin, password, role, balance, frozen)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ic_number) DO UPDATE SET
                    name = EXCLUDED.name,
                    pin = EXCLUDED.pin,
                    password = EXCLUDED.password,
                    role = EXCLUDED.role,
                    balance = EXCLUDED.balance,
                    frozen = EXCLUDED.frozen
            """, student)
        print("✅ Inserted sample students")
        
        # Insert sample menu items
        menu_items_data = [
            ('Nasi Lemak', 'Traditional Malaysian coconut rice with sambal', 5.50, 'Main Course', 'nasi_lemak.jpg', True),
            ('Chicken Rice', 'Hainanese chicken rice with soup', 6.00, 'Main Course', 'chicken_rice.jpg', True),
            ('Laksa', 'Spicy noodle soup with coconut milk', 7.50, 'Main Course', 'laksa.jpg', True),
            ('Teh Tarik', 'Malaysian pulled tea', 2.50, 'Beverages', 'teh_tarik.jpg', True),
            ('Cendol', 'Sweet dessert with coconut milk', 3.00, 'Desserts', 'cendol.jpg', True)
        ]
        
        for item in menu_items_data:
            cursor.execute("""
                INSERT INTO menu_item (name, description, price, category, image_path, is_available)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, item)
        print("✅ Inserted sample menu items")
        
        conn.commit()
        
        print("\n📋 Database schema:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  📊 {table[0]}")
        
        print("\n📊 Sample data:")
        cursor.execute("SELECT id, ic_number, name, role, pin, password, balance, frozen FROM student_info")
        students = cursor.fetchall()
        for student in students:
            print(f"  ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Role: {student[3]}, PIN: {student[4]}, Password: {student[5]}, Balance: {student[6]}, Frozen: {student[7]}")
        
        cursor.close()
        conn.close()
        
        # Create .env file with the correct password
        env_content = f"""# Local PostgreSQL Database Configuration
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}

# Flask Configuration
SECRET_KEY=canteen-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

# Barcode Configuration
BARCODE_FOLDER=static/barcodes
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n" + "=" * 60)
        print("🎉 LOCAL POSTGRESQL SETUP COMPLETE!")
        print("=" * 60)
        print("✅ Database created successfully!")
        print("✅ Tables created with correct schema!")
        print("✅ Sample data inserted!")
        print("✅ .env file created with correct DATABASE_URL!")
        print("\n🔧 Next steps:")
        print("1. Restart your Flask app")
        print("2. Test login with IC: 1234, PIN: 1234")
        print("3. Your local environment now matches production!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    setup_local_postgres()
