from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


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


def get_admin_promos_nav(index: int, total: int, promos):
    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prevAdminPromo_{index - 1}_{total}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"nextAdminPromo_{index + 1}_{total}"))

    # Aktivlik tugamsini aniqlash
    if promos[index]["active"]:
        activity_btn = [InlineKeyboardButton(text="❎ Deaktivlashtirish", callback_data=f"promoActivate_{index}")]
    else:
        activity_btn = [InlineKeyboardButton(text="✅ Aktivlashtirish", callback_data=f"promoDeactivate_{index}")]

    buttons = [
        nav_buttons,
        activity_btn,
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="promoEdit"),
            InlineKeyboardButton(text="⛔️ O'chirish", callback_data="promoDelete")
        ],
        [
            InlineKeyboardButton(text="🚀 Foydalanuvchilarga tarqatish", callback_data="promoShare")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


