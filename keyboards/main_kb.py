from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_buttons = ReplyKeyboardMarkup(
    keyboard=[
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
    ],
    resize_keyboard=True
)


def get_promo_nav_keyboard(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"prevpromo_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"nextpromo_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_news_nav_keyboard(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"prevnew_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"nextnew_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
