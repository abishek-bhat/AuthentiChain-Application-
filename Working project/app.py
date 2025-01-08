from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
import os
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create database
def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name TEXT,
            details TEXT,
            barcode_hash TEXT
        )
    ''')
    # Add sample users
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role) VALUES 
        ('manu', 'manu123', 'manufacturer'),
        ('user', 'user123', 'user')
    ''')
    conn.commit()
    conn.close()

# Hash a file for barcode verification
def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        session['username'] = user[1]
        session['role'] = user[3]
        if user[3] == 'manufacturer':
            return redirect(url_for('manufacturer'))
        elif user[3] == 'user':
            return redirect(url_for('user'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('home'))

@app.route('/manufacturer', methods=['GET', 'POST'])
def manufacturer():
    if 'role' in session and session['role'] == 'manufacturer':
        if request.method == 'POST':
            product_name = request.form['product_name']
            details = request.form['details']
            barcode = request.files['barcode']
            if barcode:
                barcode_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(barcode.filename))
                barcode.save(barcode_path)
                barcode_hash = hash_file(barcode_path)

                # Save product details to DB
                conn = sqlite3.connect('app.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO products (product_name, details, barcode_hash) VALUES (?, ?, ?)',
                               (product_name, details, barcode_hash))
                conn.commit()
                conn.close()
                flash('Product added successfully')
                return redirect(url_for('manufacturer'))
        return render_template('manufacturer.html')
    else:
        return redirect(url_for('home'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'role' in session and session['role'] == 'user':
        if request.method == 'POST':
            barcode = request.files['barcode']
            if barcode:
                barcode_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(barcode.filename))
                barcode.save(barcode_path)
                barcode_hash = hash_file(barcode_path)

                # Verify barcode
                conn = sqlite3.connect('app.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE barcode_hash = ?', (barcode_hash,))
                product = cursor.fetchone()
                conn.close()
                if product:
                    flash(f'Product Verified: {product[1]}, Details: {product[2]}')
                else:
                    flash('Counterfeit Product Detected!')
                return redirect(url_for('user'))
        return render_template('user.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    init_db()
    app.run(debug=True)
