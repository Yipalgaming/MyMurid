from flask import Flask, render_template, request, redirect, jsonify, flash, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, StudentInfo, MenuItem, Order, Vote, Feedback, FeedbackMedia, Parent, ParentChild, Payment, RewardCategory, Achievement, StudentPoints, RewardItem, StudentRedemption, Directory, Facility
import os, json, uuid
from barcode import Code128
from barcode.writer import ImageWriter
from flask_migrate import Migrate
from flask_migrate import upgrade as alembic_upgrade
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from transactions import Transaction
from sqlalchemy import func
from sqlalchemy.engine import make_url
from datetime import timedelta, datetime, timezone
from config import config
from error_handlers import register_error_handlers
import re
from functools import wraps
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

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

# Upload configuration
app.config.setdefault('FEEDBACK_UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads', 'feedback'))
app.config.setdefault('MENU_IMAGE_UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'images'))
app.config.setdefault('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)  # 50 MB limit for uploads

ALLOWED_MENU_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_FEEDBACK_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_FEEDBACK_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

# Ensure upload directories exist
for folder in [app.config['FEEDBACK_UPLOAD_FOLDER'], app.config['MENU_IMAGE_UPLOAD_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

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
    """Validate IC number format - allows Unicode characters (including Chinese), symbols, and alphanumeric"""
    if not ic:
        return False
    # Allow Unicode characters, symbols, and alphanumeric
    # Minimum 1 character, maximum 50 characters (reasonable limit)
    # This allows Chinese characters, symbols, emojis, etc.
    if len(ic) < 1 or len(ic) > 50:
        return False
    # Check if it contains at least one printable character (not just whitespace)
    if not ic.strip():
        return False
    return True

def validate_pin(pin):
    """Validate PIN format - must be exactly 4 digits"""
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

def is_allowed_file(filename, allowed_extensions):
    """Check if a filename has an allowed extension"""
    return bool(filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions)

def save_feedback_attachment(file_storage):
    """Save feedback attachment and return metadata"""
    filename = secure_filename(file_storage.filename or '')
    if not filename:
        raise ValueError("Invalid file name")
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension in ALLOWED_FEEDBACK_IMAGE_EXTENSIONS:
        media_type = 'image'
    elif extension in ALLOWED_FEEDBACK_VIDEO_EXTENSIONS:
        media_type = 'video'
    else:
        raise ValueError("Unsupported file type")
    
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config['FEEDBACK_UPLOAD_FOLDER'], unique_name)
    file_storage.save(save_path)
    
    relative_path = os.path.join('uploads', 'feedback', unique_name).replace('\\', '/')
    
    return {
        'file_path': relative_path,
        'media_type': media_type,
        'original_filename': file_storage.filename,
        'mimetype': file_storage.mimetype
    }

def delete_static_file(relative_path):
    """Delete a file from the static directory if it exists"""
    if not relative_path:
        return
    absolute_path = os.path.join(app.root_path, 'static', relative_path)
    try:
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
    except Exception as e:
        app.logger.warning(f"Failed to delete file {absolute_path}: {e}")

def save_menu_image(file_storage):
    """Save uploaded menu image and return stored filename"""
    filename = secure_filename(file_storage.filename or '')
    if not filename:
        raise ValueError("Invalid image file name")
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_MENU_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image format. Allowed: PNG, JPG, JPEG, GIF, WEBP")
    
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config['MENU_IMAGE_UPLOAD_FOLDER'], unique_name)
    file_storage.save(save_path)
    return unique_name

def delete_menu_image(filename):
    """Delete an existing menu image file"""
    if not filename:
        return
    absolute_path = os.path.join(app.config['MENU_IMAGE_UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
    except Exception as e:
        app.logger.warning(f"Failed to delete menu image {absolute_path}: {e}")

# Rate limiting decorator
def rate_limit(max_requests=5, window=300):
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

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png',
        mimetype='image/png'
    )

@login_manager.user_loader
def load_user(user_id):
    # Use session to determine user type to avoid ID conflicts
    print(f"Loading user with ID: {user_id}")
    user_type = session.get('user_type', 'student')  # Default to student for backward compatibility
    print(f"User type from session: {user_type}")
    
    if user_type == 'parent':
        # Try to load parent first
        try:
            user = Parent.query.get(int(user_id))
            if user:
                print(f"Loaded parent user: {user.name}")
                return user
        except Exception as e:
            print(f"Error loading parent: {e}")
            db.session.rollback()
    else:
        # Try to load student (default behavior)
        try:
            user = StudentInfo.query.get(int(user_id))
            if user:
                print(f"Loaded student user: {user.name}")
                return user
        except Exception as e:
            print(f"Error loading student: {e}")
            db.session.rollback()
    
    # Fallback: try the other type if the primary type failed
    if user_type == 'parent':
        try:
            user = StudentInfo.query.get(int(user_id))
            if user:
                print(f"Fallback: Loaded student user: {user.name}")
                return user
        except Exception as e:
            print(f"Fallback error loading student: {e}")
            db.session.rollback()
    else:
        try:
            user = Parent.query.get(int(user_id))
            if user:
                print(f"Fallback: Loaded parent user: {user.name}")
                return user
        except Exception as e:
            print(f"Fallback error loading parent: {e}")
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
            
            # Input validation - show same error message for format errors and invalid credentials
            if not validate_ic_number(ic) or not validate_pin(pin):
                print(f"Validation failed: IC={ic}, PIN={'*' * len(pin)}")
                flash(INVALID_CREDENTIALS, 'error')
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
            # Store user type in session to help load_user function
            session['user_type'] = 'student'
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
        print(f"User {current_user.name} logging out")
    # Clear user type from session
    session.pop('user_type', None)
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
        # Store user type in session to help load_user function
        session['user_type'] = 'parent'
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
            qr_data_result = generate_bank_qr_code(amount_decimal, transaction_id)
            
            # Extract qr_data from result - check both qr_data and qr_code fields
            if isinstance(qr_data_result, dict):
                qr_data = qr_data_result.get('qr_data') or qr_data_result.get('qr_code') or str(qr_data_result)
            else:
                qr_data = str(qr_data_result)
            
            # Ensure qr_data is not None or empty
            if not qr_data or qr_data.strip() == '':
                app.logger.error(f"QR data is empty for transaction {transaction_id}")
                qr_data = f"PAYMENT|{amount_decimal:.2f}|{transaction_id}|MyMurid"
            
            payment.qr_code_data = qr_data
            
            # Store bank account info if available
            bank_account = qr_data_result.get('bank_account') if isinstance(qr_data_result, dict) else None
            bank_name = qr_data_result.get('bank_name') if isinstance(qr_data_result, dict) else None
            
            db.session.add(payment)
            db.session.commit()
            
            return render_template('payment_qr.html', 
                                 payment=payment, 
                                 child=child,
                                 qr_data=qr_data,
                                 bank_account=bank_account,
                                 bank_name=bank_name)
            
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
            description="MyMurid Top-up"
        )
        
        if result['success']:
            return result  # Return full result dict with bank account info
        else:
            app.logger.error(f"QR generation failed: {result['error']}")
            # Fallback to mock QR
            return {
                'qr_data': f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890",
                'bank_account': '1234567890',
                'bank_name': 'Test Bank'
            }
            
    except Exception as e:
        app.logger.error(f"QR generation error: {str(e)}")
        # Fallback to mock QR
        return {
            'qr_data': f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890",
            'bank_account': '1234567890',
            'bank_name': 'Test Bank'
        }

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
    
    # Load existing unpaid orders for the cart
    if current_user.role == 'student':
        student = StudentInfo.query.get(current_user.id)
        if student:
            unpaid_orders = Order.query.filter_by(student_id=student.id, payment_status='unpaid').all()
            # Group by menu_item_id
            from collections import defaultdict
            grouped_orders = defaultdict(lambda: {'item': None, 'quantity': 0})
            for order in unpaid_orders:
                menu_id = order.menu_item_id
                if grouped_orders[menu_id]['item'] is None:
                    grouped_orders[menu_id]['item'] = order.item
                grouped_orders[menu_id]['quantity'] += order.quantity
            
            # Convert to list for template
            existing_cart = []
            for menu_id, data in grouped_orders.items():
                existing_cart.append({
                    'id': menu_id,
                    'name': data['item'].name,
                    'price': float(data['item'].price),
                    'quantity': data['quantity']
                })
        else:
            existing_cart = []
    else:
        existing_cart = []
    
    return render_template("order.html", items=items, categories=categories, existing_cart=existing_cart)


@app.route("/admin/menu/new", methods=["GET", "POST"])
@login_required
def create_menu_item():
    """Admin view to create a new menu item"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('order'))

    temp_item = MenuItem(name="", price=Decimal("0.00"), is_available=True)

    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        description = request.form.get('description', '').strip()
        category = sanitize_input(request.form.get('category'))
        price_input = request.form.get('price', '').strip()
        is_available = request.form.get('is_available') == 'on'
        image_file = request.files.get('image')

        if not name:
            flash('Item name is required.', 'error')
            return redirect(url_for('create_menu_item'))

        try:
            price_decimal = Decimal(price_input)
            if price_decimal <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            flash('Please enter a valid price (e.g., 3.50).', 'error')
            return redirect(url_for('create_menu_item'))

        temp_item.name = name
        temp_item.description = sanitize_input(description) if description else None
        temp_item.category = category if category else None
        temp_item.price = price_decimal
        temp_item.is_available = is_available

        new_image_filename = None

        try:
            if image_file and image_file.filename:
                new_image_filename = save_menu_image(image_file)
                temp_item.image_path = new_image_filename

            db.session.add(temp_item)
            db.session.commit()
            flash(f"{temp_item.name} added to the menu.", "success")
            return redirect(url_for('order'))

        except ValueError as ve:
            db.session.rollback()
            if new_image_filename:
                delete_menu_image(new_image_filename)
            flash(str(ve), 'error')
        except Exception as e:
            db.session.rollback()
            if new_image_filename:
                delete_menu_image(new_image_filename)
            app.logger.error(f"Menu item creation error: {e}")
            flash('Failed to create menu item. Please try again.', 'error')

    return render_template(
        'edit_menu_item.html',
        item=temp_item,
        form_action=url_for('create_menu_item'),
        is_new=True
    )


@app.route("/admin/menu/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_menu_item(item_id):
    """Admin view to edit menu item details and image"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('order'))

    item = MenuItem.query.get_or_404(item_id)

    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        description = request.form.get('description', '').strip()
        category = sanitize_input(request.form.get('category'))
        price_input = request.form.get('price', '').strip()
        is_available = request.form.get('is_available') == 'on'
        image_file = request.files.get('image')

        if not name:
            flash('Item name is required.', 'error')
            return redirect(url_for('edit_menu_item', item_id=item_id))

        try:
            price_decimal = Decimal(price_input)
            if price_decimal <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            flash('Please enter a valid price (e.g., 3.50).', 'error')
            return redirect(url_for('edit_menu_item', item_id=item_id))

        old_image = item.image_path
        new_image_filename = None

        try:
            item.name = name
            item.description = sanitize_input(description) if description else None
            item.category = category if category else None
            item.price = price_decimal
            item.is_available = is_available

            if image_file and image_file.filename:
                new_image_filename = save_menu_image(image_file)
                item.image_path = new_image_filename
                if old_image and old_image != new_image_filename:
                    delete_menu_image(old_image)

            db.session.commit()
            flash(f"{item.name} updated successfully.", "success")
            return redirect(url_for('order'))

        except ValueError as ve:
            db.session.rollback()
            if new_image_filename and new_image_filename != old_image:
                delete_menu_image(new_image_filename)
            flash(str(ve), 'error')
        except Exception as e:
            db.session.rollback()
            if new_image_filename and new_image_filename != old_image:
                delete_menu_image(new_image_filename)
            app.logger.error(f"Menu item update error: {e}")
            flash('Failed to update menu item. Please try again.', 'error')

    return render_template(
        'edit_menu_item.html',
        item=item,
        form_action=url_for('edit_menu_item', item_id=item.id),
        is_new=False
    )


@app.route("/admin/menu/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_menu_item(item_id):
    """Admin action to delete or archive a menu item"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('order'))

    item = MenuItem.query.get_or_404(item_id)
    redirect_target = request.referrer or url_for('order')

    try:
        orders_count = Order.query.filter_by(menu_item_id=item.id).count()
        if orders_count > 0:
            # Archive item instead of deleting to preserve order history
            if item.image_path:
                delete_menu_image(item.image_path)
                item.image_path = None
            item.is_available = False
            db.session.commit()
            flash(f"{item.name} archived because it has existing orders.", "info")
        else:
            if item.image_path:
                delete_menu_image(item.image_path)
            db.session.delete(item)
            db.session.commit()
            flash(f"{item.name} deleted from menu.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Menu item deletion error: {e}")
        flash('Failed to delete menu item. Please try again.', 'error')

    return redirect(redirect_target)

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
    
    # Group orders by menu_item_id and sum quantities
    from collections import defaultdict
    grouped_orders = defaultdict(lambda: {'item': None, 'quantity': 0, 'total_price': 0, 'order_ids': []})
    
    for order in unpaid_orders:
        menu_id = order.menu_item_id
        if menu_id not in grouped_orders or grouped_orders[menu_id]['item'] is None:
            grouped_orders[menu_id]['item'] = order.item
        grouped_orders[menu_id]['quantity'] += order.quantity
        grouped_orders[menu_id]['total_price'] += float(order.total_price or 0)
        grouped_orders[menu_id]['order_ids'].append(order.id)
    
    # Convert to list format for template
    grouped_cart_items = []
    for menu_id, data in grouped_orders.items():
        grouped_cart_items.append({
            'menu_item_id': menu_id,
            'item': data['item'],
            'quantity': data['quantity'],
            'total_price': data['total_price'],
            'order_ids': data['order_ids']
        })
    
    total = sum(item['total_price'] for item in grouped_cart_items)
    return render_template("payment.html", cart_items=grouped_cart_items, total=total, user=student)

@app.route("/my-orders")
@login_required
def my_orders():
    """Student view to see all their orders (paid and unpaid)"""
    if current_user.role != 'student':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    student = StudentInfo.query.get(current_user.id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for('student_dashboard'))
    
    # Get all orders for this student, ordered by most recent first
    all_orders = Order.query.filter_by(student_id=student.id).order_by(Order.order_time.desc()).all()
    
    # Group orders by payment status
    paid_orders = [o for o in all_orders if o.payment_status == 'paid']
    unpaid_orders = [o for o in all_orders if o.payment_status == 'unpaid']
    
    # Group paid orders by order_time (same day/time = same order session)
    from collections import defaultdict
    from datetime import datetime
    
    grouped_paid = defaultdict(list)
    for order in paid_orders:
        # Group by date and hour (orders within same hour are considered same session)
        order_key = order.order_time.strftime('%Y-%m-%d %H:00') if order.order_time else 'unknown'
        grouped_paid[order_key].append(order)
    
    # Convert to sorted list of tuples for template
    grouped_paid_sorted = sorted(grouped_paid.items(), key=lambda x: x[0], reverse=True)
    
    return render_template("my_orders.html", 
                         paid_orders=paid_orders,
                         unpaid_orders=unpaid_orders,
                         grouped_paid=grouped_paid_sorted,
                         student=student)

def handle_order_delete(student):
    # Handle multiple order IDs (when grouped items are deleted)
    order_ids = request.form.getlist("delete")
    deleted_count = 0
    
    for order_id in order_ids:
        order = Order.query.get(order_id)
        if order and order.student_id == student.id and order.payment_status == 'unpaid':
            db.session.delete(order)
            deleted_count += 1
    
    if deleted_count > 0:
        db.session.commit()
        flash(f"🗑️ {deleted_count} order(s) deleted.", "success")
    else:
        flash("❌ No orders found or already paid.", "error")
    return redirect(url_for("payment"))

@app.route('/api/update-order-quantity', methods=['POST'])
@login_required
def update_order_quantity():
    """API endpoint to update order quantity for a menu item"""
    if current_user.role != 'student':
        return jsonify({'error': ACCESS_DENIED}), 403
    
    data = request.get_json()
    menu_item_id = data.get('menu_item_id')
    new_quantity = data.get('quantity')
    
    if not menu_item_id or new_quantity is None:
        return jsonify({'error': 'Missing menu_item_id or quantity'}), 400
    
    if new_quantity < 1:
        return jsonify({'error': 'Quantity cannot be less than 1'}), 400
    
    student = StudentInfo.query.get(current_user.id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get all unpaid orders for this menu item
    unpaid_orders = Order.query.filter_by(
        student_id=student.id,
        menu_item_id=menu_item_id,
        payment_status='unpaid'
    ).all()
    
    if not unpaid_orders:
        return jsonify({'error': 'No unpaid orders found for this item'}), 404
    
    # Get the menu item to get the price
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return jsonify({'error': 'Menu item not found'}), 404
    
    try:
        # If we have multiple orders, consolidate them into one
        # Otherwise, just update the quantity of the existing order
        if len(unpaid_orders) > 1:
            # Keep the first order, update its quantity
            main_order = unpaid_orders[0]
            main_order.quantity = new_quantity
            main_order.total_price = float(menu_item.price) * new_quantity
            
            # Delete the rest
            for order in unpaid_orders[1:]:
                db.session.delete(order)
        else:
            # Update the single order
            unpaid_orders[0].quantity = new_quantity
            unpaid_orders[0].total_price = float(menu_item.price) * new_quantity
        
        db.session.commit()
        return jsonify({
            'success': True,
            'quantity': new_quantity,
            'total_price': float(menu_item.price) * new_quantity
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating order quantity: {str(e)}")
        return jsonify({'error': 'Failed to update quantity'}), 500

def validate_payment_conditions(student, unpaid_orders):
    """Validate payment conditions before processing"""
    if not unpaid_orders:
        raise ValueError("No unpaid orders found")

    if student.frozen:
        raise ValueError(ACCOUNT_FROZEN)

    total_amount = sum(Decimal(order.total_price or 0) for order in unpaid_orders)
    total_amount = total_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    total_amount_int = int(total_amount)

    if student.balance < total_amount_int:
        raise ValueError(INSUFFICIENT_BALANCE)

    return total_amount_int

def process_payment_transaction(student, unpaid_orders, total_amount):
    """Process the payment transaction"""
    # Update student balance using integer arithmetic (amount in RM)
    student.balance -= total_amount
    
    # Mark orders as paid
    for order in unpaid_orders:
        order.payment_status = 'paid'
        
    # Create transaction record
    new_tx = Transaction(
        type="Payment",
        amount=Decimal(-total_amount).quantize(Decimal('0.01')),
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

    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Optimize query with join to avoid N+1 queries
    query = db.session.query(Order, StudentInfo, MenuItem)\
        .join(StudentInfo)\
        .join(MenuItem)\
        .filter(Order.payment_status == 'paid')\
        .order_by(Order.order_time.desc())
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                StudentInfo.name.ilike(f'%{search_query}%'),
                StudentInfo.ic_number.ilike(f'%{search_query}%'),
                MenuItem.name.ilike(f'%{search_query}%')
            )
        )
    
    paid_orders = query.all()

    # Group orders by student and menu item name
    from collections import defaultdict
    grouped_by_student = defaultdict(lambda: defaultdict(lambda: {'orders': [], 'total_qty': 0, 'total_price': 0, 'status': 'pending'}))
    
    for order, student, menu_item in paid_orders:
        grouped_by_student[student][menu_item.name]['orders'].append(order)
        grouped_by_student[student][menu_item.name]['total_qty'] += order.quantity
        grouped_by_student[student][menu_item.name]['total_price'] += float(order.total_price or 0)
        # If any order is completed, mark as completed
        if order.status == 'completed':
            grouped_by_student[student][menu_item.name]['status'] = 'completed'
        grouped_by_student[student][menu_item.name]['menu_item'] = menu_item

    # Convert to format expected by template
    grouped_orders = {}
    for student, items in grouped_by_student.items():
        grouped_orders[student] = []
        for item_name, data in items.items():
            grouped_orders[student].append({
                'name': item_name,
                'orders': data['orders'],
                'total_qty': data['total_qty'],
                'total_price': data['total_price'],
                'status': data['status'],
                'menu_item': data['menu_item'],
                'order_ids': [o.id for o in data['orders']]
            })
        # Sort by status (pending first)
        grouped_orders[student].sort(key=lambda x: x['status'] == 'completed')

    return render_template("paid_orders.html", grouped_orders=grouped_orders, search_query=search_query)

@app.route("/mark-done", methods=["POST"])
@login_required
def mark_order_done():
    """Mark order(s) as done - accepts JSON with order_id or order_ids array"""
    if current_user.role not in ['admin', 'staff']:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    order_id = data.get('order_id')
    order_ids = data.get('order_ids', [])
    
    # Support both single order_id and array of order_ids
    if order_id:
        order_ids = [order_id]
    
    if not order_ids:
        return jsonify({'error': 'No order IDs provided'}), 400
    
    updated_count = 0
    try:
        for oid in order_ids:
            order = Order.query.get(oid)
            if order and order.payment_status == 'paid':
                order.status = 'completed'
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            return jsonify({'success': True, 'message': f'{updated_count} order(s) marked as completed'})
        else:
            return jsonify({'error': 'No valid orders found'}), 404
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error marking orders as done: {str(e)}")
        return jsonify({'error': 'Failed to update orders'}), 500

@app.route("/delete-order", methods=["POST"])
@login_required
def delete_order():
    """Delete order(s) - refunds money if order is pending, just deletes if completed"""
    if current_user.role not in ['admin', 'staff']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    order_id = data.get('order_id')
    order_ids = data.get('order_ids', [])
    
    # Support both single order_id and array of order_ids
    if order_id:
        order_ids = [order_id]
    
    if not order_ids:
        return jsonify({'error': 'No order IDs provided'}), 400
    
    deleted_count = 0
    refunded_amount = 0
    
    try:
        for oid in order_ids:
            order = Order.query.get(oid)
            if order and order.payment_status == 'paid':
                student = StudentInfo.query.get(order.student_id)
                if student:
                    # If order is pending, refund the money
                    if order.status != 'completed':
                        refund_amount = float(order.total_price or 0)
                        student.balance += int(refund_amount)
                        refunded_amount += refund_amount
                
                db.session.delete(order)
                deleted_count += 1
        
        if deleted_count > 0:
            db.session.commit()
            message = f'{deleted_count} order(s) deleted'
            if refunded_amount > 0:
                message += f'. RM {refunded_amount:.2f} refunded to student account.'
            return jsonify({'success': True, 'message': message, 'refunded': refunded_amount})
        else:
            return jsonify({'error': 'No valid orders found'}), 404
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting orders: {str(e)}")
        return jsonify({'error': 'Failed to delete orders'}), 500

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
        message = request.form.get('message', '').strip()
        attachments = request.files.getlist('attachments')
        attachments = [file for file in attachments if file and file.filename]
        
        if not message and not attachments:
            flash('Please enter feedback or attach a file.', 'error')
            return redirect(url_for('feedback'))

        if len(attachments) > 5:
            flash('You can upload up to 5 attachments per feedback.', 'error')
            return redirect(url_for('feedback'))

        try:
            # Ensure feedback media table exists (for deployments without migrations)
            FeedbackMedia.__table__.create(db.engine, checkfirst=True)
        except Exception as e:
            app.logger.warning(f"Could not ensure feedback_media table exists: {e}")

        new_feedback = Feedback(message=message, student_id=current_user.id)
        saved_paths = []
        
        try:
            db.session.add(new_feedback)
            db.session.flush()  # assign ID before adding attachments
            
            for file_storage in attachments:
                meta = save_feedback_attachment(file_storage)
                saved_paths.append(meta['file_path'])
                
                media_record = FeedbackMedia(
                    feedback_id=new_feedback.id,
                    file_path=meta['file_path'],
                    media_type=meta['media_type'],
                    original_filename=meta['original_filename'],
                    mimetype=meta['mimetype']
                )
                db.session.add(media_record)
            
            db.session.commit()
            flash('Feedback submitted successfully.', 'success')
        except ValueError as ve:
            db.session.rollback()
            for path in saved_paths:
                delete_static_file(path)
            flash(str(ve), 'error')
        except Exception as e:
            db.session.rollback()
            for path in saved_paths:
                delete_static_file(path)
            app.logger.error(f"Feedback submission error: {e}")
            flash('Failed to submit feedback. Please try again.', 'error')
        
        return redirect(url_for('feedback'))

    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/directory')
@login_required
def directory():
    """Display school directory map - SMK SEKSYEN 3 BANDAR KINRARA"""
    # Single floor plan - show all staff and facilities regardless of floor
    floor_level = request.args.get('floor', 1, type=int)
    
    staff_members = []
    facilities = []
    floors = [1]  # Single floor plan
    
    try:
        # Get all active staff members (single floor plan shows all)
        staff_members = Directory.query.filter_by(is_active=True).order_by(
            Directory.zone_area,
            Directory.display_order,
            Directory.name
        ).all()
        
        # Get all active facilities (single floor plan shows all)
        facilities = Facility.query.filter_by(is_active=True).order_by(
            Facility.facility_type,
            Facility.zone_area,
            Facility.display_order,
            Facility.name
        ).all()
        
        # For single floor plan, just use floor 1
        floors = [1]
        
    except Exception as e:
        # If tables don't exist, create them
        if 'does not exist' in str(e) or 'UndefinedTable' in str(e):
            try:
                # Create the tables directly using the table's create method
                Directory.__table__.create(db.engine, checkfirst=True)
                Facility.__table__.create(db.engine, checkfirst=True)
                flash('Directory tables created. You can now add staff and facilities.', 'success')
                staff_members = []
                facilities = []
                floors = [1]
            except Exception as create_error:
                flash(f'Error creating directory tables: {str(create_error)}', 'error')
                staff_members = []
                facilities = []
                floors = [1]
        else:
            flash(f'Error loading directory: {str(e)}', 'error')
            staff_members = []
            facilities = []
            floors = [1]
    
    if not floors:
        floors = [1]  # Default to floor 1 if no data
    
    # Group staff by zone/area
    staff_by_zone = {}
    zones = []
    for staff in staff_members:
        zone = staff.zone_area or staff.department or 'Unknown'
        if zone not in staff_by_zone:
            staff_by_zone[zone] = []
            zones.append(zone)
        staff_by_zone[zone].append(staff)
    
    # Group facilities by type
    facilities_by_type = {}
    for facility in facilities:
        facility_type = facility.facility_type or 'other'
        if facility_type not in facilities_by_type:
            facilities_by_type[facility_type] = []
        facilities_by_type[facility_type].append(facility)
    
    return render_template('directory.html', 
                         staff_by_zone=staff_by_zone,
                         zones=zones,
                         facilities=facilities,
                         facilities_by_type=facilities_by_type,
                         current_floor=floor_level,
                         available_floors=floors)

@app.route('/delete_feedback/<int:id>', methods=['POST'])
@login_required
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if current_user.role == 'admin' or feedback.student_id == current_user.id:
        if feedback.media:
            for media in feedback.media:
                delete_static_file(media.file_path)
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted.', 'success')
    else:
        flash('You can only delete your own feedback.', 'error')
    return redirect(url_for('feedback'))

def _render_admin_finance_page():
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))

    topup_student = None

    if request.method == 'POST':
        ic = request.form.get('ic', '').strip()
        amount = request.form.get('amount', '').strip()
        
        # Input validation
        if not validate_ic_number(ic):
            flash(INVALID_IC_FORMAT, 'error')
            return redirect(request.url)
        
        if not validate_amount(amount):
            flash(INVALID_AMOUNT, 'error')
            return redirect(request.url)
        
        student = safe_get_student(ic)
        if not student:
            flash(STUDENT_NOT_FOUND, 'error')
            return redirect(request.url)

        if student.frozen:
            flash(ACCOUNT_FROZEN, "error")
            return redirect(request.url)

        try:
            amount_int = int(amount)
            student.balance += amount_int
            topup_student = student
        
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
    
    # Get all pending payments
    pending_payments = Payment.query.filter_by(status='pending').order_by(Payment.created_at.desc()).all()
    completed_payments = Payment.query.filter_by(status='completed').order_by(Payment.completed_at.desc()).limit(20).all()
    
    return render_template(
        'admin_finance.html',
        pending_payments=pending_payments,
        completed_payments=completed_payments,
        topup_student=topup_student
    )


@app.route('/admin/finance', methods=['GET', 'POST'])
@login_required
def admin_finance():
    """Unified admin finance dashboard for top-ups and payment approvals"""
    return _render_admin_finance_page()


@app.route('/topup', methods=['GET', 'POST'])
@login_required
def topup():
    """Backward-compatible route pointing to admin finance dashboard"""
    return _render_admin_finance_page()


@app.route('/admin/payments')
@login_required
def admin_payments():
    """Backward-compatible route that now renders the finance dashboard"""
    return _render_admin_finance_page()

@app.route('/admin/payments/approve/<transaction_id>', methods=['POST'])
@login_required
def approve_payment(transaction_id):
    """Admin route to approve a payment"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    if not payment:
        flash('Payment not found.', 'error')
        return redirect(url_for('admin_finance'))
    
    if payment.status != 'pending':
        flash('Payment already processed.', 'error')
        return redirect(url_for('admin_finance'))
    
    try:
        # Update payment status
        payment.status = 'completed'
        payment.completed_at = datetime.now(timezone(timedelta(hours=8)))
        
        # Add balance to student's account
        child = StudentInfo.query.get(payment.student_id)
        if child:
            child.balance += int(payment.amount)
            
            # Create transaction record
            new_tx = Transaction(
                type="Top-up",
                amount=int(payment.amount),
                description=f"QR Payment top-up for {child.name} (Transaction: {transaction_id[:8]})"
            )
            db.session.add(new_tx)
            db.session.commit()
            
            flash(f'Payment approved! RM{payment.amount} added to {child.name}\'s account.', 'success')
        else:
            flash('Student not found.', 'error')
            db.session.rollback()
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Payment approval error: {str(e)}")
        flash('Error approving payment. Please try again.', 'error')
    
    return redirect(url_for('admin_finance'))

@app.route('/admin/payments/reject/<transaction_id>', methods=['POST'])
@login_required
def reject_payment(transaction_id):
    """Admin route to reject a payment"""
    if current_user.role != 'admin':
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    if not payment:
        flash('Payment not found.', 'error')
        return redirect(url_for('admin_finance'))
    
    if payment.status != 'pending':
        flash('Payment already processed.', 'error')
        return redirect(url_for('admin_finance'))
    
    try:
        payment.status = 'failed'
        db.session.commit()
        flash('Payment rejected.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Payment rejection error: {str(e)}")
        flash('Error rejecting payment. Please try again.', 'error')
    
    return redirect(url_for('admin_finance'))

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
    if current_user.role not in ['admin', 'staff']:
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

@app.route('/food-demand-analytics')
@login_required
def food_demand_analytics():
    """Show food demand analytics with pie chart"""
    if current_user.role not in ['admin', 'staff']:
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    # Get food demand data from paid orders
    food_stats = db.session.query(
        MenuItem.name,
        func.sum(Order.quantity).label('total_quantity')
    ).join(MenuItem).filter(
        Order.payment_status == 'paid'
    ).group_by(MenuItem.name).order_by(
        func.sum(Order.quantity).desc()
    ).all()
    
    # Prepare data for template
    food_data = []
    total_orders = 0
    for item_name, quantity in food_stats:
        total_orders += quantity
        food_data.append({
            'name': item_name,
            'total_quantity': quantity
        })
    
    # Calculate percentages
    for item in food_data:
        item['percentage'] = (item['total_quantity'] / total_orders * 100) if total_orders > 0 else 0
    
    # Prepare chart data
    food_labels = [item['name'] for item in food_data]
    food_values = [item['total_quantity'] for item in food_data]
    
    # Calculate stats
    top_item = food_data[0]['name'] if food_data else None
    avg_orders = total_orders / len(food_data) if food_data else 0
    
    return render_template(
        'food_demand_analytics.html',
        food_data=food_data,
        food_labels=food_labels,
        food_values=food_values,
        total_orders=total_orders,
        top_item=top_item,
        avg_orders=avg_orders
    )

@app.route('/cash-flow-analytics')
@login_required
def cash_flow_analytics():
    """Show cash flow analytics with pie chart"""
    if current_user.role not in ['admin', 'staff']:
        flash(ACCESS_DENIED, "error")
        return redirect(url_for('home'))
    
    # Get revenue data from paid orders
    revenue_stats = db.session.query(
        MenuItem.name,
        MenuItem.price,
        func.sum(Order.quantity).label('total_quantity'),
        func.sum(Order.total_price).label('revenue')
    ).join(MenuItem).filter(
        Order.payment_status == 'paid'
    ).group_by(MenuItem.name, MenuItem.price).order_by(
        func.sum(Order.total_price).desc()
    ).all()
    
    # Prepare data for template
    revenue_data = []
    total_revenue = 0
    total_transactions = 0
    for item_name, price, quantity, revenue in revenue_stats:
        total_revenue += float(revenue)
        total_transactions += quantity
        revenue_data.append({
            'name': item_name,
            'price': float(price),
            'total_quantity': quantity,
            'revenue': float(revenue)
        })
    
    # Calculate percentages
    for item in revenue_data:
        item['percentage'] = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
    
    # Prepare chart data
    revenue_labels = [item['name'] for item in revenue_data]
    revenue_values = [item['revenue'] for item in revenue_data]
    
    # Calculate stats
    top_earner = revenue_data[0]['name'] if revenue_data else None
    avg_revenue = total_revenue / len(revenue_data) if revenue_data else 0
    
    return render_template(
        'cash_flow_analytics.html',
        revenue_data=revenue_data,
        revenue_labels=revenue_labels,
        revenue_values=revenue_values,
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        top_earner=top_earner,
        avg_revenue=avg_revenue
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
