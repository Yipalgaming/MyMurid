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
        MenuItem(name="Mee Goreng", price=2.00, image_filename="mee_goreng.png"),
        MenuItem(name="Sandwich", price=2.00, image_filename="sandwich.png"),
        MenuItem(name="Milo", price=1.00, image_filename="milo.png"),
        MenuItem(name="Watermelon Juice", price=1.00, image_filename="watermelon_juice.png"),
    ]

    db.session.add_all(items)
    try:
        db.session.commit()
        print("✅ Menu items updated!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to insert menu items: {e}")
