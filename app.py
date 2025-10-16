from flask import Flask, render_template, request, redirect, jsonify, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, StudentInfo, MenuItem, Order, Vote, Feedback, Parent, ParentChild, Payment, RewardCategory, Achievement, StudentPoints, RewardItem, StudentRedemption
import os, json
from barcode import Code128
from barcode.writer import ImageWriter
from flask_migrate import Migrate
from flask_migrate import upgrade as alembic_upgrade
from werkzeug.security import generate_password_hash, check_password_hash
from transactions import Transaction
from sqlalchemy import func
from sqlalchemy.engine import make_url
from datetime import timedelta, datetime, timezone
from config import config
from error_handlers import register_error_handlers
import re
from functools import wraps
import time

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[Startup] Loaded environment variables from .env file")
except ImportError:
    print("[Startup] python-dotenv not installed, skipping .env file")
except Exception as e:
    print(f"[Startup] Error loading .env file: {e}")

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[config_name])

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
# csrf = CSRFProtect(app)  # Temporarily disabled for testing

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register error handlers
register_error_handlers(app)
# Log masked database URI details at startup (without secrets)
try:
    _uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if _uri:
        _url = make_url(_uri)
        masked = f"{_url.drivername}://{_url.host}:{_url.port}/{_url.database}"
        print(f"[Startup] Using database: {masked}")
except Exception as _e:
    print(f"[Startup] Could not parse DB URI: {_e}")



# Constants for error messages
STUDENT_NOT_FOUND = "Student not found."
INVALID_CREDENTIALS = "Invalid IC or PIN."
ACCESS_DENIED = "Access denied."
ACCOUNT_FROZEN = "Account is frozen. Please contact an admin."
INSUFFICIENT_BALANCE = "Not enough balance."
INVALID_IC_FORMAT = "Invalid IC number format."
INVALID_PIN_FORMAT = "Invalid PIN format."
INVALID_AMOUNT = "Invalid amount. Please enter a positive number."
ACCESS_DENIED = "Access denied."

# Input validation functions
def validate_ic_number(ic):
    """Validate IC number format"""
    if not ic or not re.match(r'^\d{4}$', ic):
        return False
    return True

def validate_pin(pin):
    """Validate PIN format"""
    if not pin or not re.match(r'^\d{4}$', pin):
        return False
    return True

def validate_amount(amount):
    """Validate amount is positive number"""
    try:
        amount = float(amount)
        return amount > 0
    except (ValueError, TypeError):
        return False

def validate_name(name):
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        return False
    # Allow letters, spaces, hyphens, and apostrophes
    return re.match(r"^[a-zA-Z\s\-']+$", name.strip()) is not None

def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 6:
        return False
    return True

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    # Remove HTML tags and escape special characters
    import html
    return html.escape(text.strip())

