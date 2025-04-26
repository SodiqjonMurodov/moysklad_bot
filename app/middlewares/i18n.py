import gettext

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from babel.support import Translations
from app.database.requests import get_user

LOCALES_DIR = "locales"
DEFAULT_LANG = "ru"

async def setup_i18n(lang=DEFAULT_LANG):
    try:
        trans = gettext.translation("messages", localedir=LOCALES_DIR, languages=[lang])
        _ = trans.gettext
    except FileNotFoundError:
        _ = lambda s: s
    return _


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Translations:
        chat_id = event.from_user.id
        user = await get_user(int(chat_id))

        if user.lang:
            user_lang = user.lang
            print(f"User language1: {user_lang}")
        else:
            user_lang = event.from_user.language_code
            print(f"User language2: {user_lang}")
        lang = user_lang if user_lang in ["uz", "ru", "en", "kz"] else DEFAULT_LANG
        print(f"User language_lang: {lang}")

        _ = await setup_i18n(lang)
        data["_"] = _

        return await handler(event, data)

