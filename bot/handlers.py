from telegram import Update
from telegram.ext import CallbackContext
from db.database import save_user, save_conversation
from auth.verification import start_verification, verify_code, is_user_verified
from knowledge.manager import get_course_info, search_courses
from utils.claude_integration import query_claude
from knowledge.manager import search_courses
from db.database import get_connection
from knowledge.manager import get_all_faqs

def start_command(update: Update, context: CallbackContext):
    """Handle the /start command"""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username
    first_name = user.first_name
    
    # Save user to database
    save_user(user_id, username, first_name)
    
    # Welcome message
    welcome_message = (
        f"👋 Hi {first_name}! I'm the SMU Master's Program AI Assistant.\n\n"
        f"I can help you with:\n"
        f"• Course information\n"
        f"• Assignments and deadlines\n"
        f"• Learning materials\n\n"
        f"Type /help to see all available commands."
    )
    
    update.message.reply_text(welcome_message)
    
def help_command(update: Update, context: CallbackContext):
    """Handle the /help command"""
    help_message = (
        "🔍 Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/course [code] - Get information about a course\n"
        "/verify [email] - Verify with your SMU email\n"
        "/reset_verification - Reset your verification status\n"
        "/faq - Show available FAQs\n"
        "You can also ask me questions directly!"
    )
    
    update.message.reply_text(help_message)

def handle_message(update: Update, context: CallbackContext):
    """Handle regular text messages"""
    user = update.effective_user
    user_id = str(user.id)
    message_text = update.message.text
    
    # Check if this is a course-related question
    course_results = search_courses(message_text)
    
    if course_results:
        # Use local knowledge for course-related questions
        course_info = "\n\n".join([
            f"📚 *{course['course_code']}: {course['title']}*\n"
            f"👨‍🏫 Instructor: {course['instructor']}\n"
            f"📝 Description: {course['description']}"
            for course in course_results
        ])
        
        response = f"Here's what I found about your question:\n\n{course_info}"
    else:
        # Use Claude for general knowledge questions
        response = query_claude(message_text)
    
    # Save the conversation
    save_conversation(user_id, message_text, response)
    
    update.message.reply_text(response, parse_mode='Markdown')


# Add these command handlers
def verify_command(update: Update, context: CallbackContext):
    """Handle the /verify command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if the user is already verified
    if is_user_verified(user_id):
        update.message.reply_text("You are already verified! ✅")
        return
    
    # Check if email was provided
    if not context.args or len(context.args) == 0:
        update.message.reply_text(
            "Please provide your SMU email address.\n"
            "Example: /verify your.name@smu.edu.sg"
        )
        return
        
    email = context.args[0].lower()
    
    # Start verification process
    success, message = start_verification(user_id, email)
    update.message.reply_text(message)
    
    if success:
        update.message.reply_text(
            "Please enter the code using the /code command.\n"
            "Example: /code 123456"
        )

def code_command(update: Update, context: CallbackContext):
    """Handle the /code command for verification"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if the code was provided
    if not context.args or len(context.args) == 0:
        update.message.reply_text(
            "Please provide the verification code sent to your email.\n"
            "Example: /code 123456"
        )
        return
        
    verification_code = context.args[0]
    
    # Verify the code
    success, message = verify_code(user_id, verification_code)
    update.message.reply_text(message)

def course_command(update: Update, context: CallbackContext):
    """Handle the /course command"""
    # Check if the course code was provided
    if not context.args or len(context.args) == 0:
        update.message.reply_text(
            "Please provide a course code.\n"
            "Example: /course IS621"
        )
        return
        
    course_code = context.args[0].upper()
    
    # Get course info
    course = get_course_info(course_code)
    
    if not course:
        update.message.reply_text(f"Course {course_code} not found.")
        return
    
    # Format course info
    course_info = (
        f"📚 *{course['course_code']}: {course['title']}*\n\n"
        f"👨‍🏫 Instructor: {course['instructor']}\n\n"
        f"📝 Description: {course['description']}"
    )
    
    update.message.reply_text(course_info, parse_mode='Markdown')


def faq_command(update: Update, context: CallbackContext):
    """Handle the /faq command"""
    # Get FAQs
    faqs = get_all_faqs()
    
    if not faqs:
        update.message.reply_text("No FAQs available yet.")
        return
    
    # Get specific FAQ if number provided
    if context.args and len(context.args) > 0:
        try:
            faq_idx = int(context.args[0]) - 1
            if 0 <= faq_idx < len(faqs):
                faq = faqs[faq_idx]
                response = f"❓ *Question:* {faq['question']}\n\n" \
                           f"✅ *Answer:* {faq['answer']}"
                update.message.reply_text(response, parse_mode='Markdown')
                return
            else:
                update.message.reply_text(f"FAQ #{faq_idx+1} not found.")
                return
        except ValueError:
            pass
    
    # Show list of FAQs
    response = "📋 *Available FAQs:*\n\n"
    for i, faq in enumerate(faqs):
        response += f"{i+1}. {faq['question']}\n"
    response += "\nUse /faq [number] to see a specific answer."
    
    update.message.reply_text(response, parse_mode='Markdown')

def reset_verification_command(update: Update, context: CallbackContext):
    """Handle the /reset_verification command"""
    user = update.effective_user
    user_id = str(user.id)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE users 
        SET is_verified = 0, verification_code = NULL, code_expires_at = NULL
        WHERE user_id = ?
        ''', (user_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            update.message.reply_text("Your verification has been reset. You can now verify again using /verify.")
        else:
            update.message.reply_text("Reset failed. User not found in database.")
            
    except Exception as e:
        update.message.reply_text(f"Error resetting verification: {str(e)}")
    finally:
        conn.close()
    