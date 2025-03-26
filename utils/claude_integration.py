# Create a new file: utils/claude_integration.py
import requests
from config import CLAUDE_API_KEY

def query_claude(question):
    """Send a question to Claude API and get a response"""
    
    if not CLAUDE_API_KEY:
        return "Claude API is not configured. Please add your API key to the .env file."
    
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-haiku-20240307",  # You can use a different model if needed
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data["content"][0]["text"]
        else:
            return f"Error from Claude API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"