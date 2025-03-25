import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.verification import send_verification_email, start_verification


def test_send_verification_email_returns_error_message():
    """
    Test that send_verification_email properly returns an error message
    when the email sending fails, instead of just printing it.
    """
    # Mock the smtplib to simulate an error
    with patch('smtplib.SMTP') as mock_smtp:
        # Set up the mock to raise an exception when login is called
        mock_instance = MagicMock()
        mock_smtp.return_value = mock_instance
        mock_instance.login.side_effect = Exception("Authentication failed")
        
        # Call the function
        result, error_message = send_verification_email("test@smu.edu.sg", "123456")
        
        # Verify it returns False and an error message string
        assert result is False
        assert isinstance(error_message, str)
        assert "Authentication failed" in error_message

def test_verify_code_handles_database_error():
    """
    Test that verify_code properly handles database connection errors
    and returns appropriate error messages.
    """
    user_id = "12345"
    code = "123456"
    
  