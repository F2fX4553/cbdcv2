import os
import ecdsa
import hashlib
import zmq
import datetime
import base64
import qrcode
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from decimal import Decimal, ROUND_HALF_UP
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from Crypto.Hash import RIPEMD160

# Import the core functionality
from core.gorgumu._db import session, SimpleStatement
from core.gorgumu._trx import create_transaction
from core.gorgumu._loan import request_loan
from core.finance import Gorgumu_Price

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GRM_secret_key_12345'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Generate wallet address from public key
def generate_address(public_key_data):
    hashing = hashlib.sha256(str(public_key_data).encode()).hexdigest()
    hashing_to_bytes = hashing.encode()
    Ripmd = RIPEMD160.new(hashing_to_bytes)
    last_hash = Ripmd.hexdigest()
    Ripmd_to_bytes = last_hash.encode()
    enc = base58.b58encode(Ripmd_to_bytes)
    dec = enc.decode()
    return dec

# Handle user loading for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Route for the home page
@app.route('/')
def index():
    if 'wallet_address' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get credentials from form
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if credentials exist in session
        # In a real implementation, you would check against the database
        if username and password:
            # Here we would verify the credentials
            # For now, we'll just set a mock wallet address in the session
            session['wallet_address'] = "GRM1234567890"
            user = User(session['wallet_address'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

# Route for user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get registration data from form
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Generate a new key pair for the wallet
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        
        # Generate wallet address
        address = generate_address(public_key.to_string())
        
        # Store user data (in a real implementation, store in database)
        # For demonstration, we'll just store in the session
        session['wallet_address'] = address
        
        # Create a user object and login
        user = User(address)
        login_user(user)
        
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

# Dashboard route (requires login)
@app.route('/dashboard')
@login_required
def dashboard():
    # Get wallet address from session
    address = session.get('wallet_address')
    
    # Query balance from database
    query = SimpleStatement(f"SELECT balance FROM wallet WHERE address = '{address}';")
    rows = session.execute(query)
    
    balance_grm = 0
    for row in rows:
        balance_grm = row.balance
    
    # Calculate USD balance
    balance_usd = Decimal(balance_grm) * Decimal(Gorgumu_Price)
    balance_usd = balance_usd.quantize(Decimal('1E-4'), rounding=ROUND_HALF_UP)
    
    # Generate QR code for wallet address
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 to display in HTML
    buffered = BytesIO()
    img.save(buffered)
    qr_img_data = base64.b64encode(buffered.getvalue()).decode()
    
    # Get transactions for history
    transactions = []
    query = SimpleStatement(f"SELECT * FROM Transaction WHERE sender = '{address}' OR receiver = '{address}' LIMIT 10;")
    rows = session.execute(query)
    for row in rows:
        transactions.append({
            'hash': row.hash,
            'sender': row.sender,
            'receiver': row.receiver,
            'amount': row.amount,
            'datetime': row.datetime
        })
    
    # Get expire date
    query = SimpleStatement(f"SELECT expire_date FROM wallet WHERE address = '{address}';")
    rows = session.execute(query)
    expire_date = None
    for row in rows:
        expire_date = row.expire_date
    
    return render_template('dashboard.html', 
                           balance_grm=balance_grm, 
                           balance_usd=balance_usd,
                           address=address,
                           qr_img_data=qr_img_data,
                           transactions=transactions,
                           expire_date=expire_date)

# Send transaction route
@app.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST':
        receiver = request.form.get('receiver')
        amount = request.form.get('amount')
        
        # Validate input
        if not receiver or not amount:
            flash('Receiver address and amount are required', 'error')
            return redirect(url_for('send'))
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number', 'error')
            return redirect(url_for('send'))
        
        # Get sender address from session
        sender = session.get('wallet_address')
        
        # Call the create_transaction function from the original code
        result = create_transaction(sender, receiver, amount)
        
        if result:
            flash('Transaction successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Transaction failed', 'error')
    
    return render_template('send.html')

# Receive transaction route (display wallet address and QR code)
@app.route('/receive')
@login_required
def receive():
    # Get wallet address from session
    address = session.get('wallet_address')
    
    # Generate QR code for wallet address
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 to display in HTML
    buffered = BytesIO()
    img.save(buffered)
    qr_img_data = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('receive.html', address=address, qr_img_data=qr_img_data)

# Loan route
@app.route('/loan', methods=['GET', 'POST'])
@login_required
def loan():
    if request.method == 'POST':
        amount = request.form.get('amount')
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number', 'error')
            return redirect(url_for('loan'))
        
        # Get wallet address from session
        address = session.get('wallet_address')
        
        # Call the request_loan function from the original code
        result = request_loan(address, amount)
        
        if result:
            flash('Loan request successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Loan request failed', 'error')
    
    return render_template('loan.html')

# Deposit route
@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount')
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number', 'error')
            return redirect(url_for('deposit'))
        
        # Get wallet address from session
        address = session.get('wallet_address')
        
        # Call the deposit function
        # Implement deposit logic here
        
        flash('Deposit successful', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('deposit.html')

# Transactions history route
@app.route('/transactions')
@login_required
def transactions():
    # Get wallet address from session
    address = session.get('wallet_address')
    
    # Get transactions for history
    transactions = []
    query = SimpleStatement(f"SELECT * FROM Transaction WHERE sender = '{address}' OR receiver = '{address}';")
    rows = session.execute(query)
    for row in rows:
        transactions.append({
            'hash': row.hash,
            'sender': row.sender,
            'receiver': row.receiver,
            'amount': row.amount,
            'datetime': row.datetime
        })
    
    return render_template('transactions.html', transactions=transactions)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 