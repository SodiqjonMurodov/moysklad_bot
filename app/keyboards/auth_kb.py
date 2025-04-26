from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Callable


async def get_phone_request_btn(_: Callable) -> ReplyKeyboardMarkup:
    button = [
        [KeyboardButton(text=_("📱 Raqamni yuborish"), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=_("Iltimos pastdagi 👇 tugma orqali 📱 telefon raqamingizni yuboring!")
    )

