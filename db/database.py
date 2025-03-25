# db/database.py
import os
from config import DATABASE_PATH
from db.connection import DatabaseConnection, get_connection

def init_database():
    """Initialize the database with required tables"""
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        # Users table for authentication
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            email TEXT,
            is_verified INTEGER DEFAULT 0,
            is_staff INTEGER DEFAULT 0,
            verification_code TEXT,
            code_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Conversations table for tracking interactions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # FAQs table for knowledge base
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            added_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Course information table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE,
            title TEXT,
            description TEXT,
            instructor TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    print("Database initialized successfully")

# Function to save a user to the database
def save_user(user_id, username, first_name):
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ''', (user_id, username, first_name))

# Function to save a conversation
def save_conversation(user_id, message, response):
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO conversations (user_id, message, response)
        VALUES (?, ?, ?)
        ''', (user_id, message, response))

def is_staff(user_id):
    """Check if a user is staff"""
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_staff FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
            
        return bool(result['is_staff'])

def make_staff(user_id):
    """Make a user a staff member"""
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_staff = 1 WHERE user_id = ?', (user_id,))
        return cursor.rowcount > 0