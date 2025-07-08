from models import db, MenuItem
from app import app

with app.app_context():
    # Ensure tables are created
    db.create_all()

    # Clear existing menu items
    MenuItem.query.delete()
    db.session.commit()

    # Add new sample items
    items = [
        MenuItem(name="Nasi Lemak", price=2.00, image_filename="nasi_lemak.png"),
        MenuItem(name="Mee Goreng", price=2.50),
        MenuItem(name="Sandwich", price=1.50),
        MenuItem(name="Milo", price=1.00),
        MenuItem(name="Apple Juice", price=1.20),
    ]

    db.session.add_all(items)
    try:
        db.session.commit()
        print("✅ Menu items updated!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to insert menu items: {e}")
