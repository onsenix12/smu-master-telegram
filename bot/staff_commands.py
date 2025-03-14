from telegram import Update
from telegram.ext import CallbackContext
from db.database import is_staff, make_staff
from knowledge.manager import add_faq

def add_faq_command(update: Update, context: CallbackContext):
    """Handle the /add_faq command (staff only)"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if user is staff
    if not is_staff(user_id):
        update.message.reply_text("Sorry, this command is only available to staff members.")
        return
    
    # Check message format
    message_text = update.message.text
    # Remove the command part
    message_text = message_text.replace('/add_faq', '', 1).strip()
    
    # Split by pipe character
    parts = message_text.split('|')
    
    if len(parts) != 2:
        update.message.reply_text(
            "Please use the format: /add_faq Question | Answer"
        )
        return
    
    question = parts[0].strip()
    answer = parts[1].strip()
    
    # Add FAQ to database
    success = add_faq(question, answer, user_id)
    
    if success:
        update.message.reply_text("FAQ added successfully! ✅")
    else:
        update.message.reply_text("Error adding FAQ. Please try again.")

def make_staff_command(update: Update, context: CallbackContext):
    """Handle the /make_staff command (admin only)"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Hard-coded admin ID for simplicity (in a real app, store in config)
    # IMPORTANT: Replace this with your own Telegram user ID
    ADMIN_ID = "123456789"  # Replace with your actual Telegram ID
    
    if user_id != ADMIN_ID:
        update.message.reply_text("Sorry, this command is only available to the admin.")
        return
    
    # Check if user ID was provided
    if not context.args or len(context.args) == 0:
        update.message.reply_text(
            "Please provide a user ID.\n"
            "Example: /make_staff 123456789"
        )
        return
        
    target_user_id = context.args[0]
    
    # Make user a staff member
    success = make_staff(target_user_id)
    
    if success:
        update.message.reply_text(f"User {target_user_id} is now a staff member! ✅")
    else:
        update.message.reply_text("Error updating user. Please check the ID and try again.")