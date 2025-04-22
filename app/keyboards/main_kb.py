from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import get_user


async def get_main_buttons(chat_id) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="ℹ️ Biz haqimizda"),
            KeyboardButton(text="💳 Mening balansim")
        ],
        [
            KeyboardButton(text="🎁 Aksiyalar"),
            KeyboardButton(text="🧾 Xaridlar tarixi")
        ],
        [
            KeyboardButton(text="📰 Yangiliklar"),
            KeyboardButton(text="✍️ Taklif va shikoyatlar")
        ]
    ]

    # Userni admin ekanligini tekshirish
    user = await get_user(chat_id)
    if user:
        if user.is_admin:
            buttons.append([
                KeyboardButton(text="🛠 Admin paneliga o'tish")
            ])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_promos_nav(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevPromo_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextPromo_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def get_news_nav(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevNew_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextNew_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def get_purchase_history_nav(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevSaleHistory_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextSaleHistory_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])

