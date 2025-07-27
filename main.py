#!/usr/bin/env python3
"""
Main entry point for the Telegram bot.
This file initializes and starts the bot with all handlers.
"""

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.config import BOT_TOKEN, LOG_LEVEL
from bot.commands import start_command, help_command, echo_command
from bot.handlers import handle_text_message, error_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to initialize and run the Telegram bot.
    """
    if not BOT_TOKEN:
        logger.error("Bot token not found. Please set TELEGRAM_BOT_TOKEN environment variable.")
        return

    logger.info("Starting Telegram bot...")

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))

    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("Bot handlers registered successfully")

    # Start the bot with polling
    try:
        logger.info("Starting polling...")
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        logger.info("Bot stopped")


if __name__ == '__main__':
    main()
