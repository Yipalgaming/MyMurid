#!/usr/bin/env python3
"""
Simple Database Viewer
"""

import psycopg2

try:
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='mymurid_db',
        user='mymurid_user',
        password='mymurid_password_2025',
        sslmode='disable'
    )
    
    cursor = conn.cursor()
    print("✅ Connected!")
    
    # Get table names
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
    tables = cursor.fetchall()
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"  • {table[0]}")
    
    # Show sample data from key tables
    print("\n" + "="*50)
    
    # Students
    print("\n👥 STUDENTS TABLE:")
    cursor.execute("SELECT * FROM student_info LIMIT 3;")
    students = cursor.fetchall()
    for student in students:
        print(f"  {student}")
    
    # Menu items
    print("\n🍽️ MENU TABLE:")
    cursor.execute("SELECT * FROM menu_item LIMIT 3;")
    menu_items = cursor.fetchall()
    for item in menu_items:
        print(f"  {item}")
    
    cursor.close()
    conn.close()
    print("\n✅ Done!")
    
except Exception as e:
    print(f"❌ Error: {e}")
