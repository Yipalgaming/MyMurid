from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Constants for foreign key references
STUDENT_INFO_ID = 'student_info.id'

class StudentInfo(db.Model, UserMixin):
    __tablename__ = 'student_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ic_number = db.Column(db.String(50), unique=True, index=True)  # Supports Unicode, symbols, Chinese characters
    pin_hash = db.Column(db.String(255), nullable=False)  # Hashed PIN for login
    password_hash = db.Column(db.String(255))  # Hashed password for admin login
    role = db.Column(db.String(10), default='student', index=True)  # 'admin' or 'student'
    balance = db.Column(db.Integer, default=0)
    frozen = db.Column(db.Boolean, default=False)
    total_points = db.Column(db.Integer, default=0)  # Total points earned
    available_points = db.Column(db.Integer, default=0)  # Points available for redemption
    
    def set_pin(self, pin):
        """Hash and store PIN"""
        self.pin_hash = generate_password_hash(pin)
    
    def check_pin(self, pin):
        """Check PIN against hash"""
        if not self.pin_hash:
            return False
        return check_password_hash(self.pin_hash, pin)
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @property
    def pin(self):
        """Legacy property for backward compatibility"""
        return self.pin_hash
    
    @pin.setter
    def pin(self, value):
        """Legacy setter for backward compatibility"""
        self.set_pin(value)

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    category = db.Column(db.String(50), index=True)
    image_path = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID), index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), index=True)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='pending', index=True)
    student = db.relationship("StudentInfo", backref="orders")
    item = db.relationship('MenuItem', backref='orders', foreign_keys=[menu_item_id])
    order_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), index=True)
    payment_status = db.Column(db.String(20), default='unpaid', index=True)
    
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    message = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID))
    student = db.relationship('StudentInfo', backref='feedbacks')
    media = db.relationship(
        'FeedbackMedia',
        backref='feedback',
        cascade='all, delete-orphan',
        order_by='FeedbackMedia.uploaded_at'
    )


class FeedbackMedia(db.Model):
    __tablename__ = 'feedback_media'

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False, index=True)
    file_path = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(20), nullable=False)  # image or video
    original_filename = db.Column(db.String(255))
    mimetype = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    food_name = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID))
    student = db.relationship('StudentInfo', backref='votes')

class TopUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID))
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    student = db.relationship('StudentInfo', backref='topups')

class Parent(db.Model, UserMixin):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with children
    children = db.relationship('StudentInfo', secondary='parent_child', backref='parents')
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class ParentChild(db.Model):
    __tablename__ = 'parent_child'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID), nullable=False)
    relationship = db.Column(db.String(20), default='parent')  # parent, guardian, etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), default='bank_qr')
    qr_code_data = db.Column(db.Text)  # Store QR code data
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    bank_reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    completed_at = db.Column(db.DateTime)
    
    parent = db.relationship('Parent', backref='payments')
    student = db.relationship('StudentInfo', backref='payments')

# Rewards & Gamification System
class RewardCategory(db.Model):
    __tablename__ = 'reward_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # behavior, academic, participation
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    color = db.Column(db.String(20))  # Color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))

class Achievement(db.Model):
    __tablename__ = 'achievement'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('reward_category.id'), nullable=False)
    points_value = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50))
    badge_color = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    category = db.relationship('RewardCategory', backref='achievements')

class StudentPoints(db.Model):
    __tablename__ = 'student_points'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    awarded_by = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID))  # Admin/teacher who awarded
    reason = db.Column(db.Text)  # Specific reason for earning points
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    student = db.relationship('StudentInfo', foreign_keys=[student_id], backref='points_earned')
    achievement = db.relationship('Achievement', backref='student_earnings')
    awarded_by_user = db.relationship('StudentInfo', foreign_keys=[awarded_by])

class RewardItem(db.Model):
    __tablename__ = 'reward_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_cost = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2))  # For discount rewards
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'))  # For specific item rewards
    reward_type = db.Column(db.String(20), default='discount')  # discount, free_item, cash_credit
    is_active = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer)  # For limited items
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    menu_item = db.relationship('MenuItem', backref='reward_items')

class StudentRedemption(db.Model):
    __tablename__ = 'student_redemption'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(STUDENT_INFO_ID), nullable=False)
    reward_item_id = db.Column(db.Integer, db.ForeignKey('reward_item.id'), nullable=False)
    points_used = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, redeemed, expired
    redeemed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    student = db.relationship('StudentInfo', backref='redemptions')
    reward_item = db.relationship('RewardItem', backref='redemptions')

class Directory(db.Model):
    __tablename__ = 'directory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)  # e.g., "Principal", "Mathematics Teacher"
    department = db.Column(db.String(100), nullable=False)  # e.g., "Administration", "Mathematics", "Science"
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    office_location = db.Column(db.String(100))  # e.g., "Room 101", "Main Office"
    floor_level = db.Column(db.Integer, default=1)  # Floor number (1, 2, 3, etc.)
    zone_area = db.Column(db.String(100))  # Zone/area on the map (e.g., "A1", "North Wing", "Building A")
    map_x = db.Column(db.Float)  # X coordinate on map (0-100 percentage)
    map_y = db.Column(db.Float)  # Y coordinate on map (0-100 percentage)
    bio = db.Column(db.Text)
    photo_path = db.Column(db.String(100))  # Path to staff photo
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)  # For ordering within department
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone(timedelta(hours=8))))

class Facility(db.Model):
    __tablename__ = 'facility'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Classroom 101", "Science Lab 1", "Library"
    facility_type = db.Column(db.String(50), nullable=False)  # classroom, lab, library, canteen, gym, office, restroom, etc.
    floor_level = db.Column(db.Integer, default=1)
    zone_area = db.Column(db.String(100))  # Zone/area on the map
    room_number = db.Column(db.String(20))  # Room number/identifier
    map_x = db.Column(db.Float)  # X coordinate on map (0-100 percentage)
    map_y = db.Column(db.Float)  # Y coordinate on map (0-100 percentage)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer)  # For classrooms/labs
    icon = db.Column(db.String(50), default='fas fa-door-open')  # Font Awesome icon class
    color = db.Column(db.String(20), default='blue')  # Color for the icon/marker
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone(timedelta(hours=8))))
