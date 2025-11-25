from models import db  # Make sure db is initialized in models.py
from sqlalchemy import Numeric
from tz_utils import now_myt

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'), nullable=True, index=True)  # Nullable for system transactions
    type = db.Column(db.String(50), nullable=False)  # e.g. "Top-up", "Payment"
    amount = db.Column(Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)  # e.g. "Student top-up", "Food order - Nasi Lemak"
    transaction_time = db.Column(db.DateTime, default=now_myt)
    
    # Relationship to StudentInfo
    student = db.relationship('StudentInfo', backref='transactions', foreign_keys=[student_id])

    def __repr__(self):
        return f"<Transaction {self.type} | RM{self.amount} | {self.transaction_time}>"
