import sqlite3
import hashlib
import os

# Store DB in the root folder, one level up from services/
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.db')

def init_db():
    """Initialize the user database table."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] Failed to initialize file-based DB: {e}. Switching to in-memory DB.")
        global DB_FILE
        DB_FILE = ':memory:'
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

def hash_password(password):
    """Hash a password for storing. Format: salt$hash"""
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
    return f"{salt}${key}"

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    try:
        salt, key = stored_password.split('$')
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
        return new_key == key
    except ValueError:
        return False

def register_user(username, password, full_name, location=""):
    """Register a new user. Returns True if successful, False if username exists."""
    try:
        pwd_hash = hash_password(password)
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('INSERT INTO users (username, password, full_name, location) VALUES (?, ?, ?, ?)',
                         (username, pwd_hash, full_name, location))
        return True
    except sqlite3.IntegrityError:
        return False  # Username exists

def login_user(username, password):
    """Verify login and return user info if valid."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT id, username, password, full_name, location FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
    
    if user and verify_password(user[2], password):
        return {
            'id': user[0],
            'username': user[1],
            'full_name': user[3],
            'location': user[4]
        }
    return None

# Initialize DB on import
if not os.path.exists(DB_FILE):
    init_db()
else:
    # Ensure table exists even if file exists
    init_db()
