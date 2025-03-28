import unittest
import tempfile
import os
from unittest.mock import Mock, patch

from telegram import Update, User, Chat
from telegram.ext import CallbackContext

from db.database import save_user, init_database
from db.connection import DatabaseConnection
from bot.handlers import course_command, help_command, faq_command
from knowledge.manager import load_courses_to_db
from config import DATABASE_PATH

class TestBotCommands(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.original_db_path = DATABASE_PATH

        # Mock user and chat objects
        self.user = User(id=123, first_name='Test', is_bot=False, username='testuser')
        self.chat = Chat(id=123, type=Chat.PRIVATE)

        # Create a mock message
        self.message = Mock()
        self.message.chat = self.chat
        self.message.from_user = self.user
        self.message.reply_text = Mock()

        # Create a mock update object
        self.update = Mock(spec=Update)
        self.update.effective_user = self.user
        self.update.message = self.message

        # Create a mock context object
        self.context = Mock(spec=CallbackContext)
        self.context.args = []

    def tearDown(self):
        """Clean up after each test"""
        # Close and remove the temporary database
        if hasattr(self, 'temp_db'):
            os.unlink(self.temp_db.name)

    @patch('config.DATABASE_PATH')
    def test_help_command(self, mock_db_path):
        """Test the help_command function"""
        # Set the temporary database path
        mock_db_path.return_value = self.temp_db.name

        # Initialize the test database
        init_database()

        # Mark user as verified for testing
        save_user(str(self.user.id), self.user.username, self.user.first_name)
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET is_verified = 1 WHERE user_id = ?',
                (str(self.user.id),)
            )

        # Call the help_command function
        help_command(self.update, self.context)

        # Check that reply_text was called with the expected help message
        self.message.reply_text.assert_called_once()
        self.assertIn("Available commands", self.message.reply_text.call_args[0][0])

    @patch('config.DATABASE_PATH')
    def test_course_command_no_args(self, mock_db_path):
        """Test course_command with no arguments"""
        # Set the temporary database path
        mock_db_path.return_value = self.temp_db.name

        # Initialize the test database
        init_database()

        # Mark user as verified for testing
        save_user(str(self.user.id), self.user.username, self.user.first_name)
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET is_verified = 1 WHERE user_id = ?',
                (str(self.user.id),)
            )

        # Call the course_command function with no args
        course_command(self.update, self.context)

        # Check that reply_text was called with a message about providing a course code
        self.message.reply_text.assert_called_once()
        self.assertIn("Please provide a course code", self.message.reply_text.call_args[0][0])

    @patch('config.DATABASE_PATH')
    def test_course_command_integration(self, mock_db_path):
        """Test course_command with actual database interaction"""
        # Set the temporary database path
        mock_db_path.return_value = self.temp_db.name

        # Initialize the test database before loading courses
        init_database()

        # Setup test database with course data
        load_courses_to_db()
        save_user(str(self.user.id), self.user.username, self.user.first_name)

        # Mark user as verified for testing
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET is_verified = 1 WHERE user_id = ?',
                (str(self.user.id),)
            )

        # Set up command with arguments
        self.context.args = ['IS621']

        # Call the course command
        course_command(self.update, self.context)

        # Check that reply_text was called with course info
        self.message.reply_text.assert_called_once()
        course_info = self.message.reply_text.call_args[0][0]
        self.assertIn("IS621", course_info)
        self.assertIn("Agile and DevSecOps", course_info)

    @patch('config.DATABASE_PATH')
    def test_faq_command(self, mock_db_path):
        """Test the faq_command function"""
        # Set the temporary database path
        mock_db_path.return_value = self.temp_db.name

        # Initialize the test database
        init_database()

        # Mark user as verified for testing
        save_user(str(self.user.id), self.user.username, self.user.first_name)
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET is_verified = 1 WHERE user_id = ?',
                (str(self.user.id),)
            )

        # Mock get_all_faqs to return sample FAQs
        with patch('bot.handlers.get_all_faqs', return_value=[
            {'id': 1, 'question': 'Test Question 1', 'answer': 'Test Answer 1'},
            {'id': 2, 'question': 'Test Question 2', 'answer': 'Test Answer 2'}
        ]):
            # Call the faq_command function
            faq_command(self.update, self.context)

            # Check that reply_text was called with the expected FAQ list
            self.message.reply_text.assert_called_once()
            faq_list = self.message.reply_text.call_args[0][0]
            self.assertIn("Available FAQs", faq_list)
            self.assertIn("Test Question 1", faq_list)
            self.assertIn("Test Question 2", faq_list)

if __name__ == '__main__':
    unittest.main()