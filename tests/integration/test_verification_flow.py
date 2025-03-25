import pytest
from unittest.mock import patch

from auth.verification import start_verification, verify_code
from db.connection import DatabaseConnection

class TestVerificationFlow:
    @patch('auth.verification.send_verification_email')
    def test_verification_start(self, mock_send_email, test_db):
        """Test starting the verification process"""
        # Setup
        user_id = "12345"
        email = "test@smu.edu.sg"
        test_code = "123456"
        
        # Mock email sending to succeed
        mock_send_email.return_value = (True, None)
        
        # Insert test user
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, "testuser", "Test User"))
        
        # Test verification start
        with patch('auth.verification.generate_verification_code', return_value=test_code):
            success, message = start_verification(user_id, email)
        
        # Assertions
        assert success is True
        assert "Verification code sent" in message
        
        # Verify database was updated
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            assert user is not None
            assert user['verification_code'] == test_code