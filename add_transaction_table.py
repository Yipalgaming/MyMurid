#!/usr/bin/env python3
import psycopg2
from dotenv import load_dotenv
import getpass

def add_transaction_table():
    print("🔧 ADDING TRANSACTION TABLE TO POSTGRESQL")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Database connection details
    host = 'localhost'
    port = '5432'
    user = 'postgres'
    database = 'canteen_kiosk'
    
    # Get password from user
    print("🔐 Enter your PostgreSQL password:")
    password = getpass.getpass("Password: ")
    
    try:
        # Connect to database
        print("🔗 Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("📋 Creating transaction table...")
        
        # Create transaction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES student_info(id),
                description VARCHAR(100) NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created transaction table")
        
        print("\n📝 Inserting sample transaction data...")
        
        # Insert sample transactions
        transactions_data = [
            (1, 'Top-up', 50.00),  # Sean Chuah Shang En
            (2, 'Food order - Nasi Lemak', -5.50),  # Ali
            (2, 'Top-up', 20.00),  # Ali
            (1, 'Food order - Chicken Rice', -6.00),  # Sean Chuah Shang En
        ]
        
        for transaction in transactions_data:
            cursor.execute("""
                INSERT INTO transaction (student_id, description, amount)
                VALUES (%s, %s, %s)
            """, transaction)
        print("✅ Inserted sample transactions")
        
        conn.commit()
        
        print("\n📋 Updated database schema:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  📊 {table[0]}")
        
        print("\n📊 Sample transaction data:")
        cursor.execute("""
            SELECT t.id, s.name, t.description, t.amount, t.timestamp 
            FROM transaction t 
            JOIN student_info s ON t.student_id = s.id 
            ORDER BY t.timestamp DESC
        """)
        transactions = cursor.fetchall()
        for tx in transactions:
            print(f"  ID: {tx[0]}, Student: {tx[1]}, Description: {tx[2]}, Amount: RM{tx[3]}, Time: {tx[4]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 TRANSACTION TABLE ADDED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Transaction table created!")
        print("✅ Sample transaction data inserted!")
        print("✅ Your database now has all required tables!")
        print("\n🔧 Next steps:")
        print("1. Restart your Flask app")
        print("2. Check the /transactions page")
        print("3. View the table in pgAdmin 4")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    add_transaction_table()
