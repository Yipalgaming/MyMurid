from models import db, StudentInfo
from werkzeug.security import generate_password_hash
from app import app

with app.app_context():
    # Ensure tables are created before inserting data
    db.create_all()

    # Optional: Clear existing data for fresh start (caution in production!)
    StudentInfo.query.delete()
    db.session.commit()

    # Sample student
    users = [
        StudentInfo(ic_last4='0415', name='Sean Chuah Shang En', pin='1234', role='student', balance=20, frozen=False),
        StudentInfo(ic_last4='1234', name='Ali', pin='1234', role='student', balance=20, frozen=False),
        StudentInfo(ic_last4='9999', name='Teacher/Admin', pin='1234', role='admin', password='adminpass', balance=0, frozen=False)
    ]

    db.session.add_all(users)
    try:
        db.session.commit()
        print("✅ Student/Admin Info updated!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to update Student/Admin Info: {e}")
