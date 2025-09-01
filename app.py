from flask import Flask, render_template, request, redirect, jsonify, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, StudentInfo, MenuItem, Order, Vote, Feedback
import os, json
from barcode import Code128
from barcode.writer import ImageWriter
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from transactions import Transaction
from sqlalchemy import func
from datetime import timedelta
from config import config

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[config_name])

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def make_session_non_permanent():
    session.permanent = False

@login_manager.user_loader
def load_user(user_id):
    return StudentInfo.query.get(int(user_id))

@app.context_processor
def inject_user():
    return {'user': current_user}

def inject_request():
    return {"request": request}

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ic = request.form.get('ic')
        pin = request.form.get('pin')
        password = request.form.get('password')
        user = StudentInfo.query.filter_by(ic_number=ic).first()

        if user and user.pin == pin:
            if user.role == 'admin' and user.password != password:
                flash('Invalid password for admin.', 'error')
                return redirect(url_for('login'))
            login_user(user, remember=False)
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid IC or PIN.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('login'))

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
    if current_user.role == 'admin':
        return render_template('admin.html', user=current_user)
    else:
        return redirect(url_for('home'))

@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    items = MenuItem.query.all()
    categories = list({item.category for item in items if item.category})
    if request.method == "POST":
        try:
            cart = request.form.get("cart_items")
            cart_items = json.loads(cart)
            if not cart_items:
                flash("Cart is empty or invalid!", "error")
                return redirect(url_for("order"))
        except Exception:
            flash("❌ Invalid cart data.", "error")
            return redirect(url_for("order"))

        student = StudentInfo.query.get(current_user.id)
        if not student:
            flash("❌ Student not found.", "error")
            return redirect(url_for("order"))

        for entry in cart_items:
            item = MenuItem.query.get(entry["id"])
            if not item:
                continue
            total_price = item.price * entry["quantity"]
            order = Order(student_id=student.id, menu_item_id=item.id, quantity=entry["quantity"], total_price=total_price, payment_status='unpaid')
            db.session.add(order)

        db.session.commit()
        flash("✅ Order submitted! Proceed to payment.", "success")
        return redirect(url_for("payment"))

    return render_template("order.html", items=items, categories=categories)

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

def handle_order_payment(student):
    unpaid_orders = Order.query.filter_by(student_id=student.id, payment_status='unpaid').all()
    total_amount = sum(order.item.price * order.quantity for order in unpaid_orders)

    if student.frozen:
        flash("🧊 Account is frozen. Please contact an admin.", "error")
        return redirect(url_for("payment"))

    if student.balance < total_amount:
        flash("❌ Not enough balance.", "error")
        return redirect(url_for("payment"))

    student.balance -= total_amount
    for order in unpaid_orders:
        order.payment_status = 'paid'
        
    new_tx = Transaction(
        type="Payment",
        amount=-total_amount,
        description=f"Payment for {len(unpaid_orders)} items"
        )
    db.session.add(new_tx)

    db.session.commit()
    flash("✅ Payment successful!", "success")
    return redirect(url_for("student_dashboard"))


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
    if current_user.role != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        order_id = request.form.get("order_id")
        order = Order.query.get(order_id)
        if order:
            order.done = True
            db.session.commit()
            flash("✅ Order marked as done.", "success")
        return redirect(url_for("paid_orders"))

    paid_orders = Order.query.filter_by(payment_status='paid').order_by(Order.order_time.desc()).all()

    grouped = {}
    for order in paid_orders:
        student = StudentInfo.query.get(order.student_id)
        if student not in grouped:
            grouped[student] = []
        grouped[student].append(order)

    # Optional: sort orders by `status`
    for orders in grouped.values():
        orders.sort(key=lambda x: x.status == 'completed' or False)

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
    if current_user.role != "admin":
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
        flash("Unauthorized access.", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        ic = request.form.get('ic')
        amount = request.form.get('amount')
        student = StudentInfo.query.filter_by(ic_number=ic).first()

        if student.frozen:
            flash("🧊 Account is frozen. Please contact an admin.", "error")
            return redirect(url_for("topup"))

        if student:
            try:
                student.balance += int(amount)
                new_tx = Transaction(
                    type="Top-up",
                    amount=amount,
                    description=f"Student top-up"
                )
                db.session.add(new_tx)
                db.session.commit()
                flash(f"Successfully topped up RM{amount} for {student.name}.", "success")
            except Exception:
                db.session.rollback()
                flash("Error processing top-up. Try again.", "error")
        else:
            flash("Student not found.", "error")

    return render_template("topup.html")

@app.route('/freeze_card', methods=['POST'])
@login_required
def freeze_card():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    ic = request.form['ic']
    student = StudentInfo.query.filter_by(ic_number=ic).first()
    if student:
        student.frozen = True
        db.session.commit()
        flash(f"{student.name}'s card has been frozen.")
    else:
        flash("Student not found.")
    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_card_status', methods=['POST'])
@login_required
def toggle_card_status():
    ic = request.form.get('ic')
    action = request.form.get('action')

    student = StudentInfo.query.filter_by(ic_number=ic).first()
    if not student:
        flash("Student not found.", "danger")
    else:
        if action == 'freeze':
            student.frozen = True
            flash(f"{student.name}'s card has been frozen.", "warning")
        elif action == 'unfreeze':
            student.frozen = False
            flash(f"{student.name}'s card has been unfrozen.", "success")
        db.session.commit()

    return redirect(url_for('student_balances'))

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
