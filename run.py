import asyncio
import logging

from aiogram import Dispatcher
from core.bot import bot
from handlers import auth_handlers, main_handlers, admin_handlers
from database.models import async_main


async def main():
    # Connection to db
    await async_main()

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
