# tests/integration/test_bot_commands.py
import pytest
from unittest.mock import Mock, patch
from telegram import Update, Chat, Message, User
from db.connection import DatabaseConnection 
from bot.handlers import start_command, help_command, course_command
from db.database import save_user
from knowledge.manager import load_courses_to_db

class TestBotCommands:
    def setup_method(self):
        """Setup mock objects for Telegram"""
        self.user = User(id=123, first_name='Test', is_bot=False, username='testuser')
        self.chat = Chat(id=123, type='private')
        self.message = Message(
            message_id=1, 
            date=None, 
            chat=self.chat,
            from_user=self.user,
            text=""
        )
        self.update = Update(update_id=1, message=self.message)
        self.context = Mock()
        self.context.args = []
    
    def test_course_command_integration(self, test_db):
        """Test course_command with actual database interaction"""
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
        self.message.text = "/course IS621"
        
        # Create a mock for reply_text to capture response
        self.message.reply_text = Mock()
        
        # Execute command
        course_command(self.update, self.context)
        
        # Verify response
        args, kwargs = self.message.reply_text.call_args
        response = args[0]
        
        # Check for expected content in response
        assert "IS621" in response
        assert "Agile and DevSecOps" in response