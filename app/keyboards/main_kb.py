from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import get_user
from typing import Callable


async def get_main_buttons(_: Callable, chat_id) -> ReplyKeyboardMarkup:
    print(f"get_main_buttons: {chat_id}")
    buttons = [
        [
            KeyboardButton(text=_("ℹ️ Biz haqimizda")),
            KeyboardButton(text=_("💳 Mening balansim"))
        ],
        [
            KeyboardButton(text=_("🎁 Aksiyalar")),
            KeyboardButton(text=_("🧾 Xaridlar tarixi"))
        ],
        [
            KeyboardButton(text=_("📰 Yangiliklar")),
            KeyboardButton(text=_("🌐 Tilni o'zgartirish"))
        ],
        [
            KeyboardButton(text=_("✍️ Taklif va shikoyatlar")),
        ]
    ]

    # Userni admin ekanligini tekshirish
    user = await get_user(chat_id)
    if user and user.is_admin:
        print(f"User {chat_id} is admin")
        buttons.append([
            KeyboardButton(text=_("🛠 Admin paneliga o'tish"))
        ])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_lang_buttons(_: Callable) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="🇷🇺 Русский"),
            KeyboardButton(text="🇬🇧 English")
        ],
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text="🇰🇿 Қазақша")

        ],
        [
            KeyboardButton(text=_("🔙 Orqaga"))
        ]
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_promos_nav(_: Callable, index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text=_("⬅️ Oldingi"), callback_data=f"prevPromo_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text=_("Keyingi ➡️"), callback_data=f"nextPromo_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def get_news_nav(_: Callable, index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text=_("⬅️ Oldingi"), callback_data=f"prevNew_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text=_("Keyingi ➡️"), callback_data=f"nextNew_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def get_purchase_history_nav(_: Callable, index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text=_("⬅️ Oldingi"), callback_data=f"prevSaleHistory_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text=_("Keyingi ➡️"), callback_data=f"nextSaleHistory_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def get_cancel_feedback_button(_: Callable):
    button = [
        [
            InlineKeyboardButton(text=_("❌ Bekor qilish"), callback_data="cancelFeedbackMessage")
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=button)
