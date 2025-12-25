import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from settings import config
from bot.handlers import router as deepseek_router

async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(deepseek_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот отключен пользователем!")