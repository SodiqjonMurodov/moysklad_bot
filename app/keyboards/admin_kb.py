from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import get_promo_list, get_new_list


async def get_admin_panel_buttons() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="🎁 Aksiyalar ro'yxati"),
            KeyboardButton(text="📰 Yangiliklar ro'yxati")
        ],
        [
            KeyboardButton(text="➕ Aksiya qo'shish"),
            KeyboardButton(text="➕ Yangilik qo'shish")
        ],
        [
            KeyboardButton(text="🏠 Foydalanuvchi paneliga o'tish")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_admin_promos_nav(index: int, total: int):
    nav_buttons = []
    promos = await get_promo_list()
    promo = promos[index]
    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevAdminPromo_{index - 1}_{total}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextAdminPromo_{index + 1}_{total}"))

    # Aktivlik tugamsini aniqlash
    if promo.is_active:
        activity_btn = [InlineKeyboardButton(text="❎ Deaktivlashtirish", callback_data=f"promoDeactivate_{index}_{promo.id}")]
    else:
        activity_btn = [InlineKeyboardButton(text="✅ Aktivlashtirish", callback_data=f"promoActivate_{index}_{promo.id}")]

    buttons = [
        nav_buttons,
        activity_btn,
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"promoEdit_{promo.id}"),
            InlineKeyboardButton(text="⛔️ O'chirish", callback_data=f"promoDelete_{promo.id}")
        ],
        [
            InlineKeyboardButton(text="🚀 Foydalanuvchilarga tarqatish", callback_data=f"promoShare_{promo.id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_admin_news_nav(index: int, total: int):
    nav_buttons = []
    news = await get_new_list()
    new = news[index]
    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevAdminNew_{index - 1}_{total}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextAdminNew_{index + 1}_{total}"))

    # Aktivlik tugamsini aniqlash
    if new.is_active:
        activity_btn = [InlineKeyboardButton(text="❎ Deaktivlashtirish", callback_data=f"newDeactivate_{index}_{new.id}")]
    else:
        activity_btn = [InlineKeyboardButton(text="✅ Aktivlashtirish", callback_data=f"newActivate_{index}_{new.id}")]

    buttons = [
        nav_buttons,
        activity_btn,
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"newEdit_{new.id}"),
            InlineKeyboardButton(text="⛔️ O'chirish", callback_data=f"newDelete_{new.id}")
        ],
        [
            InlineKeyboardButton(text="🚀 Foydalanuvchilarga tarqatish", callback_data=f"newShare_{new.id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_feedback_answer_btn(chat_id, message_id):
    button = [
        [InlineKeyboardButton(text=" Javob yozish", callback_data=f"feedbackAnswer_{chat_id}_{message_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button)

