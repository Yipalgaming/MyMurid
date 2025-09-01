from datetime import datetime, timezone, timedelta
from models import db  # Make sure db is initialized in models.py
from sqlalchemy import Numeric

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # e.g. "Top-up", "Payment"
    amount = db.Column(Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)  # e.g. "Student top-up", "Food order - Nasi Lemak"
    transaction_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))

    def __repr__(self):
        return f"<Transaction {self.type} | RM{self.amount} | {self.transaction_time}>"
