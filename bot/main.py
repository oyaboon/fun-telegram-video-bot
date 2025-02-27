"""
main.py
-------
Purpose: Main entry point for the Telegram bot
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from .handlers import setup_handlers, on_startup, on_shutdown

# Load environment variables
load_dotenv()

# Get bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("No bot token provided. Please set BOT_TOKEN in .env file.")
    exit(1)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Register handlers
setup_handlers(dp)

async def main_async():
    """
    Async main function to start the bot
    """
    logger.info("Starting Telegram Video Bot...")
    
    # Set up startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start the bot
    await dp.start_polling(bot, skip_updates=True)

def main():
    """
    Main function to start the bot
    """
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 