import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Import routers
from bot.handlers.start import router as start_router
from bot.handlers.tasks.create import router as tasks_create_router  
from bot.handlers.tasks.list import router as tasks_list_router
from bot.handlers.timer.start import router as timer_router
from bot.handlers.statistics.daily import router as stats_router


# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    # Initialize bot with token from environment
    bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN_HERE", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start_router)
    dp.include_router(tasks_create_router)
    dp.include_router(tasks_list_router)
    dp.include_router(timer_router)
    dp.include_router(stats_router)
    
    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())