#!/usr/bin/env python3
import psycopg2
import os

def fix_render_schema():
    print("🔧 FIXING RENDER DATABASE SCHEMA")
    print("=" * 60)
    
    # Render PostgreSQL connection details
    DATABASE_URL = "postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com/mymurid_db"
    
    try:
        # Connect to Render database
        print("🔗 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        
        print("📋 Checking current schema...")
        
        # Check if transaction table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'transaction'
            );
        """)
        transaction_exists = cursor.fetchone()[0]
        
        if not transaction_exists:
            print("📦 Creating transaction table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    description TEXT,
                    transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created transaction table")
        else:
            print("ℹ️  Transaction table already exists")
        
        # Check and fix order table columns
        print("🔍 Checking order table columns...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'order' 
            AND table_schema = 'public'
        """)
        order_columns = [col[0] for col in cursor.fetchall()]
        
        # Add missing columns to order table
        if 'payment_status' not in order_columns:
            print("➕ Adding payment_status column to order table...")
            cursor.execute("ALTER TABLE \"order\" ADD COLUMN payment_status VARCHAR(20) DEFAULT 'unpaid'")
            print("✅ Added payment_status column")
        
        if 'order_time' not in order_columns:
            print("➕ Adding order_time column to order table...")
            cursor.execute("ALTER TABLE \"order\" ADD COLUMN order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added order_time column")
        
        if 'total_price' not in order_columns:
            print("➕ Adding total_price column to order table...")
            cursor.execute("ALTER TABLE \"order\" ADD COLUMN total_price NUMERIC(10, 2)")
            print("✅ Added total_price column")
        
        if 'status' not in order_columns:
            print("➕ Adding status column to order table...")
            cursor.execute("ALTER TABLE \"order\" ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
            print("✅ Added status column")
        
        # Update existing orders to have proper payment_status
        print("🔄 Updating existing orders...")
        cursor.execute("""
            UPDATE "order" 
            SET payment_status = 'unpaid'
            WHERE payment_status IS NULL
        """)
        print("✅ Updated payment_status for existing orders")
        
        # Update existing orders to have proper order_time
        cursor.execute("""
            UPDATE "order" 
            SET order_time = CURRENT_TIMESTAMP
            WHERE order_time IS NULL
        """)
        print("✅ Updated order_time for existing orders")
        
        # Update existing orders to have proper total_price
        cursor.execute("""
            UPDATE "order" 
            SET total_price = (
                SELECT price * "order".quantity 
                FROM menu_item 
                WHERE menu_item.id = "order".menu_item_id
            )
            WHERE total_price IS NULL
        """)
        print("✅ Updated total_price for existing orders")
        
        # Check and fix menu_item table columns
        print("🔍 Checking menu_item table columns...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'menu_item' 
            AND table_schema = 'public'
        """)
        menu_columns = [col[0] for col in cursor.fetchall()]
        
        if 'image_path' not in menu_columns:
            print("➕ Adding image_path column to menu_item table...")
            cursor.execute("ALTER TABLE menu_item ADD COLUMN image_path VARCHAR(100)")
            print("✅ Added image_path column")
            
            # Copy data from image_filename if it exists
            if 'image_filename' in menu_columns:
                cursor.execute("UPDATE menu_item SET image_path = image_filename WHERE image_path IS NULL")
                print("✅ Copied image_filename to image_path")
        
        if 'description' not in menu_columns:
            print("➕ Adding description column to menu_item table...")
            cursor.execute("ALTER TABLE menu_item ADD COLUMN description TEXT")
            print("✅ Added description column")
        
        if 'is_available' not in menu_columns:
            print("➕ Adding is_available column to menu_item table...")
            cursor.execute("ALTER TABLE menu_item ADD COLUMN is_available BOOLEAN DEFAULT TRUE")
            print("✅ Added is_available column")
        
        if 'created_at' not in menu_columns:
            print("➕ Adding created_at column to menu_item table...")
            cursor.execute("ALTER TABLE menu_item ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added created_at column")
        
        # Check and fix student_info table columns
        print("🔍 Checking student_info table columns...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'student_info' 
            AND table_schema = 'public'
        """)
        student_columns = [col[0] for col in cursor.fetchall()]
        
        if 'ic_number' not in student_columns:
            print("➕ Adding ic_number column to student_info table...")
            cursor.execute("ALTER TABLE student_info ADD COLUMN ic_number VARCHAR(4)")
            print("✅ Added ic_number column")
            
            # Copy data from ic_last4 if it exists
            if 'ic_last4' in student_columns:
                cursor.execute("UPDATE student_info SET ic_number = ic_last4 WHERE ic_number IS NULL")
                print("✅ Copied ic_last4 to ic_number")
        
        if 'frozen' not in student_columns:
            print("➕ Adding frozen column to student_info table...")
            cursor.execute("ALTER TABLE student_info ADD COLUMN frozen BOOLEAN DEFAULT FALSE")
            print("✅ Added frozen column")
            
            # Copy data from is_frozen if it exists
            if 'is_frozen' in student_columns:
                cursor.execute("UPDATE student_info SET frozen = is_frozen WHERE frozen IS NULL")
                print("✅ Copied is_frozen to frozen")
        
        # Add sample transaction data if table is empty
        cursor.execute("SELECT COUNT(*) FROM transaction")
        transaction_count = cursor.fetchone()[0]
        
        if transaction_count == 0:
            print("📝 Adding sample transaction data...")
            sample_transactions = [
                ('Top-up', 50.00, 'Student top-up'),
                ('Payment', -5.50, 'Food order - Nasi Lemak'),
                ('Top-up', 20.00, 'Student top-up'),
                ('Payment', -6.00, 'Food order - Chicken Rice'),
            ]
            
            for transaction in sample_transactions:
                cursor.execute("""
                    INSERT INTO transaction (type, amount, description)
                    VALUES (%s, %s, %s)
                """, transaction)
            print("✅ Added sample transactions")
        
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
            print(f"  📊 {table[0]}")
        
        print("\n📊 Sample data verification:")
        cursor.execute("SELECT COUNT(*) FROM transaction")
        tx_count = cursor.fetchone()[0]
        print(f"  💰 Transactions: {tx_count}")
        
        cursor.execute("SELECT COUNT(*) FROM \"order\"")
        order_count = cursor.fetchone()[0]
        print(f"  📦 Orders: {order_count}")
        
        cursor.execute("SELECT COUNT(*) FROM student_info")
        student_count = cursor.fetchone()[0]
        print(f"  👥 Students: {student_count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 RENDER DATABASE SCHEMA FIXED!")
        print("=" * 60)
        print("✅ All tables updated with correct schema!")
        print("✅ Column names match your updated code!")
        print("✅ Sample data added!")
        print("\n🔧 Next steps:")
        print("1. Redeploy your app on Render")
        print("2. Test the /transactions and /paid-orders pages")
        print("3. Your production environment should now work!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_render_schema()
