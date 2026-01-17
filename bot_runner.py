import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.core.config import settings

# Import routers
from src.bot.handlers.start import router as start_router
from src.bot.handlers.tasks.create import router as tasks_create_router  
from src.bot.handlers.tasks.list import router as tasks_list_router
from src.bot.handlers.timer.start import router as timer_router
from src.bot.handlers.statistics.daily import router as stats_router


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Check if bot token is provided
    if not settings.telegram_bot_token:
        logger.critical("FATAL: 'TELEGRAM_BOT_TOKEN' is not set in the environment.")
        sys.exit(1)
        
    # Initialize bot with token from settings
    bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start_router)
    dp.include_router(tasks_create_router)
    dp.include_router(tasks_list_router)
    dp.include_router(timer_router)
    dp.include_router(stats_router)
    
    # Start polling
    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())