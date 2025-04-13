from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from keyboards.main_kb import main_buttons

router = Router()


@router.startup()
async def on_startup(bot: Bot):
    # Komandalarni menu tugamasiga chiqarish
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="reg", description="Qayta ro'yxatdan o'tish"),
    ])


@router.message(CommandStart())
async def cmd_start(message: Message):
    # /start handleri funksiyasi
    greeting_text = """
<b>👋 Assalomu alaykum va Telegram botimizga xush kelibsiz!</b>

Bu bot orqali siz quyidagi bo‘limlardan foydalanishingiz mumkin:

ℹ️ <b>Biz haqimizda</b> — kompaniyamiz faoliyati haqida qisqacha ma’lumot  
💳 <b>Mening balansim</b> — hisobingizdagi bonuslar va qoldiqni ko‘rish  
🎁 <b>Aksiyalar</b> — hozirgi chegirmalar va maxsus takliflar  
🧾 <b>Xaridlar tarixi</b> — amalga oshirgan xaridlaringiz ro‘yxati  
📰 <b>Yangiliklar</b> — eng so‘nggi yangiliklar va e’lonlar  
✍️ <b>Taklif va shikoyatlar</b> — bizga fikr va takliflaringizni yuboring

<b>💚 Oilamizga marhamat!</b>
"""
    await message.answer(text=greeting_text, reply_markup=main_buttons)


@router.message(F.text == "ℹ️ Biz haqimizda")
async def cmd_about_us(message: Message):
    about_text = """
<b>ℹ️ Biz haqimizda</b>

    Assalomu alaykum!  
Biz — <b>[Sizning kompaniya nomi]</b>, mijozlarimizga yuqori sifatli xizmat va mahsulotlar taqdim etishga intiladigan jamoamiz. 

Kompaniyamiz quyidagi yo‘nalishlarda faoliyat yuritadi:
    ✅ Sifatli mahsulotlar savdosi  
    ✅ Mijozlarga sodiqlik tizimi (bonus va chegirmalar)  
    ✅ Onlayn xizmatlar orqali tezkor va qulay xizmat ko‘rsatish  

<b>🎯 Bizning maqsadimiz:</b>  
    Har bir mijozga qulaylik yaratish va ishonchli xizmat ko‘rsatish orqali uzoq muddatli hamkorlikka erishish.

<b>💡 Biz nimasi bilan ajralib turamiz?</b>  
    • Sifatli xizmat  
    • Tezkor aloqa  
    • Hamyonbop narxlar  
    • Mijozlarga individual yondashuv  

<b>📞 Biz bilan bog‘lanish:</b>  
    📱 Telefon: +998 90 123 45 67  
    ✉️ Email: info@company.uz  
    📍 Manzil: Toshkent shahri, Amir Temur ko‘chasi, 15-uy  
    🌐 Veb-sayt: www.company.uz  
    📱 Telegram: @company_support

<b>💚 Sizga xizmat ko‘rsatishdan mamnunmiz!</b>
"""
    await message.answer(text=about_text, reply_markup=main_buttons)

