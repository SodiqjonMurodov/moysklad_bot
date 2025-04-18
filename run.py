import os, asyncio, logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import auth_handlers, main_handlers, admin_handlers
from database.models import async_main

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    await async_main()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()

    # Routers
    dp.include_routers(
        main_handlers.router,
        auth_handlers.router,
        admin_handlers.router
    )

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # logging
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
