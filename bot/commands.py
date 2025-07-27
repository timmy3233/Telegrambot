"""
Command handlers for the Telegram bot.
This module contains all the command functions that respond to user commands.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .config import WELCOME_MESSAGE, HELP_MESSAGE

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    Sends a welcome message to the user.
    """
    try:
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong while processing your request. Please try again."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    Sends help information about available commands.
    """
    try:
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) requested help")
        
        await update.message.reply_text(
            HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't load the help information right now. Please try again later."
        )


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /echo command.
    Echoes back the message provided by the user.
    """
    try:
        user = update.effective_user
        
        # Get the message text after the command
        message_text = update.message.text
        command_parts = message_text.split(' ', 1)
        
        if len(command_parts) < 2:
            await update.message.reply_text(
                "Please provide a message to echo. Usage: /echo <your message>"
            )
            return
        
        echo_text = command_parts[1]
        logger.info(f"User {user.id} ({user.username}) used echo command")
        
        await update.message.reply_text(
            f"🔊 You said: {echo_text}"
        )
    except Exception as e:
        logger.error(f"Error in echo_command: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't echo your message right now. Please try again."
        )


# Dictionary to easily add new commands
COMMANDS = {
    'start': start_command,
    'help': help_command,
    'echo': echo_command,
}


def get_command_list() -> str:
    """
    Get a formatted list of available commands.
    Used for dynamic help generation.
    """
    command_descriptions = {
        'start': 'Start the bot and get a welcome message',
        'help': 'Show help information',
        'echo': 'Echo back your message',
    }
    
    command_list = []
    for cmd, desc in command_descriptions.items():
        command_list.append(f"/{cmd} - {desc}")
    
    return "\n".join(command_list)
