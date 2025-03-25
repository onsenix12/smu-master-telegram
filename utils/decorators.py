from functools import wraps
from auth.verification import is_user_verified

def require_verification(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if not is_user_verified(user_id):
            update.message.reply_text(
                "⚠️ Please verify your SMU email before using this bot.\n\n"
                "Use the command: /verify your.name@smu.edu.sg"
            )
            return
        return func(update, context, *args, **kwargs)
    return wrapper