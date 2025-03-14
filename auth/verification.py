import random
import string
import time
import sqlite3
from config import VERIFICATION_TIMEOUT
from db.database import get_connection

#verification
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_PASSWORD

def send_verification_email(email, code):
    """Send verification email with code"""
    subject = "Your SMU Bot Verification Code"
    body = f"Your verification code is: {code}\n\nThis code will expire in 10 minutes."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def generate_verification_code(length=6):
    """Generate a random verification code"""
    # Use digits only for a simple code
    return ''.join(random.choices(string.digits, k=length))

def start_verification(user_id, email):
    """Start the verification process for a user"""
    # Check if the email is from SMU
    if not email.endswith('@smu.edu.sg'):
        return False, "Please use your SMU email address (@smu.edu.sg)"
    
    # Generate a verification code
    code = generate_verification_code()
    expires_at = int(time.time()) + VERIFICATION_TIMEOUT
    
    # Store the code in the database
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE users 
        SET email = ?, verification_code = ?, code_expires_at = ?
        WHERE user_id = ?
        ''', (email, code, expires_at, user_id))
        
        conn.commit()
        
        # In a real application, you would send an email here
        # For this example, we'll pretend the email is sent
        print(f"Verification code for {email}: {code}")
        
        return True, "Verification code sent to your email. Please check your inbox."
    except Exception as e:
        return False, f"Error starting verification: {str(e)}"
    finally:
        conn.close()

def verify_code(user_id, code):
    """Verify a user's verification code"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get the user's verification info
        cursor.execute('''
        SELECT verification_code, code_expires_at, email
        FROM users 
        WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return False, "User not found"
        
        stored_code = result['verification_code']
        expires_at = result['code_expires_at']
        email = result['email']
        
        # Check if code is expired
        if int(time.time()) > expires_at:
            return False, "Verification code has expired. Please request a new one."
        
        # Check if code matches
        if code != stored_code:
            return False, "Invalid verification code. Please try again."
        
        # Mark user as verified
        cursor.execute('''
        UPDATE users 
        SET is_verified = 1, verification_code = NULL, code_expires_at = NULL
        WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        
        return True, f"Email {email} verified successfully!"
    except Exception as e:
        return False, f"Error verifying code: {str(e)}"
    finally:
        conn.close()

def is_user_verified(user_id):
    """Check if a user is verified"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
            
        return bool(result['is_verified'])
    except Exception:
        return False
    finally:
        conn.close()