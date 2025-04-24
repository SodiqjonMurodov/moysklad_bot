import asyncio
import logging
import sys

from aiogram import Dispatcher
from app.core.bot import bot
from app.handlers import main_handlers, admin_handlers, auth_handlers
from app.database.models import async_main
from app.middlewares.i18n import I18nMiddleware


async def main():
    # Connection to db
    await async_main()

    dp = Dispatcher()

    # I18n localization
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Routers
    dp.include_routers(
        main_handlers.router,
        auth_handlers.router,
        admin_handlers.router
    )

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
                        )  # logging
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
