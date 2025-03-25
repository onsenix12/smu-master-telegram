from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from db.connection import DatabaseConnection
from config import DASHBOARD_USERNAME, DASHBOARD_PASSWORD, DASHBOARD_SECRET_KEY

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Set secret key for session
app.secret_key = DASHBOARD_SECRET_KEY  # Use value from config

@app.route('/')
def home():
    """Home page - redirects to dashboard if logged in, otherwise to login"""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Get statistics from database
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        # Get verified user count
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_verified = 1')
        verified_count = cursor.fetchone()['count']
        
        # Get conversation count
        cursor.execute('SELECT COUNT(*) as count FROM conversations')
        conversation_count = cursor.fetchone()['count']
        
        # Get recent conversations
        cursor.execute('''
        SELECT c.message, c.response, c.timestamp, u.first_name
        FROM conversations c
        JOIN users u ON c.user_id = u.user_id
        ORDER BY c.timestamp DESC
        LIMIT 10
        ''')
        recent_conversations = cursor.fetchall()
    
    return render_template('dashboard.html',
                          user_count=user_count,
                          verified_count=verified_count,
                          conversation_count=conversation_count,
                          recent_conversations=recent_conversations)

@app.route('/users')
def users():
    """Users list page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT user_id, username, first_name, email, is_verified, is_staff
        FROM users
        ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
    
    return render_template('users.html', users=users)

@app.route('/faqs')
def faqs():
    """FAQs management page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT f.id, f.question, f.answer, f.created_at, u.first_name
        FROM faqs f
        LEFT JOIN users u ON f.added_by = u.user_id
        ORDER BY f.created_at DESC
        ''')
        
        faqs = cursor.fetchall()
    
    return render_template('faqs.html', faqs=faqs)

def start_dashboard():
    """Start the Flask dashboard"""
    app.run(host='0.0.0.0', port=5002, debug=False)