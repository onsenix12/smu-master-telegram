#bot
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TELEGRAM_TOKEN
from db.database import init_database
from bot.handlers import (
    start_command, help_command, handle_message, 
    verify_command, code_command, course_command, faq_command, reset_verification_command
)
from knowledge.manager import load_courses_to_db
from bot.staff_commands import add_faq_command, make_staff_command

#dashboard
import threading
from dashboard.app import start_dashboard


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Initialize the database
    init_database()

    # Load courses into database
    load_courses_to_db()
    
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("verify", verify_command))
    dispatcher.add_handler(CommandHandler("code", code_command))
    dispatcher.add_handler(CommandHandler("course", course_command))
    dispatcher.add_handler(CommandHandler("add_faq", add_faq_command))
    dispatcher.add_handler(CommandHandler("make_staff", make_staff_command))
    dispatcher.add_handler(CommandHandler("faq", faq_command))
    dispatcher.add_handler(CommandHandler("reset_verification", reset_verification_command))
    
    # Regular message handler
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, handle_message
    ))
    
    # Start the Bot
    updater.start_polling()
    logger.info("Bot started")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == "__main__":
    main()

def main():
    # Initialize the database
    init_database()
    
    # Load courses into database
    load_courses_to_db()
    
    # Start the dashboard in a separate thread
    dashboard_thread = threading.Thread(target=start_dashboard)
    dashboard_thread.daemon = True  # This ensures the thread will exit when the main program exits
    dashboard_thread.start()

