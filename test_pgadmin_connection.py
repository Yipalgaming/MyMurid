#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection details for pgAdmin4
"""

import os
from sqlalchemy import create_engine, text

def test_connection():
    """Test the database connection and show details"""
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv not installed")
        return
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    print("🔗 Database Connection Test")
    print("=" * 50)
    print(f"Database URL: {database_url}")
    print()
    
    # Parse the URL to show individual components
    if database_url.startswith('postgresql://'):
        # Extract components
        url_parts = database_url.replace('postgresql://', '').split('@')
        if len(url_parts) == 2:
            auth_part = url_parts[0]
            host_part = url_parts[1]
            
            username, password = auth_part.split(':')
            host_port_db = host_part.split('/')
            host_port = host_port_db[0]
            database = host_port_db[1] if len(host_port_db) > 1 else 'mymurid_db'
            
            if ':' in host_port:
                host, port = host_port.split(':')
            else:
                host = host_port
                port = '5432'
            
            print("📋 Connection Details for pgAdmin4:")
            print(f"  Host: {host}")
            print(f"  Port: {port}")
            print(f"  Database: {database}")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
            print()
    
    # Test the connection
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"PostgreSQL Version: {version}")
            
            # Show table count
            result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.fetchone()[0]
            print(f"Tables in database: {table_count}")
            
            # Show some key tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Table names: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
