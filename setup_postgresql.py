#!/usr/bin/env python3
"""
PostgreSQL Setup Script for MyMurid Canteen Kiosk
Run this after installing PostgreSQL to set up the database
"""

import psycopg2
from psycopg2 import sql
import os

def setup_postgresql():
    """Set up PostgreSQL database for MyMurid"""
    
    # Database configuration
    DB_NAME = "mymurid_db"
    DB_USER = "mymurid_user"
    DB_PASSWORD = "mymurid_password_2025"  # Change this to a secure password
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    # Admin connection (to postgres database)
    ADMIN_CONNECTION = {
        'host': DB_HOST,
        'port': DB_PORT,
        'database': 'postgres',  # Connect to default postgres database
        'user': 'postgres',      # Default admin user
        'password': input("Enter your PostgreSQL admin password: "),  # The password you set during installation
        'sslmode': 'disable'     # Disable SSL to avoid connection issues
    }
    
    try:
        # Connect as admin to create database and user
        print("🔌 Connecting to PostgreSQL as admin...")
        admin_conn = psycopg2.connect(**ADMIN_CONNECTION)
        admin_conn.autocommit = True
        admin_cursor = admin_conn.cursor()
        
        # Create user
        print("👤 Creating database user...")
        try:
            admin_cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                sql.Identifier(DB_USER)), (DB_PASSWORD,))
            print("✅ User created successfully")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  User already exists")
        
        # Create database
        print("🗄️  Creating database...")
        try:
            admin_cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(DB_NAME), sql.Identifier(DB_USER)))
            print("✅ Database created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️  Database already exists")
        
        # Grant privileges
        print("🔐 Granting privileges...")
        admin_cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(DB_NAME), sql.Identifier(DB_USER)))
        print("✅ Privileges granted")
        
        admin_cursor.close()
        admin_conn.close()
        
        # Test connection with new user
        print("🧪 Testing connection with new user...")
        test_connection = {
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'sslmode': 'disable'  # Disable SSL for testing
        }
        
        test_conn = psycopg2.connect(**test_connection)
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT version();")
        version = test_cursor.fetchone()
        print(f"✅ Connected successfully! PostgreSQL version: {version[0]}")
        
        test_cursor.close()
        test_conn.close()
        
        # Create .env file with database configuration
        print("📝 Creating environment configuration...")
        env_content = f"""# MyMurid Database Configuration
FLASK_ENV=production
DATABASE_URL=postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable
SECRET_KEY=your-super-secret-key-change-this-in-production
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        
        print("\n🎉 PostgreSQL setup completed successfully!")
        print(f"📊 Database: {DB_NAME}")
        print(f"👤 User: {DB_USER}")
        print(f"🔗 Connection: postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        print("\n💡 Next steps:")
        print("1. Run: python setup_db.py")
        print("2. Start your app: python app.py")
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your admin password")
        print("3. Verify PostgreSQL is installed correctly")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🐘 MyMurid PostgreSQL Setup")
    print("=" * 40)
    print("This script will set up PostgreSQL for your MyMurid system.")
    print("Make sure PostgreSQL is installed and running first.")
    print()
    
    setup_postgresql()
