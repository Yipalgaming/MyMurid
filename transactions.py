from datetime import datetime, timezone, timedelta
from models import db  # Make sure db is initialized in models.py
from sqlalchemy import Numeric

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)  # e.g. "Top-up", "Food order"
    amount = db.Column(Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))

    student = db.relationship('StudentInfo', backref='transactions')  # Optional but useful

    def __repr__(self):
        return f"<Transaction {self.description} | RM{self.amount} | {self.timestamp}>"
