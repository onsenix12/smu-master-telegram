# SMU Master's Program Telegram Assistant

## Overview

This Telegram bot serves as an AI-powered educational assistant for SMU Master's Program students. It provides support for course information, learning materials, FAQs, and general academic queries, addressing the challenges faced by adult learners balancing academic, work, and personal commitments.

## Features

- **Course Information**: Access details about courses, instructors, syllabi, and prerequisites
- **FAQ Management**: View and search frequently asked questions about courses and program details
- **Email Verification**: Secure access through SMU email verification
- **Admin Dashboard**: Web-based interface for monitoring conversations and user management
- **AI Integration**: Powered by Claude AI for intelligent responses to student queries
- **Staff Commands**: Special commands for course administrators and staff members

## System Architecture

The bot implements a microservices architecture with the following components:

1. **User Interface**:
   - Telegram Bot for student interaction
   - Web-based admin dashboard

2. **Business Logic**:
   - Natural Language Processing for query understanding
   - Authentication and authorization
   - Course information management
   - FAQ management

3. **Data Storage**:
   - SQLite database for user profiles, conversations, course data, and FAQs

## Security Features

- **Authentication**: Email verification for SMU students
- **Authorization**: Role-based access control (students vs. staff)
- **Data Protection**: Secure handling of user data
- **API Security**: Protection for external service integrations

## Getting Started

### Prerequisites

- Python 3.9+
- Telegram Bot API token
- Claude API key (for AI responses)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smu-master-telegram.git
   cd smu-master-telegram
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following configuration:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   CLAUDE_API_KEY=your_claude_api_key
   DATABASE_PATH=bot.db
   DASHBOARD_USERNAME=admin
   DASHBOARD_PASSWORD=your_secure_password
   DASHBOARD_SECRET_KEY=your_secure_secret_key
   EMAIL_USER=your_outlook_email@outlook.com
   EMAIL_PASSWORD=your_email_password
   DEV_MODE=True  # Set to False in production
   ```

### Running the Bot

1. Start the bot:
   ```
   python3 main.py
   ```

2. Access the admin dashboard at `http://localhost:5002`

## Deployment on Replit

This project is deployed on Replit using a Reserved VM environment for continuous operation:

1. **Reserved VM Deployment**: 
   - Ensures high uptime and minimizes disruptions
   - Perfect for long-running applications like Telegram bots
   - Maintains persistent session data across restarts
   - Billed hourly at $0.014/hour

2. **Setup on Replit**:
   - Fork this repository to your Replit account
   - Add your secrets (TELEGRAM_TOKEN, CLAUDE_API_KEY, etc.) in Replit's Secrets tab
   - Choose "Always On" deployment to keep the bot running continuously
   - The bot automatically starts with `python3 main.py`

3. **Benefits of Reserved VM**:
   - Ideal for stateful applications like chatbots
   - Supports webhook operations
   - Provides consistent performance for users
   - Maintains persistent connections to external services

## Usage

### Student Commands

- `/start` - Begin interaction with the bot
- `/help` - Display available commands
- `/verify [email]` - Verify your SMU email address
- `/code [verification_code]` - Complete email verification
- `/course [code]` - Get information about a specific course
- `/course_faq [code] [number]` - View FAQs for a specific course
- `/faq [number]` - View general FAQs
- `/reset_verification` - Reset your verification status

### Staff Commands

- `/add_faq [question] | [answer]` - Add a new FAQ to the system
- `/make_staff [user_id]` - Promote a user to staff status (admin only)

### Direct Queries

Students can also ask questions directly, and the bot will:
1. Search for course-related information in its database
2. Check for FAQ matches
3. Use Claude AI for general knowledge queries

## Development

### Project Structure

- `main.py` - Entry point for the application
- `bot/` - Telegram bot handlers and commands
- `dashboard/` - Web admin dashboard
- `db/` - Database connection and models
- `auth/` - Authentication and verification
- `knowledge/` - Course information and FAQ management
- `utils/` - Helper functions and utilities
- `config.py` - Application configuration

### Testing

Run tests using pytest:
```
pytest
```

### Security Scanning

Run security scans using bandit:
```
bandit -r ./ --exclude ./venv
```

## CI/CD

The project uses GitHub Actions for continuous integration with:
- Automated testing
- Linting with flake8
- Security scanning with bandit

## Future Enhancements

- Integration with additional SMU systems
- Support for more complex queries
- Enhanced analytics for learning patterns
- Mobile-friendly admin dashboard
- Support for file uploads and sharing