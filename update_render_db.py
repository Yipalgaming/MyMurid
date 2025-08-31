#!/usr/bin/env python3
"""
Update Render Database
Easy script to update values in your Render PostgreSQL database
"""

import psycopg2

# Render Database Connection Details
DB_CONFIG = {
    'host': 'dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
    'port': '5432',
    'database': 'mymurid_db',
    'user': 'mymurid_user',
    'password': '0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
    'sslmode': 'require'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def show_menu():
    """Show update options"""
    print("\n🔄 UPDATE RENDER DATABASE")
    print("=" * 40)
    print("1. Update student balance")
    print("2. Update menu item price")
    print("3. Update menu item availability")
    print("4. Add new student")
    print("5. Add new menu item")
    print("6. View all data")
    print("7. Exit")
    print("=" * 40)

def update_student_balance():
    """Update student balance"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Show current students
        cursor.execute("SELECT id, ic_number, name, balance FROM student_info;")
        students = cursor.fetchall()
        
        print("\n👥 Current Students:")
        for student in students:
            print(f"ID: {student[0]}, IC: {student[1]}, Name: {student[2]}, Balance: RM{student[3]}")
        
        # Get update details
        student_id = input("\nEnter student ID to update: ")
        new_balance = input("Enter new balance (RM): ")
        
        # Update balance
        cursor.execute("UPDATE student_info SET balance = %s WHERE id = %s;", (new_balance, student_id))
        conn.commit()
        
        print(f"✅ Updated student {student_id} balance to RM{new_balance}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def update_menu_price():
    """Update menu item price"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Show current menu items
        cursor.execute("SELECT id, name, price, category FROM menu_item;")
        items = cursor.fetchall()
        
        print("\n🍽️ Current Menu Items:")
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}, Price: RM{item[2]}, Category: {item[3]}")
        
        # Get update details
        item_id = input("\nEnter menu item ID to update: ")
        new_price = input("Enter new price (RM): ")
        
        # Update price
        cursor.execute("UPDATE menu_item SET price = %s WHERE id = %s;", (new_price, item_id))
        conn.commit()
        
        print(f"✅ Updated menu item {item_id} price to RM{new_price}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def update_menu_availability():
    """Update menu item availability"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Show current menu items
        cursor.execute("SELECT id, name, is_available FROM menu_item;")
        items = cursor.fetchall()
        
        print("\n🍽️ Current Menu Items:")
        for item in items:
            status = "Available" if item[2] else "Not Available"
            print(f"ID: {item[0]}, Name: {item[1]}, Status: {status}")
        
        # Get update details
        item_id = input("\nEnter menu item ID to update: ")
        available = input("Available? (y/n): ").lower() == 'y'
        
        # Update availability
        cursor.execute("UPDATE menu_item SET is_available = %s WHERE id = %s;", (available, item_id))
        conn.commit()
        
        status = "Available" if available else "Not Available"
        print(f"✅ Updated menu item {item_id} to {status}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def add_new_student():
    """Add new student"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get student details
        ic_number = input("\nEnter IC number (4 digits): ")
        name = input("Enter student name: ")
        balance = input("Enter initial balance (RM): ")
        
        # Insert new student
        cursor.execute("""
            INSERT INTO student_info (ic_number, name, balance) 
            VALUES (%s, %s, %s);
        """, (ic_number, name, balance))
        
        conn.commit()
        print(f"✅ Added new student: {name} (IC: {ic_number})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def add_new_menu_item():
    """Add new menu item"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get menu item details
        name = input("\nEnter menu item name: ")
        description = input("Enter description: ")
        price = input("Enter price (RM): ")
        category = input("Enter category: ")
        
        # Insert new menu item
        cursor.execute("""
            INSERT INTO menu_item (name, description, price, category) 
            VALUES (%s, %s, %s, %s);
        """, (name, description, price, category))
        
        conn.commit()
        print(f"✅ Added new menu item: {name} (RM{price})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def view_all_data():
    """View all data in tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n📊 DATABASE OVERVIEW")
        print("=" * 50)
        
        # Students
        cursor.execute("SELECT COUNT(*) FROM student_info;")
        student_count = cursor.fetchone()[0]
        print(f"👥 Students: {student_count}")
        
        # Menu items
        cursor.execute("SELECT COUNT(*) FROM menu_item;")
        menu_count = cursor.fetchone()[0]
        print(f"🍽️ Menu Items: {menu_count}")
        
        # Orders
        cursor.execute("SELECT COUNT(*) FROM \"order\";")
        order_count = cursor.fetchone()[0]
        print(f"📋 Orders: {order_count}")
        
        # Recent students
        print("\n👥 Recent Students:")
        cursor.execute("SELECT ic_number, name, balance FROM student_info ORDER BY id DESC LIMIT 5;")
        students = cursor.fetchall()
        for student in students:
            print(f"  IC: {student[0]}, Name: {student[1]}, Balance: RM{student[2]}")
        
        # Recent menu items
        print("\n🍽️ Menu Items:")
        cursor.execute("SELECT name, price, category, is_available FROM menu_item ORDER BY id DESC LIMIT 5;")
        items = cursor.fetchall()
        for item in items:
            status = "✅" if item[3] else "❌"
            print(f"  {status} {item[0]} - RM{item[1]} ({item[2]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu loop"""
    while True:
        show_menu()
        choice = input("\nSelect option (1-7): ")
        
        if choice == '1':
            update_student_balance()
        elif choice == '2':
            update_menu_price()
        elif choice == '3':
            update_menu_availability()
        elif choice == '4':
            add_new_student()
        elif choice == '5':
            add_new_menu_item()
        elif choice == '6':
            view_all_data()
        elif choice == '7':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("🌐 Render Database Update Tool")
    print("🔗 Connected to: dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com")
    main()
