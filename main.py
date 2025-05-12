import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from internal.bot.config.config import TOKEN, DATABASE
from internal.bot.handlers.download import router as download_router
from internal.bot.handlers.start import router as start_router
from internal.bot.handlers.send_video import router as send_video_router
from internal.database.db import create_db

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    if DATABASE:
        await create_db() 
    
    # Регистрируем обработчики
    dp.include_router(download_router)
    dp.include_router(start_router)
    dp.include_router(send_video_router)
    
    await bot.set_my_commands(commands=[BotCommand(command="start", description="Start bot"),
                                        BotCommand(command="help", description="Help menu")])

    try:
        logging.info("Бот запущен")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())