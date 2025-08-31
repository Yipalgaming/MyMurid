#!/usr/bin/env python3
"""
Database setup script for MyMurid Canteen System
This script helps set up PostgreSQL database and migrate existing data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config import config

def create_postgres_database():
    """Create PostgreSQL database if it doesn't exist"""
    try:
        # Get database URL from environment or config
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("Please set DATABASE_URL with your PostgreSQL connection string")
            print("Example: postgresql://username:password@localhost:5432/mymurid")
            return False
        
        # Test connection
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
        return True
        
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL format")
        print("3. Verify username, password, and database name")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_database():
    """Main setup function"""
    print("🚀 MyMurid Database Setup")
    print("=" * 40)
    
    # Check if we're using PostgreSQL
    if os.environ.get('DATABASE_URL'):
        print("📊 Using PostgreSQL database")
        if create_postgres_database():
            print("\n✅ PostgreSQL setup successful!")
            print("\nNext steps:")
            print("1. Run: flask db upgrade")
            print("2. Run: flask db migrate -m 'Initial migration'")
            print("3. Start your application: python app.py")
        else:
            print("\n❌ PostgreSQL setup failed")
            sys.exit(1)
    else:
        print("📁 Using SQLite database (development mode)")
        print("\nTo use PostgreSQL:")
        print("1. Set DATABASE_URL environment variable")
        print("2. Run this script again")
        print("3. Or run: python setup_database.py")

if __name__ == "__main__":
    setup_database()
