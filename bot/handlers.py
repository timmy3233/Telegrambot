"""
Message handlers for the Telegram bot.
This module contains handlers for different types of messages and events.
"""

import logging
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes

from .config import DEFAULT_RESPONSE_ENABLED, RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW

logger = logging.getLogger(__name__)

# Simple rate limiting storage
user_message_times = defaultdict(list)


def is_rate_limited(user_id: int) -> bool:
    """
    Check if user is rate limited.
    Returns True if user has exceeded rate limit, False otherwise.
    """
    current_time = time.time()
    user_times = user_message_times[user_id]
    
    # Remove old timestamps outside the window
    user_times[:] = [t for t in user_times if current_time - t < RATE_LIMIT_WINDOW]
    
    # Check if user has exceeded rate limit
    if len(user_times) >= RATE_LIMIT_MESSAGES:
        return True
    
    # Add current timestamp
    user_times.append(current_time)
    return False


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle regular text messages from users.
    Provides automated responses based on message content.
    """
    try:
        user = update.effective_user
        message_text = update.message.text.lower().strip()
        
        # Rate limiting check
        if is_rate_limited(user.id):
            logger.warning(f"Rate limit exceeded for user {user.id}")
            await update.message.reply_text(
                "⚠️ You're sending messages too quickly. Please wait a moment before sending another message."
            )
            return
        
        logger.info(f"User {user.id} ({user.username}) sent message: {message_text[:50]}...")
        
        # Simple keyword-based responses
        response = await generate_response(message_text, user)
        
        if response:
            await update.message.reply_text(response)
        elif DEFAULT_RESPONSE_ENABLED:
            # Default response when no specific response is triggered
            await update.message.reply_text(
                "Thanks for your message! I'm a simple bot, but I'm here to help. "
                "Use /help to see what I can do!"
            )
    
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your message. Please try again."
        )


async def generate_response(message_text: str, user) -> str:
    """
    Generate an appropriate response based on the message content.
    This function can be extended to include more sophisticated response logic.
    """
    # Greeting responses
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in message_text for greeting in greetings):
        return f"Hello {user.first_name}! 👋 How can I help you today?"
    
    # Farewell responses
    farewells = ['bye', 'goodbye', 'see you', 'farewell', 'take care']
    if any(farewell in message_text for farewell in farewells):
        return "Goodbye! 👋 Feel free to message me anytime!"
    
    # Question responses
    question_words = ['what', 'how', 'when', 'where', 'why', 'who', '?']
    if any(word in message_text for word in question_words):
        return "That's a great question! While I'm a simple bot, you can use /help to see what I can do for you."
    
    # Thanks responses
    thanks_words = ['thank', 'thanks', 'appreciate', 'grateful']
    if any(word in message_text for word in thanks_words):
        return "You're very welcome! I'm happy to help! 😊"
    
    # Help requests
    help_words = ['help', 'assist', 'support', 'guidance']
    if any(word in message_text for word in help_words):
        return "I'd be happy to help! Use /help to see all available commands, or just tell me what you need."
    
    # Bot-related queries
    bot_words = ['bot', 'robot', 'ai', 'artificial']
    if any(word in message_text for word in bot_words):
        return "Yes, I'm a Telegram bot! I'm here to assist you. Use /help to see what I can do!"
    
    # No specific response triggered
    return None


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during bot operation.
    Logs errors and provides user feedback when appropriate.
    """
    logger.error(f"Update {update.update_id if update else 'Unknown'} caused error: {context.error}")
    
    # Send error message to user if update exists
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "🚫 Oops! Something went wrong. Our team has been notified. Please try again in a moment."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


# Cleanup function for rate limiting
def cleanup_rate_limit_data():
    """
    Clean up old rate limiting data to prevent memory leaks.
    Should be called periodically in production.
    """
    current_time = time.time()
    for user_id in list(user_message_times.keys()):
        user_times = user_message_times[user_id]
        user_times[:] = [t for t in user_times if current_time - t < RATE_LIMIT_WINDOW]
        
        # Remove empty entries
        if not user_times:
            del user_message_times[user_id]
    
    logger.info(f"Rate limit cleanup completed. Active users: {len(user_message_times)}")
