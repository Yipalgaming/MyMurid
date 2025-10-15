#!/usr/bin/env python3
"""
Create sample users in PostgreSQL with proper password hashes
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash

def create_sample_users():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="mymurid_db",
            user="mymurid_user",
            password="mymurid_password_2025"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # Generate password hashes
        pin_hash = generate_password_hash("1234")
        password_hash = generate_password_hash("adminpass")
        
        print(f"Generated PIN hash: {pin_hash}")
        print(f"Generated password hash: {password_hash}")
        
        # Clear existing users
        print("Clearing existing users...")
        cursor.execute("DELETE FROM student_info")
        
        # Create sample users
        users = [
            {
                "name": "Sean Chuah Shang En",
                "ic_number": "0415",
                "pin": "1234",
                "pin_hash": pin_hash,
                "password": "adminpass",
                "password_hash": password_hash,
                "role": "student",
                "balance": 50.0,
                "frozen": False,
                "total_points": 100,
                "available_points": 80
            },
            {
                "name": "Ali",
                "ic_number": "1234",
                "pin": "1234",
                "pin_hash": pin_hash,
                "password": "adminpass",
                "password_hash": password_hash,
                "role": "staff",
                "balance": 0.0,
                "frozen": False,
                "total_points": 0,
                "available_points": 0
            },
            {
                "name": "Admin/Teacher",
                "ic_number": "9999",
                "pin": "1234",
                "pin_hash": pin_hash,
                "password": "adminpass",
                "password_hash": password_hash,
                "role": "admin",
                "balance": 0.0,
                "frozen": False,
                "total_points": 0,
                "available_points": 0
            }
        ]
        
        for user in users:
            print(f"Creating user: {user['name']} (IC: {user['ic_number']}, Role: {user['role']})")
            cursor.execute("""
                INSERT INTO student_info (name, ic_number, pin, password, pin_hash, password_hash, role, balance, frozen, total_points, available_points)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user['name'],
                user['ic_number'],
                user['pin'],
                user['password'],
                user['pin_hash'],
                user['password_hash'],
                user['role'],
                user['balance'],
                user['frozen'],
                user['total_points'],
                user['available_points']
            ))
        
        print("Sample users created successfully!")
        
        # Show current users
        print("\nCurrent users in database:")
        cursor.execute("SELECT name, ic_number, role FROM student_info ORDER BY role, name")
        for row in cursor.fetchall():
            print(f"  {row[0]} (IC: {row[1]}, Role: {row[2]})")
        
        cursor.close()
        conn.close()
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"Error creating sample users: {e}")

if __name__ == "__main__":
    create_sample_users()
