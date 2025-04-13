from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


request_phone_number_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Iltimos pastdagi 👇 tugma orqali 📱 telefon raqamingizni yuboring!'
)