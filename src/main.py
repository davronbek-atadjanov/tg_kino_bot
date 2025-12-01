"""
Bot main fayli - Dispatcher va middleware setup
"""
import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.database.connection import init_db, close_db
from src.middleware.subscription_check import SubscriptionCheckMiddleware
from src.routers import admin, user, subscription, common, echo_handler

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Bot kommandalarini o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam olish"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Bot ishga tushirish"""
    
    # Database init
    logger.info("Database initializatsiyasi...")
    await init_db()
    
    # Bot va Dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Routers qo'shish
    dp.include_router(subscription.router)
    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(echo_handler.router)
    
    # Middleware qo'shish (admin handlers oldidan)
    dp.message.middleware(SubscriptionCheckMiddleware())
    dp.callback_query.middleware(SubscriptionCheckMiddleware())
    
    # Kommandalarni o'rnatish
    await set_commands(bot)
    
    try:
        logger.info("Bot ishga tushurildi...")
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())