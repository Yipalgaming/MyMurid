#!/usr/bin/env python3
import psycopg2

def check_transaction_structure():
    print("🔍 CHECKING RENDER TRANSACTION TABLE STRUCTURE")
    print("=" * 60)
    
    # Render PostgreSQL connection details
    DATABASE_URL = "postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com/mymurid_db"
    
    try:
        # Connect to Render database
        print("🔗 Connecting to Render PostgreSQL database...")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        
        # Check transaction table structure
        print("📋 Transaction table columns:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'transaction' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  📊 {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        # Check if there's any data
        cursor.execute("SELECT COUNT(*) FROM transaction")
        count = cursor.fetchone()[0]
        print(f"\n📊 Current transaction count: {count}")
        
        if count > 0:
            print("\n📋 Sample transaction data:")
            cursor.execute("SELECT * FROM transaction LIMIT 3")
            sample_data = cursor.fetchall()
            for row in sample_data:
                print(f"  📝 {row}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_transaction_structure()
