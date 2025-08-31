from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()

class StudentInfo(db.Model, UserMixin):
    __tablename__ = 'student_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ic_number = db.Column(db.String(4), unique=True)
    pin = db.Column(db.String(4), nullable=False)  # PIN for login
    password = db.Column(db.String(10),)  # Password for admin login
    role = db.Column(db.String(10), default='student')  # 'admin' or 'student'
    balance = db.Column(db.Integer, default=0)
    frozen = db.Column(db.Boolean, default=False)

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    image_filename = db.Column(db.String(100))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'))
    quantity = db.Column(db.Integer)
    paid = db.Column(db.Boolean, default=False)
    student = db.relationship("StudentInfo", backref="orders")
    item = db.relationship('MenuItem', backref='orders')
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    is_done = db.Column(db.Boolean, default=False)
    
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    message = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    student = db.relationship('StudentInfo', backref='feedbacks')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    food_name = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    student = db.relationship('StudentInfo', backref='votes')

class TopUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    student = db.relationship('StudentInfo', backref='topups')
