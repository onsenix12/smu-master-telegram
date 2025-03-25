from telegram import Update
from telegram.ext import CallbackContext
from db.database import save_user, save_conversation
from auth.verification import start_verification, verify_code, is_user_verified
from knowledge.manager import get_course_info, search_courses
from utils.claude_integration import query_claude
from knowledge.manager import search_courses
from db.database import get_connection
from knowledge.manager import get_all_faqs
from db.connection import DatabaseConnection
from utils.decorators import require_verification

def start_command(update: Update, context: CallbackContext):
    """Handle the /start command"""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username
    first_name = user.first_name
    
    # Save user to database
    save_user(user_id, username, first_name)
    
    # Check if the user is already verified
    if is_user_verified(user_id):
        # Welcome message for verified users
        welcome_message = (
            f"👋 Hi {first_name}! I'm the SMU Master's Program AI Assistant.\n\n"
            f"I can help you with:\n"
            f"• Course information\n"
            f"• Assignments and deadlines\n"
            f"• Learning materials\n\n"
            f"Type /help to see all available commands."
        )
        update.message.reply_text(welcome_message)
    else:
        # Message for unverified users
        verification_message = (
            f"👋 Hi {first_name}! Welcome to the SMU Master's Program AI Assistant.\n\n"
            f"Before we begin, please verify your SMU email address.\n\n"
            f"Use the command: /verify your.name@smu.edu.sg"
        )
        update.message.reply_text(verification_message)

@require_verification
def help_command(update: Update, context: CallbackContext):
    """Handle the /help command"""
    help_message = (
        "🔍 Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/course [code] - Get information about a course\n"
        "/course_faq [code] [number] - View FAQs for a specific course\n"
        "/verify [email] - Verify with your SMU email\n"
        "/reset_verification - Reset your verification status\n"
        "/faq - Show available FAQs\n\n"
        "You can also ask me questions directly!"
    )
    
    update.message.reply_text(help_message)

