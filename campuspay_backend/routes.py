from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from .models import db, User, Transaction
from . import bcrypt
import cv2
import face_recognition
import numpy as np
import stripe
from flask import current_app
from datetime import datetime

app_routes = Blueprint('app_routes', __name__)

stripe.api_key = ""
PUBLISHABLE_KEY = ""

@app_routes.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.index'))

    user = User.query.get(user_id)
    amount = float(request.form.get('amount'))

    if amount <= 0:
        return redirect(url_for('app_routes.dashboard'))

    try:
        # Create a Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Add Funds to CampusPay Account',
                        },
                        'unit_amount': int(amount * 100),  # Stripe expects the amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('app_routes.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('app_routes.dashboard', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(f"Error creating Stripe Checkout session: {e}")
        return redirect(url_for('app_routes.dashboard'))
    

@app_routes.route('/payment_success')
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('app_routes.dashboard'))

    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        amount = checkout_session.amount_total / 100  # Convert cents to dollars

        # Update the user's balance
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        user.balance += amount

        # Record the transaction
        transaction = Transaction(
            user_id=user.id,
            timestamp=datetime.utcnow(),
            amount=amount,
            description="Funds added via Stripe"
        )
        db.session.add(transaction)
        db.session.commit()

        return render_template('success.html', message="Payment successful! Funds have been added to your account.")
    except Exception as e:
        print(f"Error handling payment success: {e}")
        return redirect(url_for('app_routes.dashboard'))
    

@app_routes.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        from_srn = request.form.get('from_srn')
        to_srn = request.form.get('to_srn')
        amount = float(request.form.get('amount'))

        # Check if the "from" user exists
        from_user = User.query.filter_by(srn=from_srn).first()
        if not from_user:
            return render_template('index.html', error="Sender SRN does not exist.")

        # Check if the "to" user exists
        to_user = User.query.filter_by(srn=to_srn).first()
        if not to_user:
            return render_template('index.html', error="Recipient SRN does not exist.")

        # Store transaction details in the session
        session['from_user_id'] = from_user.id
        session['to_user_id'] = to_user.id
        session['amount'] = amount

        # Redirect to facial authentication
        return redirect(url_for('app_routes.facial_authentication'))

    return render_template('index.html')

@app_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        sex = request.form.get('sex')
        srn = request.form.get('srn')

        # Check if SRN is already registered
        if User.query.filter_by(srn=srn).first():
            return render_template('register.html', error="SRN already registered")

        # Create a new user without a password
        new_user = User(
            name=name,
            dob=datetime.strptime(dob, '%Y-%m-%d'),
            sex=sex,
            srn=srn
        )

        db.session.add(new_user)
        db.session.commit()

        # Redirect to facial scan page
        return redirect(url_for('app_routes.register_facial_scan', user_id=new_user.id))

    return render_template('register.html')


@app_routes.route('/facial_authentication', methods=['GET', 'POST'])
def facial_authentication():
    from_user_id = session.get('from_user_id')
    to_user_id = session.get('to_user_id')
    amount = session.get('amount')

    if not from_user_id or not to_user_id or not amount:
        return redirect(url_for('app_routes.index'))

    from_user = User.query.get(from_user_id)
    to_user = User.query.get(to_user_id)

    if request.method == 'POST':
        # Deduct the amount from the sender's balance
        if from_user.balance < amount:
            return jsonify({"error": "Insufficient balance. Please add funds to your account."}), 400

        from_user.balance -= amount
        to_user.balance += amount

        # Record the transaction for the sender
        sender_transaction = Transaction(
            user_id=from_user.id,
            timestamp=datetime.utcnow(),
            amount=-amount,
            description=f"Transfer to {to_user.srn}"
        )
        db.session.add(sender_transaction)

        # Record the transaction for the recipient
        recipient_transaction = Transaction(
            user_id=to_user.id,
            timestamp=datetime.utcnow(),
            amount=amount,
            description=f"Received from {from_user.srn}"
        )
        db.session.add(recipient_transaction)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"success": "Transaction successful!"}), 200

    return render_template('facial_authentication.html', user=from_user)

@app_routes.route('/register_facial_scan/<int:user_id>', methods=['GET', 'POST'])
def register_facial_scan(user_id):
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('app_routes.register'))

    if request.method == 'POST':
        # Get the uploaded image from the form
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({"error": "No image uploaded"}), 400

        # Read the image and process it
        image = face_recognition.load_image_file(image_file)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return jsonify({"error": "No face detected. Please try again."}), 400

        # Save the facial encoding to the database
        user.facial_encoding = face_encodings[0]
        db.session.commit()
        return jsonify({"success": "Facial scan completed successfully!"}), 200

    return render_template('register_facial_scan.html', user=user)

    
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        srn = request.form.get('srn')

        # Check if the user exists
        user = User.query.filter_by(srn=srn).first()
        if not user:
            return render_template('login.html', error="Invalid SRN")

        # Store the user ID in the session for facial authentication
        session['user_id'] = user.id
        return redirect(url_for('app_routes.login_facial_authentication'))

    return render_template('login.html')


@app_routes.route('/login_facial_authentication', methods=['GET', 'POST'])
def login_facial_authentication():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        # Get the uploaded image from the form
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({"error": "No image uploaded"}), 400

        try:
            # Read the image and process it
            image = face_recognition.load_image_file(image_file)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                return jsonify({"error": "No face detected. Please try again."}), 400

            # Compare facial encoding with the stored encoding
            matches = face_recognition.compare_faces([user.facial_encoding], face_encodings[0])
            if not any(matches):
                return jsonify({"error": "Face does not match. Please try again."}), 400

            # If the face matches, log the user in
            return jsonify({"success": "Authentication successful!"}), 200

        except Exception as e:
            print(f"Error processing image: {e}")
            return jsonify({"error": "An error occurred while processing the image. Please try again."}), 500

    return render_template('login_facial_authentication.html', user=user)

@app_routes.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.index'))

    user = User.query.get(user_id)
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    return render_template('dashboard.html', user=user, transactions=transactions)

@app_routes.route('/add_funds', methods=['POST'])
def add_funds():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.index'))

    user = User.query.get(user_id)
    amount = float(request.form.get('amount'))

    if amount <= 0:
        return redirect(url_for('app_routes.dashboard'))

    # Update the user's balance
    user.balance += amount

    # Record the transaction
    transaction = Transaction(
        user_id=user.id,
        timestamp=datetime.utcnow(),
        amount=amount,
        description="Funds added to account"
    )
    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('app_routes.dashboard'))

@app_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('app_routes.index'))