from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_kb import main_buttons, get_navigation_keyboard
from keyboards.auth_kb import phone_btn
from db_handlers.db_users import is_user_authenticated, get_user_data
from db_handlers.db_promotions import load_active_promotions
from handlers.auth_handlers import Reg
from api.counterparty import get_balance_counterparty

router = Router()


@router.startup()
async def on_startup(bot: Bot):
    # Komandalarni menu tugamasiga chiqarish
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="reg", description="Qayta ro'yxatdan o'tish"),
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
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
    if is_user_authenticated(chat_id=message.from_user.id):
        phone_request_text = "📞 Iltimos, telefon raqamingizni pastdagi tugmani bosgan holda yuboring:"
        await state.set_state(Reg.phone_number)
        return await message.answer(text=phone_request_text, reply_markup=phone_btn)

    return await message.answer(text=greeting_text, reply_markup=main_buttons)


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


@router.message(F.text == "💳 Mening balansim")
async def cmd_counterparty_balance(message: Message):
    user = await get_user_data(chat_id=message.from_user.id)
    counterparty = await get_balance_counterparty(counterparty_id=str(user.get("counterparty_id")))
    balance_text = f"""
💳 <b>📊 Mening balansim</b>

🧑‍💼 <b>F.I.Sh:</b> {user.get("full_name")}
📞 <b>Telefon:</b> {user.get("phone_number")}

💰 <b>Joriy balans:</b> {counterparty.get("balance")} so'm
🎁 <b>Yig'ilgan bonuslar:</b> {counterparty.get("bonusBalance")} so'm

🛍 <b>Xaridlar soni:</b> {counterparty.get("demandsCount")} ta
💵 <b>Xaridlar summasi:</b> {counterparty.get("demandsSum")} so'm
📆 <b>Oxirgi xarid sanasi:</b> {counterparty.get("lastDemandDate")}

🎯 <b>Skidkalar summasi:</b> {counterparty.get("discountsSum")} so'm

↩️ <b>Vozvratlar soni:</b> {counterparty.get("returnsCount")} ta
💸 <b>Vozvratlar summasi:</b> {counterparty.get("returnsSum")} so'm

❗️Agar balansingizda xatolik bo‘lsa, operator bilan bog‘laning: @admin_username
"""
    await message.answer(text=balance_text, reply_markup=main_buttons)


async def send_promo_page(message: Message, index: int):
    promos = load_active_promotions()
    total = len(promos)
    print(index)
    if total == 0:
        return await message.answer("❌ Hozircha faol aksiyalar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday aksiya sahifasi mavjud emas.")

    promo = promos[index]
    kb = get_navigation_keyboard(index=index, total=total)
    text = f"""
<b>{promo["title"]}</b>

{promo["description"]}
"""

    return await message.answer_photo(photo=FSInputFile(promo["image"]), caption=text, reply_markup=kb)


@router.message(F.text == "🎁 Aksiyalar")
async def show_promotions(message: Message, state: FSMContext):
    await send_promo_page(message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prev_", "next_")))
async def navigate_posts(callback_query: CallbackQuery):
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total :
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_promo_page(callback_query.message, index)