@require_verification
def handle_message(update: Update, context: CallbackContext):
    """Handle regular text messages"""
    user = update.effective_user
    user_id = str(user.id)
    message_text = update.message.text.strip()
    
    # Check if this is a question about course FAQs
    faq_keywords = ['faq', 'question', 'answer', 'frequently asked']
    course_pattern = r'IS\d{3}'
    
    import re
    # Extract potential course codes (like IS621)
    course_codes = re.findall(course_pattern, message_text.upper())
    
    # Check if the message is asking about FAQs for a course
    is_faq_question = any(keyword.lower() in message_text.lower() for keyword in faq_keywords) and course_codes
    
    if is_faq_question:
        course_code = course_codes[0]  # Use the first course code found
        
        # Get course info
        course = get_course_info(course_code)
        
        if not course:
            update.message.reply_text(f"Course {course_code} not found.")
            return
        
        # Check if course has FAQs
        if 'course_faqs' not in course or not course['course_faqs']:
            update.message.reply_text(f"No FAQs available for {course_code}.")
            return
        
        # Format FAQs
        faqs = course['course_faqs']
        
        # Look for specific number in the question (e.g., "faq 2 for IS621")
        faq_number_match = re.search(r'\b(question|faq|q)\s*#?\s*(\d+)\b', message_text.lower())
        if faq_number_match:
            try:
                faq_idx = int(faq_number_match.group(2)) - 1
                if 0 <= faq_idx < len(faqs):
                    faq = faqs[faq_idx]
                    response = f"❓ <b>Question:</b> {faq['question']}\n\n" \
                               f"✅ <b>Answer:</b> {faq['answer']}"
                    update.message.reply_text(response, parse_mode='HTML')
                    
                    # Save the conversation
                    save_conversation(user_id, message_text, response)
                    return
                else:
                    update.message.reply_text(f"FAQ #{faq_idx+1} not found for {course_code}.")
                    return
            except ValueError:
                pass
        
        # Show list of FAQs
        response = f"📋 <b>FAQs for {course_code}:</b>\n\n"
        for i, faq in enumerate(faqs):
            response += f"{i+1}. {faq['question']}\n"
        response += f"\nYou can ask about a specific FAQ by saying 'FAQ 1 for {course_code}' or use the command /course_faq {course_code} [number]."
        
        # Save the conversation
        save_conversation(user_id, message_text, response)
        
        update.message.reply_text(response, parse_mode='HTML')
        return
    
    # Check if this is a course-related question (non-FAQ)
    course_results = search_courses(message_text)
    
    if course_results:
        # Use local knowledge for course-related questions
        course_info = "\n\n".join([
            f"📚 <b>{course['course_code']}: {course['title']}</b>\n"
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
    
    # Use HTML parse mode for consistency
    update.message.reply_text(response, parse_mode='HTML')

def verify_command(update: Update, context: CallbackContext):
    """Handle the /verify command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if the user is already verified
    if is_user_verified(user_id):
        update.message.reply_text("You are already verified! ✅\n\nYou can use all bot features now.")
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
            "Example: /code 123456\n\n"
            "Once verified, you'll have full access to the bot's features."
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
    
    if success:
        # Send welcome message after successful verification
        welcome_message = (
            "🎉 Verification successful! You now have full access to all bot features.\n\n"
            "I can help you with:\n"
            "• Course information\n"
            "• Assignments and deadlines\n"
            "• Learning materials\n\n"
            "Type /help to see all available commands."
        )
        update.message.reply_text(welcome_message)

@require_verification
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
    
    # Format basic course info - using HTML instead of Markdown for better compatibility
    course_info = (
        f"📚 <b>{course['course_code']}: {course['title']}</b>\n\n"
        f"👨‍🏫 Instructor: {course['instructor']}\n\n"
        f"📝 Description: {course['description']}"
    )
    
    # Add credits and prerequisites if available
    if 'credits' in course and course['credits']:
        course_info += f"\n\n💯 Credits: {course['credits']}"
        
    if 'prerequisites' in course and course['prerequisites']:
        # Join prerequisites safely, escaping any special characters
        prereqs = ", ".join(str(p) for p in course['prerequisites'])
        course_info += f"\n\n⚠️ Prerequisites: {prereqs}"
    
    # Add syllabus overview if available
    if 'syllabus' in course and course['syllabus']:
        course_info += "\n\n📆 <b>Weekly Topics:</b>"
        for week in course['syllabus']:
            # Make sure 'week' and 'topic' exist to prevent errors
            if 'week' in week and 'topic' in week:
                week_num = week.get('week', '')
                topic = week.get('topic', '')
                course_info += f"\n• Week {week_num}: {topic}"
    
    # Add note about course FAQs if available
    if 'course_faqs' in course and course['course_faqs']:
        course_info += f"\n\n❓ This course has {len(course['course_faqs'])} FAQs. Use /course_faq {course_code} to view them."
    
    # Send with HTML parse mode instead of Markdown
    update.message.reply_text(course_info, parse_mode='HTML')

@require_verification
def course_faq_command(update: Update, context: CallbackContext):
    """Handle the /course_faq command to show FAQs for a specific course"""
    # Check if the course code was provided
    if not context.args or len(context.args) == 0:
        update.message.reply_text(
            "Please provide a course code.\n"
            "Example: /course_faq IS621"
        )
        return
        
    course_code = context.args[0].upper()
    
    # Get course info
    course = get_course_info(course_code)
    
    if not course:
        update.message.reply_text(f"Course {course_code} not found.")
        return
    
    # Check if course has FAQs
    if 'course_faqs' not in course or not course['course_faqs']:
        update.message.reply_text(f"No FAQs available for {course_code}.")
        return
    
    # Format FAQs
    faqs = course['course_faqs']
    
    # Check if a specific FAQ number was requested
    if len(context.args) > 1:
        try:
            faq_idx = int(context.args[1]) - 1
            if 0 <= faq_idx < len(faqs):
                faq = faqs[faq_idx]
                response = f"❓ <b>Question:</b> {faq['question']}\n\n" \
                           f"✅ <b>Answer:</b> {faq['answer']}"
                update.message.reply_text(response, parse_mode='HTML')
                return
            else:
                update.message.reply_text(f"FAQ #{faq_idx+1} not found for {course_code}.")
                return
        except ValueError:
            pass
    
    # Show list of FAQs
    response = f"📋 <b>FAQs for {course_code}:</b>\n\n"
    for i, faq in enumerate(faqs):
        response += f"{i+1}. {faq['question']}\n"
    response += f"\nUse /course_faq {course_code} [number] to see a specific answer."
    
    update.message.reply_text(response, parse_mode='HTML')

@require_verification
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
                response = f"❓ <b>Question:</b> {faq['question']}\n\n" \
                           f"✅ <b>Answer:</b> {faq['answer']}"
                update.message.reply_text(response, parse_mode='HTML')
                return
            else:
                update.message.reply_text(f"FAQ #{faq_idx+1} not found.")
                return
        except ValueError:
            pass
    
    # Show list of FAQs
    response = "📋 <b>Available FAQs:</b>\n\n"
    for i, faq in enumerate(faqs):
        response += f"{i+1}. {faq['question']}\n"
    response += "\nUse /faq [number] to see a specific answer."
    
    update.message.reply_text(response, parse_mode='HTML')

def reset_verification_command(update: Update, context: CallbackContext):
    """Handle the /reset_verification command"""
    user = update.effective_user
    user_id = str(user.id)
    
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE users 
            SET is_verified = 0, verification_code = NULL, code_expires_at = NULL
            WHERE user_id = ?
            ''', (user_id,))
            
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                update.message.reply_text("Your verification has been reset. You can now verify again using /verify.")
            else:
                update.message.reply_text("Reset failed. User not found in database.")
    except Exception as e:
        update.message.reply_text(f"Error resetting verification: {str(e)}")