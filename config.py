import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("WARNING: No TELEGRAM_TOKEN found in .env file!")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")

# Dashboard configuration
DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "password")
DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "your_secure_secret_key")  # Add this line

# Email verification settings
VERIFICATION_TIMEOUT = int(os.getenv("VERIFICATION_TIMEOUT", "600"))  # 10 minutes in seconds

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DEV_MODE = os.getenv("DEV_MODE", "True").lower() == "true"