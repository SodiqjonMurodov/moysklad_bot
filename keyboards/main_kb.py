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


def get_navigation_keyboard(index: int, total: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"prev_{index - 1}_{total}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"next_{index + 1}_{total}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