# Rate limiting decorator
def rate_limit(max_requests=99, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (for production, use Redis)
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Initialize rate limit storage
            if not hasattr(app, 'rate_limit_storage'):
                app.rate_limit_storage = {}
            
            # Clean old entries
            app.rate_limit_storage = {
                ip: requests for ip, requests in app.rate_limit_storage.items()
                if any(req_time > current_time - window for req_time in requests)
            }
            
            # Check rate limit
            if client_ip in app.rate_limit_storage:
                requests = [req_time for req_time in app.rate_limit_storage[client_ip] 
                           if req_time > current_time - window]
                print(f"Rate limit check for {client_ip}: {len(requests)}/{max_requests} requests in {window}s")
                if len(requests) >= max_requests:
                    print(f"Rate limit exceeded for {client_ip}, redirecting to rate limit page")
                    flash('Too many requests. Please try again later.', 'error')
                    return redirect(url_for('rate_limit_exceeded'))
                app.rate_limit_storage[client_ip].append(current_time)
            else:
                app.rate_limit_storage[client_ip] = [current_time]
                print(f"First request from {client_ip}, initializing rate limit")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Security headers decorator
def add_security_headers(f):
    """Add security headers to responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    return decorated_function

def safe_get_student(ic_number):
    """Safely get student with error handling"""
    try:
        if not validate_ic_number(ic_number):
            return None
        return StudentInfo.query.filter_by(ic_number=ic_number).first()
    except Exception as e:
        app.logger.error(f"Database error getting student {ic_number}: {str(e)}")
        return None

@app.before_request
def make_session_non_permanent():
    session.permanent = False

@login_manager.user_loader
def load_user(user_id):
    # Check if this is a parent or student based on session
    # For now, try parent first, then student
    print(f"Loading user with ID: {user_id}")
    
    # Try to load student first (since parent table doesn't exist)
    try:
        user = StudentInfo.query.get(int(user_id))
        if user:
            print(f"Loaded student user: {user.name}")
            return user
    except Exception as e:
        print(f"Error loading student: {e}")
        # Rollback the transaction to clear the failed state
        db.session.rollback()
    
    # Try to load parent (if parent table exists)
    try:
        user = Parent.query.get(int(user_id))
        if user:
            print(f"Loaded parent user: {user.name}")
            return user
    except Exception as e:
        print(f"Parent table not available: {e}")
        # Rollback the transaction to clear the failed state
        db.session.rollback()
    
    print(f"No user found with ID: {user_id}")
    return None

@app.context_processor
def inject_user():
    return {'user': current_user}

@app.context_processor
def inject_csrf_token():
    """Make CSRF token available in templates"""
    from flask_wtf.csrf import generate_csrf
    return {'csrf_token': generate_csrf}

def inject_request():
    return {"request": request}

@app.route('/register')
def register():
    # Students do not register via this app; redirect to parent registration
    return redirect(url_for('parent_register'))

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Check if it's a Parent user (no role attribute)
        if hasattr(current_user, 'role'):
            if current_user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
        else:
            # Parent user - redirect to parent dashboard
            return redirect(url_for('parent_dashboard'))
    return redirect(url_for('login'))

@app.route('/rate-limit-exceeded')
def rate_limit_exceeded():
    """Show rate limit exceeded page"""
    return render_template('rate_limit.html')



@app.route('/login', methods=['GET', 'POST'])
@add_security_headers
def login():
    print(f"Login route accessed, method: {request.method}")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"User already authenticated: {current_user.name}, role: {current_user.role}")
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        try:
            ic = request.form.get('ic', '').strip()
            pin = request.form.get('pin', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"Login attempt: IC={ic}, PIN={'*' * len(pin)}")
            
            # Input validation
            if not validate_ic_number(ic) or not validate_pin(pin):
                print(f"Validation failed: IC={ic}, PIN={'*' * len(pin)}")
                flash(INVALID_IC_FORMAT, 'error')
                return redirect(url_for('login'))
            
            print(f"Validation passed, looking up student: {ic}")
            user = safe_get_student(ic)
            print(f"Student lookup result: {user}")
            if not user:
                print(f"Student not found: {ic}")
                flash(INVALID_CREDENTIALS, 'error')
                return redirect(url_for('login'))

            # Check PIN
            if not user.check_pin(pin):
                print(f"Invalid PIN for student: {ic}")
                flash(INVALID_CREDENTIALS, 'error')
                return redirect(url_for('login'))
            
            # Check password for admin/staff
            if user.role in ['admin', 'staff']:
                if not password:
                    flash('Password is required for admin/staff.', 'error')
                    return redirect(url_for('login'))
                if not user.check_password(password):
                    flash('Invalid password for admin/staff.', 'error')
                    return redirect(url_for('login'))
            
            # Check if account is frozen
            if user.frozen:
                print(f"Account frozen for student: {ic}")
                flash(ACCOUNT_FROZEN, 'error')
                return redirect(url_for('login'))
            
            print(f"Login successful for user: {user.name}, role: {user.role}")
            login_user(user, remember=False)
            flash('Login successful!', 'success')
            
            # Clear rate limit on successful login
            client_ip = request.remote_addr
            if hasattr(app, 'rate_limit_storage') and client_ip in app.rate_limit_storage:
                del app.rate_limit_storage[client_ip]
                print(f"Cleared rate limit for {client_ip} after successful login")
            
            if user.role == 'admin':
                print(f"Redirecting admin {user.name} to admin dashboard")
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'staff':
                print(f"Redirecting staff {user.name} to staff dashboard")
                return redirect(url_for('staff_dashboard'))
            else:
                print(f"Redirecting student {user.name} to student dashboard")
                return redirect(url_for('student_dashboard'))
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('login'))

# Parent Authentication Routes
@app.route('/parent/register', methods=['GET', 'POST'])
def parent_register():
    print(f"Parent register route accessed, method: {request.method}")
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        email = sanitize_input(request.form.get('email', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not validate_name(name):
            flash('Please enter a valid name.', 'error')
            return redirect(url_for('parent_register'))
        
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('parent_register'))
        
        if not validate_password(password):
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('parent_register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('parent_register'))
        
        # Check if email already exists
        existing_parent = Parent.query.filter_by(email=email).first()
        if existing_parent:
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('parent_register'))
        
        try:
            # Create new parent
            new_parent = Parent(
                name=name,
                email=email,
                phone=phone
            )
            new_parent.set_password(password)
            
            db.session.add(new_parent)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            print(f"Parent registration successful for {email}, redirecting to parent_login")
            return redirect(url_for('parent_login'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Parent registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('parent_register'))
    
    return render_template('parent_register.html')

@app.route('/parent/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=300)
@add_security_headers
def parent_login():
    print(f"Parent login route accessed, method: {request.method}")
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('parent_login'))
        
        parent = Parent.query.filter_by(email=email).first()
        if not parent or not parent.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('parent_login'))
        
        if not parent.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('parent_login'))
        
        login_user(parent, remember=False)
        flash('Login successful!', 'success')
        print(f"Parent {email} logged in successfully, redirecting to parent_dashboard")
        return redirect(url_for('parent_dashboard'))
    
    return render_template('parent_login.html')

@app.route('/parent/dashboard')
@login_required
def parent_dashboard():
    print(f"Parent dashboard accessed by user: {current_user.name if hasattr(current_user, 'name') else 'Unknown'}")
    if not hasattr(current_user, 'email'):  # Not a parent
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    # Get parent's children
    children = current_user.children
    recent_payments = Payment.query.filter_by(parent_id=current_user.id).order_by(Payment.created_at.desc()).limit(5).all()
    
    return render_template('parent_dashboard.html', 
                         children=children, 
                         recent_payments=recent_payments)

@app.route('/parent/add-child', methods=['GET', 'POST'])
@login_required
def add_child():
    if not hasattr(current_user, 'email'):  # Not a parent
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        child_ic = sanitize_input(request.form.get('child_ic', ''))
        relationship = sanitize_input(request.form.get('relationship', 'parent'))
        
        if not validate_ic_number(child_ic):
            flash('Please enter a valid 4-digit IC number.', 'error')
            return redirect(url_for('add_child'))
        
        # Find child
        child = StudentInfo.query.filter_by(ic_number=child_ic).first()
        if not child:
            flash('Student not found. Please check the IC number.', 'error')
            return redirect(url_for('add_child'))
        
        # Check if relationship already exists
        existing = ParentChild.query.filter_by(
            parent_id=current_user.id, 
            child_id=child.id
        ).first()
        
        if existing:
            flash('This child is already linked to your account.', 'error')
            return redirect(url_for('add_child'))
        
        try:
            # Create parent-child relationship
            parent_child = ParentChild(
                parent_id=current_user.id,
                child_id=child.id,
                relationship=relationship
            )
            
            db.session.add(parent_child)
            db.session.commit()
            
            flash(f'Successfully linked {child.name} to your account.', 'success')
            return redirect(url_for('parent_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Add child error: {str(e)}")
            flash('Failed to link child. Please try again.', 'error')
            return redirect(url_for('add_child'))
    
    return render_template('add_child.html')

# Bank QR Payment API Routes
@app.route('/parent/payment/<int:child_id>', methods=['GET', 'POST'])
@login_required
def parent_payment(child_id):
    if not hasattr(current_user, 'email'):  # Not a parent
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    # Verify child belongs to parent
    child = StudentInfo.query.get(child_id)
    if not child or child not in current_user.children:
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('parent_dashboard'))
    
    if request.method == 'POST':
        amount = request.form.get('amount', '')
        
        if not validate_amount(amount):
            flash('Please enter a valid amount.', 'error')
            return redirect(url_for('parent_payment', child_id=child_id))
        
        amount_decimal = float(amount)
        
        try:
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())
            
            # Create payment record
            payment = Payment(
                parent_id=current_user.id,
                student_id=child.id,
                amount=amount_decimal,
                payment_method='bank_qr',
                transaction_id=transaction_id,
                status='pending'
            )
            
            # Generate QR code data (simplified - in real implementation, use bank API)
            qr_data = generate_bank_qr_code(amount_decimal, transaction_id)
            payment.qr_code_data = qr_data
            
            db.session.add(payment)
            db.session.commit()
            
            return render_template('payment_qr.html', 
                                 payment=payment, 
                                 child=child,
                                 qr_data=qr_data)
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Payment creation error: {str(e)}")
            flash('Failed to create payment. Please try again.', 'error')
            return redirect(url_for('parent_payment', child_id=child_id))
    
    return render_template('parent_payment.html', child=child)

@app.route('/api/payment/status/<transaction_id>')
@login_required
def check_payment_status(transaction_id):
    if not hasattr(current_user, 'email'):  # Not a parent
        return jsonify({'error': ACCESS_DENIED}), 403
    
    payment = Payment.query.filter_by(
        transaction_id=transaction_id,
        parent_id=current_user.id
    ).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Check payment status with real payment provider
    from bank_qr_integration import get_payment_provider
    from payment_config import payment_config
    
    try:
        # Get payment provider
        provider = get_payment_provider(payment_config.provider, payment_config.get_config())
        
        # Check payment status with provider
        result = provider.check_payment_status(transaction_id)
        
        if result['success']:
            # Update payment status based on provider response
            if result['status'] == 'completed' and payment.status == 'pending':
                payment.status = 'completed'
                payment.completed_at = datetime.now(timezone(timedelta(hours=8)))
                payment.bank_reference = result.get('reference_id')
                
                # Add balance to child's account
                child = StudentInfo.query.get(payment.student_id)
                if child:
                    child.balance += int(payment.amount)
                    db.session.commit()
        else:
            # Fallback to mock behavior for testing
            import time
            if time.time() - payment.created_at.timestamp() > 30:
                if payment.status == 'pending':
                    payment.status = 'completed'
                    payment.completed_at = datetime.now(timezone(timedelta(hours=8)))
                    
                    # Add balance to child's account
                    child = StudentInfo.query.get(payment.student_id)
                    if child:
                        child.balance += int(payment.amount)
                        db.session.commit()
    
    except Exception as e:
        app.logger.error(f"Payment status check error: {str(e)}")
        # Fallback to mock behavior
        import time
        if time.time() - payment.created_at.timestamp() > 30:
            if payment.status == 'pending':
                payment.status = 'completed'
                payment.completed_at = datetime.now(timezone(timedelta(hours=8)))
                
                # Add balance to child's account
                child = StudentInfo.query.get(payment.student_id)
                if child:
                    child.balance += int(payment.amount)
                    db.session.commit()
    
    return jsonify({
        'status': payment.status,
        'amount': float(payment.amount),
        'transaction_id': payment.transaction_id,
        'created_at': payment.created_at.isoformat(),
        'completed_at': payment.completed_at.isoformat() if payment.completed_at else None
    })

def generate_bank_qr_code(amount, transaction_id):
    """Generate bank QR code data using real payment provider"""
    from bank_qr_integration import get_payment_provider
    from payment_config import payment_config
    
    try:
        # Get payment provider
        provider = get_payment_provider(payment_config.provider, payment_config.get_config())
        
        # Generate QR payment
        result = provider.generate_qr_payment(
            amount=float(amount),
            transaction_id=transaction_id,
            description="MyMurid Canteen Top-up"
        )
        
        if result['success']:
            return result['qr_data']
        else:
            app.logger.error(f"QR generation failed: {result['error']}")
            # Fallback to mock QR
            return f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890"
            
    except Exception as e:
        app.logger.error(f"QR generation error: {str(e)}")
        # Fallback to mock QR
        return f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890"

# Rewards & Gamification Routes
@app.route('/rewards')
@login_required
def rewards_dashboard():
    """Student rewards dashboard"""
    if current_user.role != 'student':
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    # Get student's points and achievements
    student_points = StudentPoints.query.filter_by(student_id=current_user.id).order_by(StudentPoints.created_at.desc()).limit(10).all()
    available_rewards = RewardItem.query.filter_by(is_active=True).all()
    recent_redemptions = StudentRedemption.query.filter_by(student_id=current_user.id).order_by(StudentRedemption.created_at.desc()).limit(5).all()
    
    # Get achievements by category
    categories = RewardCategory.query.filter_by(is_active=True).all()
    achievements_by_category = {}
    for category in categories:
        achievements_by_category[category.name] = Achievement.query.filter_by(category_id=category.id, is_active=True).all()
    
    return render_template('rewards_dashboard.html', 
                         student_points=student_points,
                         available_rewards=available_rewards,
                         recent_redemptions=recent_redemptions,
                         categories=categories,
                         achievements_by_category=achievements_by_category)

@app.route('/rewards/redeem/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    """Redeem a reward item"""
    if current_user.role != 'student':
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    reward_item = RewardItem.query.get(reward_id)
    if not reward_item or not reward_item.is_active:
        flash('Reward not found or no longer available.', 'error')
        return redirect(url_for('rewards_dashboard'))
    
    if current_user.available_points < reward_item.points_cost:
        flash('Insufficient points to redeem this reward.', 'error')
        return redirect(url_for('rewards_dashboard'))
    
    # Check stock if applicable
    if reward_item.stock_quantity is not None and reward_item.stock_quantity <= 0:
        flash('This reward is out of stock.', 'error')
        return redirect(url_for('rewards_dashboard'))
    
    try:
        # Create redemption record
        redemption = StudentRedemption(
            student_id=current_user.id,
            reward_item_id=reward_item.id,
            points_used=reward_item.points_cost,
            status='pending',
            expires_at=datetime.now(timezone(timedelta(hours=8))) + timedelta(days=30)  # 30 days to use
        )
        
        # Update student's available points
        current_user.available_points -= reward_item.points_cost
        
        # Update stock if applicable
        if reward_item.stock_quantity is not None:
            reward_item.stock_quantity -= 1
        
        db.session.add(redemption)
        db.session.commit()
        
        flash(f'Successfully redeemed {reward_item.name}! Check your redemptions.', 'success')
        return redirect(url_for('rewards_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Redemption error: {str(e)}")
        flash('Failed to redeem reward. Please try again.', 'error')
        return redirect(url_for('rewards_dashboard'))

@app.route('/admin/award-points', methods=['GET', 'POST'])
@login_required
def award_points():
    """Admin interface to award points to students"""
    if current_user.role not in ['admin', 'staff']:
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        student_ic = sanitize_input(request.form.get('student_ic', ''))
        achievement_id = request.form.get('achievement_id')
        reason = sanitize_input(request.form.get('reason', ''))
        
        if not validate_ic_number(student_ic):
            flash('Please enter a valid 4-digit IC number.', 'error')
            return redirect(url_for('award_points'))
        
        student = StudentInfo.query.filter_by(ic_number=student_ic).first()
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('award_points'))
        
        achievement = Achievement.query.get(achievement_id)
        if not achievement:
            flash('Invalid achievement selected.', 'error')
            return redirect(url_for('award_points'))
        
        try:
            # Award points
            student_points = StudentPoints(
                student_id=student.id,
                achievement_id=achievement.id,
                points_earned=achievement.points_value,
                awarded_by=current_user.id,
                reason=reason
            )
            
            # Update student's total and available points
            student.total_points += achievement.points_value
            student.available_points += achievement.points_value
            
            db.session.add(student_points)
            db.session.commit()
            
            flash(f'Awarded {achievement.points_value} points to {student.name} for {achievement.name}!', 'success')
            return redirect(url_for('award_points'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Points award error: {str(e)}")
            flash('Failed to award points. Please try again.', 'error')
            return redirect(url_for('award_points'))
    
    # Get all students and achievements for the form
    students = StudentInfo.query.filter_by(role='student').all()
    achievements = Achievement.query.filter_by(is_active=True).all()
    categories = RewardCategory.query.filter_by(is_active=True).all()
    
    return render_template('admin_award_points.html', 
                         students=students,
                         achievements=achievements,
                         categories=categories)

@app.route('/admin/manage-rewards', methods=['GET', 'POST'])
@login_required
def manage_rewards():
    """Admin interface to manage reward items"""
    if current_user.role not in ['admin', 'staff']:
        flash(ACCESS_DENIED, 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        description = sanitize_input(request.form.get('description', ''))
        points_cost = request.form.get('points_cost')
        reward_type = request.form.get('reward_type', 'discount')
        discount_percentage = request.form.get('discount_percentage')
        menu_item_id = request.form.get('menu_item_id')
        stock_quantity = request.form.get('stock_quantity')
        
        if not name or not points_cost:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('manage_rewards'))
        
        try:
            reward_item = RewardItem(
                name=name,
                description=description,
                points_cost=int(points_cost),
                reward_type=reward_type,
                discount_percentage=float(discount_percentage) if discount_percentage else None,
                menu_item_id=int(menu_item_id) if menu_item_id else None,
                stock_quantity=int(stock_quantity) if stock_quantity else None
            )
            
            db.session.add(reward_item)
            db.session.commit()
            
            flash(f'Successfully added reward: {name}', 'success')
            return redirect(url_for('manage_rewards'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Reward creation error: {str(e)}")
            flash('Failed to create reward. Please try again.', 'error')
            return redirect(url_for('manage_rewards'))
    
    # Get all reward items and menu items
    reward_items = RewardItem.query.all()
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    
    return render_template('admin_manage_rewards.html', 
                         reward_items=reward_items,
                         menu_items=menu_items)

@app.route('/api/apply-reward/<int:redemption_id>')
@login_required
def apply_reward(redemption_id):
    """Apply a redeemed reward to an order (for staff use)"""
    if current_user.role not in ['admin', 'staff']:
        return jsonify({'error': ACCESS_DENIED}), 403
    
    redemption = StudentRedemption.query.get(redemption_id)
    if not redemption or redemption.status != 'pending':
        return jsonify({'error': 'Invalid or already used redemption'}), 400
    
    # Mark as redeemed
    redemption.status = 'redeemed'
    redemption.redeemed_at = datetime.now(timezone(timedelta(hours=8)))
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'reward_name': redemption.reward_item.name,
        'discount_percentage': float(redemption.reward_item.discount_percentage) if redemption.reward_item.discount_percentage else None,
        'message': f'Applied {redemption.reward_item.name} successfully!'
    })

@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role == 'student':
        return render_template('dashboard.html', user=current_user)
    else:
        return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    print(f"Admin dashboard accessed by user: {current_user.name}, role: {current_user.role}")
    if current_user.role == 'admin':
        return render_template('admin.html', user=current_user)
    else:
        print(f"User {current_user.name} with role {current_user.role} redirected to home")
        return redirect(url_for('home'))

@app.route('/staff')
@login_required
def staff_dashboard():
    if current_user.role == 'staff':
        return render_template('staff.html', user=current_user)
    else:
        return redirect(url_for('home'))

def get_menu_data():
    """Get menu items and categories for order page"""
    items = MenuItem.query.filter_by(is_available=True).order_by(MenuItem.category, MenuItem.name).all()
    categories = db.session.query(MenuItem.category).filter(
        MenuItem.is_available == True,
        MenuItem.category.isnot(None)
    ).distinct().all()
    return items, [cat[0] for cat in categories]

def validate_cart_data(cart_json):
    """Validate and parse cart data from request"""
    try:
        cart_items = json.loads(cart_json)
        if not cart_items:
            raise ValueError("Cart is empty")
        return cart_items
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid cart data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid cart data: {str(e)}")

def create_orders_from_cart(cart_items, student_id):
    """Create order records from cart items"""
    orders_created = 0
    for entry in cart_items:
        item = MenuItem.query.get(entry["id"])
        if not item:
            continue
        
        total_price = item.price * entry["quantity"]
        order = Order(
            student_id=student_id,
            menu_item_id=item.id,
            quantity=entry["quantity"],
            total_price=total_price,
            payment_status='unpaid'
        )
        db.session.add(order)
        orders_created += 1
    
    return orders_created

@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    """Handle order page display and order submission"""
    if request.method == "POST":
        return handle_order_submission()
    
    items, categories = get_menu_data()
    return render_template("order.html", items=items, categories=categories)

def handle_order_submission():
    """Handle order submission from cart"""
    try:
        cart_items = validate_cart_data(request.form.get("cart_items"))
    except ValueError as e:
        flash(f"❌ {str(e)}", "error")
        return redirect(url_for("order"))

    student = StudentInfo.query.get(current_user.id)
    if not student:
        flash("❌ Student not found.", "error")
        return redirect(url_for("order"))

    try:
        orders_created = create_orders_from_cart(cart_items, student.id)
        db.session.commit()
        
        if orders_created > 0:
            flash("✅ Order submitted! Proceed to payment.", "success")
            return redirect(url_for("payment"))
        else:
            flash("❌ No valid items in cart.", "error")
            return redirect(url_for("order"))
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Order submission error: {str(e)}")
        flash("❌ Order submission failed. Please try again.", "error")
        return redirect(url_for("order"))

@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    student = StudentInfo.query.get(current_user.id)

    if request.method == "POST":
        if "delete" in request.form:
            return handle_order_delete(student)
        if "pay" in request.form:
            return handle_order_payment(student)

    unpaid_orders = Order.query.filter_by(student_id=student.id, payment_status='unpaid').all()
    total = sum(order.total_price for order in unpaid_orders)
    return render_template("payment.html", cart_items=unpaid_orders, total=total, user=student)

def handle_order_delete(student):
    order_id = request.form.get("delete")
    order = Order.query.get(order_id)
    if order and order.student_id == student.id and order.payment_status == 'unpaid':
        db.session.delete(order)
        db.session.commit()
        flash("🗑️ Order deleted.", "success")
    else:
        flash("❌ Order not found or already paid.", "error")
    return redirect(url_for("payment"))

def validate_payment_conditions(student, unpaid_orders):
    """Validate payment conditions before processing"""
    if not unpaid_orders:
        raise ValueError("No unpaid orders found")

    if student.frozen:
        raise ValueError(ACCOUNT_FROZEN)

    total_amount = sum(float(order.total_price) for order in unpaid_orders)
    if student.balance < total_amount:
        raise ValueError(INSUFFICIENT_BALANCE)

    return total_amount

def process_payment_transaction(student, unpaid_orders, total_amount):
    """Process the payment transaction"""
    # Update student balance
    student.balance -= total_amount
    
    # Mark orders as paid
    for order in unpaid_orders:
        order.payment_status = 'paid'
        
    # Create transaction record
    new_tx = Transaction(
        type="Payment",
        amount=-total_amount,
        description=f"Payment for {len(unpaid_orders)} items"
        )
    db.session.add(new_tx)

def handle_order_payment(student):
    """Handle order payment processing"""
    try:
        unpaid_orders = Order.query.filter_by(student_id=student.id, payment_status='unpaid').all()
        total_amount = validate_payment_conditions(student, unpaid_orders)
        
        process_payment_transaction(student, unpaid_orders, total_amount)
        db.session.commit()
        
        flash("✅ Payment successful!", "success")
        return redirect(url_for("student_dashboard"))
        
    except ValueError as e:
        flash(f"❌ {str(e)}", "error")
        return redirect(url_for("payment"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Payment error for student {student.id}: {str(e)}")
        flash("❌ Payment failed. Please try again.", "error")
        return redirect(url_for("payment"))


@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    order = session.pop('pending_order', None)
    if not order:
        flash("No order found.", "warning")
        return redirect(url_for('order'))

    # Save order to database here...

    flash("Payment successful!", "success")
    return redirect(url_for('student_dashboard'))

@app.route("/paid-orders", methods=["GET", "POST"])
@login_required
def paid_orders():
    if current_user.role not in ['admin', 'staff']:
        flash(ACCESS_DENIED, "error")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        order_id = request.form.get("order_id")
        order = Order.query.get(order_id)
        if order:
            order.status = 'completed'  # Fixed: use status instead of done
            db.session.commit()
            flash("✅ Order marked as completed.", "success")
        return redirect(url_for("paid_orders"))

    # Optimize query with join to avoid N+1 queries
    paid_orders = db.session.query(Order, StudentInfo)\
        .join(StudentInfo)\
        .filter(Order.payment_status == 'paid')\
        .order_by(Order.order_time.desc())\
        .all()

    grouped = {}
    for order, student in paid_orders:
        if student not in grouped:
            grouped[student] = []
        grouped[student].append(order)

    # Sort orders by status (completed first)
    for orders in grouped.values():
        orders.sort(key=lambda x: x.status == 'completed', reverse=True)

    return render_template("paid_orders.html", grouped_orders=grouped)

@app.route("/mark-done/<int:id>", methods=["POST"])
@login_required
def mark_order_done(id):
    if current_user.role not in ['admin', 'staff']:
        flash("Unauthorized access", "error")
        return redirect(url_for("paid_orders"))

    order = Order.query.get(id)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("paid_orders"))

    order.status = 'completed'
    db.session.commit()
    return redirect(url_for("paid_orders"))

@app.route("/delete-order/<int:id>", methods=["POST"])
@login_required
def delete_order(id):
    if current_user.role not in ['admin', 'staff']:
        flash("Unauthorized", "error")
        return redirect(url_for("paid_orders"))

    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash("Order deleted.", "success")
    return redirect(url_for("paid_orders"))

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    code = data.get('code')
    student = StudentInfo.query.filter_by(ic_number=code).first()
    if not student:
        return jsonify({"success": False, "message": "Student not found"})
    if student.frozen:
        return jsonify({"success": False, "message": "Card is frozen."})
    return jsonify({"success": True, "name": student.name, "balance": student.balance})

@app.route('/generate_barcode/<ic_number>')
def generate_barcode(ic_number):
    filename = f'static/barcodes/{ic_number}'
    if not os.path.exists(filename + '.png'):
        Code128(ic_number, writer=ImageWriter()).save(filename)
    return redirect(f'/{filename}.png')

@app.route('/test-barcodes')
def test_barcodes():
    return render_template('test_barcodes.html')

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        new_vote = Vote(food_name=food_name, student_id=current_user.id)
        db.session.add(new_vote)
        db.session.commit()
        return redirect(url_for('vote'))
    votes = Vote.query.all()
    return render_template('vote.html', votes=votes)

@app.route('/vote_summary')
@login_required
def vote_summary():
    summary = db.session.query(Vote.food_name, func.count(Vote.food_name)).group_by(Vote.food_name).all()
    return render_template("vote_summary.html", food_summary=summary)

@app.route('/delete_vote/<int:id>', methods=['POST'])
@login_required
def delete_vote(id):
    vote = Vote.query.get_or_404(id)
    if current_user.role == 'admin' or vote.student_id == current_user.id:
        db.session.delete(vote)
        db.session.commit()
        flash('Vote deleted.', 'success')
    else:
        flash('You can only delete your own vote.', 'error')
    return redirect(url_for('vote'))

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        message = request.form.get('message')
        new_feedback = Feedback(message=message, student_id=current_user.id)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('feedback'))
    feedbacks = Feedback.query.all()
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/delete_feedback/<int:id>', methods=['POST'])
@login_required
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if current_user.role == 'admin' or feedback.student_id == current_user.id:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted.', 'success')
    else:
        flash('You can only delete your own feedback.', 'error')
    return redirect(url_for('feedback'))

@app.route('/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        ic = request.form.get('ic', '').strip()
        amount = request.form.get('amount', '').strip()
        
        # Input validation
        if not validate_ic_number(ic):
            flash(INVALID_IC_FORMAT, 'error')
            return redirect(url_for('topup'))
        
        if not validate_amount(amount):
            flash(INVALID_AMOUNT, 'error')
            return redirect(url_for('topup'))
        
        student = safe_get_student(ic)
        if not student:
            flash(STUDENT_NOT_FOUND, 'error')
            return redirect(url_for('topup'))

        if student.frozen:
            flash(ACCOUNT_FROZEN, "error")
            return redirect(url_for("topup"))

        try:
            amount_int = int(amount)
            student.balance += amount_int
            
            new_tx = Transaction(
                type="Top-up",
                amount=amount_int,  # Fixed: use int instead of string
                description=f"Top-up for {student.name}"
            )
            db.session.add(new_tx)
            db.session.commit()
            flash(f"Successfully topped up RM{amount_int} for {student.name}.", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Top-up error: {str(e)}")
            flash("Error processing top-up. Please try again.", "error")

    return render_template("topup.html")

@app.route('/freeze_card', methods=['POST'])
@login_required
def freeze_card():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    ic = request.form.get('ic', '').strip()
    if not validate_ic_number(ic):
        flash(INVALID_IC_FORMAT, 'error')
        return redirect(url_for('admin_dashboard'))
    
    student = safe_get_student(ic)
    if student:
        student.frozen = True
        db.session.commit()
        flash(f"{student.name}'s card has been frozen.", "warning")
    else:
        flash(STUDENT_NOT_FOUND, "error")
    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_card_status', methods=['POST'])
@login_required
def toggle_card_status():
    ic = request.form.get('ic', '').strip()
    action = request.form.get('action')

    if not validate_ic_number(ic):
        flash(INVALID_IC_FORMAT, 'error')
        return redirect(url_for('manage_students'))

    student = safe_get_student(ic)
    if not student:
        flash(STUDENT_NOT_FOUND, "error")
    else:
        if action == 'freeze':
            student.frozen = True
            flash(f"{student.name}'s card has been frozen.", "warning")
        elif action == 'unfreeze':
            student.frozen = False
            flash(f"{student.name}'s card has been unfrozen.", "success")
        else:
            flash("Invalid action.", "error")
            return redirect(url_for('manage_students'))
        db.session.commit()

    return redirect(url_for('manage_students'))

@app.route('/student_balances')
@login_required
def student_balances():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    students = StudentInfo.query.order_by(StudentInfo.name).all()
    return render_template('student_balances.html', students=students)

@app.route('/transactions')
@login_required
def transactions():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    logs = Transaction.query.order_by(Transaction.transaction_time.desc()).all()
    total_in = sum(t.amount for t in logs if t.amount > 0)
    total_out = sum(abs(t.amount) for t in logs if t.amount < 0)
    return render_template('transactions.html', logs=logs, total_in=total_in, total_out=total_out)

@app.route('/manage_students')
@login_required
def manage_students():
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    # Optimize query - use pagination for large datasets
    page = request.args.get('page', 1, type=int)
    students = StudentInfo.query.order_by(StudentInfo.name).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('manage_students.html', students=students)

def validate_student_form_data(form_data):
    """Validate all student form data"""
    name = form_data.get('name', '').strip()
    ic_number = form_data.get('ic_number', '').strip()
    pin = form_data.get('pin', '').strip()
    role = form_data.get('role', 'student').strip()
    balance = form_data.get('balance', '0').strip()
    password = form_data.get('password', '').strip()
    
    # Validate each field
    if not validate_name(name):
        raise ValueError('Name must be at least 2 characters long and contain only letters, spaces, hyphens, and apostrophes.')
    
    if not validate_ic_number(ic_number):
        raise ValueError(INVALID_IC_FORMAT)
    
    if not validate_pin(pin):
        raise ValueError(INVALID_PIN_FORMAT)
    
    if role not in ['student', 'staff', 'admin']:
        raise ValueError('Invalid role selected.')
    
    if not validate_amount(balance):
        raise ValueError(INVALID_AMOUNT)
    
    # Validate password for admin/staff roles
    if role in ['admin', 'staff']:
        if not password:
            raise ValueError('Password is required for admin and staff roles.')
        if not validate_password(password):
            raise ValueError('Password must be at least 6 characters long.')
    
    return {
        'name': name,
        'ic_number': ic_number,
        'pin': pin,
        'role': role,
        'balance': int(balance),
        'password': password
    }

def create_new_student(student_data):
    """Create a new student with validated data"""
    # Check if IC number already exists
    existing_student = safe_get_student(student_data['ic_number'])
    if existing_student:
        raise ValueError(f'Student with IC number {student_data["ic_number"]} already exists.')
    
    # Create new student
    new_student = StudentInfo(
        name=student_data['name'],
        ic_number=student_data['ic_number'],
        role=student_data['role'],
        balance=student_data['balance'],
        frozen=False
    )
    
    # Set PIN
    new_student.set_pin(student_data['pin'])
    
    # Set password for admin/staff
    if student_data['role'] in ['admin', 'staff']:
        new_student.set_password(student_data['password'])
    
    return new_student

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    """Handle adding a new student"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    try:
        student_data = validate_student_form_data(request.form)
        new_student = create_new_student(student_data)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash(f'✅ Successfully added student: {student_data["name"]} (IC: {student_data["ic_number"]})', 'success')
        return redirect(url_for('manage_students'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('manage_students'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding student: {str(e)}")
        flash('Error adding student. Please try again.', 'error')
        return redirect(url_for('manage_students'))

# Temporary endpoint to hash PINs and passwords for online database
@app.route('/hash-credentials', methods=['POST'])
def hash_credentials():
    """Hash PINs and passwords for existing users in online database"""
    try:
        # Get all users
        users = StudentInfo.query.all()
        
        if not users:
            return jsonify({'message': 'No users found', 'status': 'empty'})
        
        processed_users = []
        
        for user in users:
            user_info = {
                'name': user.name,
                'ic': user.ic_number,
                'role': user.role,
                'pin_hashed': bool(user.pin_hash),
                'password_hashed': bool(user.password_hash)
            }
            
            # Set default PIN if not already hashed
            if not user.pin_hash:
                user.set_pin("1234")  # Default PIN
                user_info['pin_action'] = 'hashed'
            else:
                user_info['pin_action'] = 'already_hashed'
            
            # Set default password for admin/staff if not already hashed
            if user.role in ['admin', 'staff'] and not user.password_hash:
                user.set_password("adminpass")  # Default password
                user_info['password_action'] = 'hashed'
            elif user.role in ['admin', 'staff'] and user.password_hash:
                user_info['password_action'] = 'already_hashed'
            else:
                user_info['password_action'] = 'not_needed'
            
            processed_users.append(user_info)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': 'Credentials hashed successfully',
            'status': 'success',
            'users_processed': len(processed_users),
            'users': processed_users
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'status': 'error'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
