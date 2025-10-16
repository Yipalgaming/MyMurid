#!/usr/bin/env python3
"""
Script to add role column to student_info table in online database
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mymurid_user:mymurid_password_2025@localhost:5432/mymurid_db')

def add_role_column_if_not_exists(engine, table_name, column_name, column_type, default_value=None):
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='{column_name}'"))
            if result.fetchone():
                print(f"Column {column_name} already exists in {table_name} table.")
            else:
                # Add column
                if default_value is not None:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'"))
                else:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                connection.commit()
                print(f"✅ Added {column_name} column to {table_name} table")
        except ProgrammingError as e:
            print(f"Error adding column {column_name} to {table_name}: {e}")
            connection.rollback()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            connection.rollback()

def update_existing_roles(engine):
    """Update existing students with appropriate roles based on their data"""
    with engine.connect() as connection:
        try:
            # Check current data
            result = connection.execute(text("SELECT id, name, ic_number FROM student_info"))
            students = result.fetchall()
            
            print(f"\nFound {len(students)} students in database:")
            for student in students:
                print(f"  - ID: {student[0]}, Name: {student[1]}, IC: {student[2]}")
            
            # Update roles based on IC numbers (you can customize this logic)
            role_updates = [
                ("1234", "staff"),  # Ali - staff
                ("0415", "student"), # Sean Chuah Shang En - student  
                ("9999", "admin")   # Admin/Teacher - admin
            ]
            
            for ic_number, role in role_updates:
                connection.execute(text(f"UPDATE student_info SET role = '{role}' WHERE ic_number = '{ic_number}'"))
                print(f"✅ Updated IC {ic_number} to role '{role}'")
            
            connection.commit()
            print("✅ All role updates committed successfully")
            
        except Exception as e:
            print(f"Error updating roles: {e}")
            connection.rollback()

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    print("Connected to PostgreSQL database")
    print(f"Database URL: {DATABASE_URL}")

    # Add role column to student_info table
    add_role_column_if_not_exists(engine, 'student_info', 'role', 'VARCHAR(50)', 'student')
    
    # Update existing students with appropriate roles
    update_existing_roles(engine)

    print("✅ All database changes completed successfully")
    engine.dispose()
    print("Database connection closed")
