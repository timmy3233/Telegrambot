"""
Configuration module for the Telegram bot.
Handles environment variables and bot settings.
"""

import os
from typing import Optional

# Bot configuration
BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Rate limiting configuration
RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Bot behavior configuration
DEFAULT_RESPONSE_ENABLED: bool = os.getenv("DEFAULT_RESPONSE_ENABLED", "true").lower() == "true"
WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE", 
    "👋 Welcome! I'm your friendly Telegram bot. Use /help to see available commands.")

HELP_MESSAGE: str = os.getenv("HELP_MESSAGE", """
🤖 **Available Commands:**

/start - Start the bot and get a welcome message
/help - Show this help message
/echo <message> - Echo back your message

You can also just send me any text message and I'll respond!

Need help? Just type any message and I'll do my best to assist you.
""")

# Validate configuration
def validate_config() -> bool:
    """
    Validate the bot configuration.
    Returns True if configuration is valid, False otherwise.
    """
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is required")
        return False
    
    if len(BOT_TOKEN) < 10:
        print("Error: TELEGRAM_BOT_TOKEN appears to be invalid")
        return False
    
    return True
