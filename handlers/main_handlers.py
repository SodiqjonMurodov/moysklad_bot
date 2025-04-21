import asyncio
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from core.bot import bot
from handlers.admin_handlers import parse_entities
from handlers.auth_handlers import Reg
from keyboards.admin_kb import get_feedback_answer_btn
from keyboards.main_kb import get_main_buttons, get_promos_nav, get_news_nav, get_purchase_history_nav
from keyboards.auth_kb import phone_btn
from database.requests import is_user_authenticated, get_user, get_active_promo_list, get_new_list, get_admin_users_list
from api.counterparty import get_balance_counterparty
from api.demand import get_demands_by_counterparty, get_positions_from_demand
from api.salesreturn import get_salesreturns_by_counterparty, get_positions_from_salesreturn
from api.objects import get_object_by_url
from utils.formats import pretty_sum, pretty_datetime

router = Router()


@router.startup()
async def on_startup():
    # Komandalarni menu tugamasiga chiqarish
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="reg", description="Qayta ro'yxatdan o'tish")
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
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
    chat_id = message.from_user.id

    if not await is_user_authenticated(chat_id):
        phone_request_text = "📞 Iltimos, ro'yxatdan o'tish uchun telefon raqamingizni pastdagi tugmani bosgan holda yuboring:"
        await state.set_state(Reg.phone_number)
        return await message.answer(text=phone_request_text, reply_markup=phone_btn)

    main_kb = await get_main_buttons(chat_id)
    return await message.answer(text=greeting_text, reply_markup=main_kb)


# Biz haqimizda bo'limi
@router.message(F.text == "ℹ️ Biz haqimizda")
async def cmd_about_us(message: Message, state: FSMContext):
    await state.clear()
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
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(chat_id)
    await message.answer(text=about_text, reply_markup=main_kb)


# Mening balansim bo'limi
@router.message(F.text == "💳 Mening balansim")
async def cmd_counterparty_balance(message: Message, state: FSMContext):
    await state.clear()
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(chat_id)
    user = await get_user(chat_id)
    counterparty = await get_balance_counterparty(counterparty_id=user.api_id)
    balance_text = f"""
💳 <b>Mening balansim</b>

🧑‍💼 <b>F.I.Sh:</b> {user.full_name}
📞 <b>Telefon:</b> {user.phone_number}

💰 <b>Joriy balans:</b> {pretty_sum(counterparty.get("balance"))} so'm
🎁 <b>Yig'ilgan bonuslar:</b> {pretty_sum(counterparty.get("bonusBalance"))} so'm

🛍 <b>Xaridlar soni:</b> {counterparty.get("demandsCount")} ta
💵 <b>Xaridlar summasi:</b> {pretty_sum(counterparty.get("demandsSum"))} so'm
📆 <b>Oxirgi xarid sanasi:</b> {pretty_datetime(counterparty.get("lastDemandDate"))}

🎯 <b>Skidkalar summasi:</b> {pretty_sum(counterparty.get("discountsSum"))} so'm

↩️ <b>Vozvratlar soni:</b> {counterparty.get("returnsCount")} ta
💸 <b>Vozvratlar summasi:</b> {pretty_sum(counterparty.get("returnsSum"))} so'm

❗️Agar balansingizda xatolik bo‘lsa, operator bilan bog‘laning: @admin_username
"""
    await message.answer(text=balance_text, reply_markup=main_kb)


# Aksiyalar bo'limi
async def send_promo_page(message: Message, index: int):
    promos = await get_active_promo_list()

    if promos is None:
        return await message.answer("❌ Hozircha aksiyalar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    total = len(promos)

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday aksiya sahifasi mavjud emas.")

    promo = promos[index]
    kb = await get_promos_nav(index=index, total=total)
    # Parse entities
    entities = await parse_entities(promo.caption_entities)
    promo_page = None

    if promo.content_type == "text":
        promo_page = await message.answer(
            text=promo.caption,
            entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    elif promo.content_type == "photo":
        promo_page = await message.answer_photo(
            photo=promo.file_id,
            caption=promo.caption,
            caption_entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    elif promo.content_type == "video":
        promo_page = await message.answer_video(
            video=promo.file_id,
            caption=promo.caption,
            caption_entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    return promo_page


@router.message(F.text == "🎁 Aksiyalar")
async def show_promotions(message: Message, state: FSMContext):
    await state.clear()
    await send_promo_page(message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevPromo_", "nextPromo_")))
async def navigate_posts(callback_query: CallbackQuery):
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_promo_page(callback_query.message, index)


# Yangiliklar bo'limi
async def send_new_page(message: Message, index: int):
    news = await get_new_list()

    if news is None:
        return await message.answer("❌ Hozircha yangiliklar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    total = len(news)

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday yangilik sahifasi mavjud emas.")

    new = news[index]
    kb = await get_news_nav(index=index, total=total)
    # Parse entities
    entities = await parse_entities(new.caption_entities)
    new_page = None

    if new.content_type == "text":
        new_page = await message.answer(
            text=new.caption,
            entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    elif new.content_type == "photo":
        new_page = await message.answer_photo(
            photo=new.file_id,
            caption=new.caption,
            caption_entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    elif new.content_type == "video":
        new_page = await message.answer_video(
            video=new.file_id,
            caption=new.caption,
            caption_entities=entities,
            reply_markup=kb,
            parse_mode=None
        )
    return new_page


@router.message(F.text == "📰 Yangiliklar")
async def show_news(message: Message, state: FSMContext):
    await state.clear()
    await send_new_page(message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevNew_", "nextNew_")))
async def navigate_news(callback_query: CallbackQuery):
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_new_page(callback_query.message, index)


# Xaridlar tarixi bo'limi
async def get_sorted_history_data(message: Message):
    """
    Xaridlar tarixini vaqti bo'yicha sortirovkalash

    """
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer(text="🔒 Iltimos, ro'yxatdan o'tganingizga ishonch hosil qiling!")
        return None

    demands = await get_demands_by_counterparty(user.api_id)
    sales_returns = await get_salesreturns_by_counterparty(user.api_id)
    history_data = []

    if demands:
        history_data.extend(demands)
    if sales_returns:
        history_data.extend(sales_returns)

    sorted_history_data_desc = sorted(history_data,
                                      key=lambda x: datetime.strptime(x["moment"], "%Y-%m-%d %H:%M:%S.%f"),
                                      reverse=True)
    return sorted_history_data_desc


async def send_purchase_history_page(message: Message, sorted_data: list, index: int):
    wait_msg = await message.answer("⏳ Iltimos, kuting...")
    total = len(sorted_data)

    if total == 0:
        return await wait_msg.edit_text("❌ Sizda hozircha xaridlar tarixi mavjud emas.")

    if not isinstance(index, int):
        return await wait_msg.edit_text("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await wait_msg.edit_text("⚠️ Bunday sahifasi mavjud emas.")

    data = sorted_data[index]
    kb = await get_purchase_history_nav(index=index, total=total)
    positions = []
    doc_type = ""

    # Dokument turini aniqlash
    if "salesreturn" in data["meta"]["href"]:
        doc_type = "Vozvrat"
        positions = await get_positions_from_salesreturn(data["id"])
    elif "demand" in data["meta"]["href"]:
        doc_type = "Xarid"
        positions = await get_positions_from_demand(data["id"])

    strpositions = "" # Dokumentdagi tovarlar ro'yxati
    product_order = 1 # Tovarlarni tartib raqami

    # Valyutasini olish
    currency_url = data["rate"]["currency"]["meta"]["href"]
    currency = await get_object_by_url(currency_url)

    if positions:
        for position in positions:
            # Mahsulot ma'lumotlarini olish
            product_url = position["assortment"]["meta"]["href"]
            product = await get_object_by_url(product_url)

            # O'lchov birligini olish
            uomname_url = product["uom"]["meta"]["href"]
            uomname = await get_object_by_url(uomname_url)

            strpositions += f"📌 {product_order}.{product['name']}\n\t\t 🔢 Miqdori: {position['quantity']} <i>{uomname['name']}</i>\n\t\t 💰 Narxi: {pretty_sum(position['price'])} <i>{currency['name']}</i>\n"
            product_order += 1

            # Skidka borligini tekshirish
            if not position['discount'] == 0:
                strpositions += f"\t\t 🎁 Skidka: {pretty_sum(position['discount'])} <i>{currency['name']}</i>\n\n"
            else:
                strpositions += "\n"

    history_text = f"""
📃 <b>{doc_type}</b> № {data["name"]}
🕒 <i>{pretty_datetime(data["moment"])}</i>

📦 <b>Tovarlar ro'yxati:</b>
{strpositions}💵 <b>{doc_type}lar summasi:</b> {pretty_sum(data["sum"])} <i>{currency["name"]}</i>
    """
    return await wait_msg.edit_text(text=history_text, reply_markup=kb)


@router.message(F.text == "🧾 Xaridlar tarixi")
async def show_purchase_history(message: Message, state: FSMContext):
    await state.clear()
    sorted_data = await get_sorted_history_data(message)
    await state.update_data(sorted_data=sorted_data)
    await send_purchase_history_page(message, sorted_data, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevSaleHistory_", "nextSaleHistory_")))
async def navigate_purchase_history(callback_query: CallbackQuery, state: FSMContext):
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    data = await state.get_data()
    sorted_data = data.get("sorted_data", [])

    if not sorted_data:
        return await callback_query.message.answer("❌ Xaridlar tarixi ma'lumotlarini topib bo'lmadi.")

    await callback_query.answer("")
    return await send_purchase_history_page(callback_query.message, sorted_data, index)


# Taklif va shikoyatlar bo'limi
class FeedbackStates(StatesGroup):
    AwaitFeedback = State()
    AnswerFeedback = State()


@router.message(F.text == "✍️ Taklif va shikoyatlar")
async def show_feedback(message: Message, state: FSMContext):
    await state.clear()
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(chat_id)
    feedback_txt = """
✍️ <b>Taklif va shikoyatlar bo‘limi</b>\n\n
Sizning fikringiz biz uchun juda muhim!\n
Iltimos, o‘zingizni qiziqtirgan masala, taklif yoki shikoyatingizni shu yerga yozib qoldiring.\n\n
📌 Biz barcha xabarlarni diqqat bilan ko‘rib chiqamiz va imkon qadar tez orada javob beramiz.  
"""
    await state.set_state(FeedbackStates.AwaitFeedback)
    await message.answer(text=feedback_txt, reply_markup=main_kb)


@router.message(FeedbackStates.AwaitFeedback)
async def send_feedback_to_admins(message: Message, state: FSMContext):
    admins = await get_admin_users_list()
    feedback_text = message.text
    feedback_entities = message.entities
    user = await get_user(message.from_user.id)
    kb = await get_feedback_answer_btn(message_id=message.message_id, chat_id=message.from_user.id)

    if not user:
        await message.answer(text="🔒 Iltimos, ro'yxatdan o'tganingizga ishonch hosil qiling!")
        return None

    if not message.text:
        return await message.answer("🔔 Iltimos, faqat matn shaklidagi ma'lumot yuboring!")

    feedback = f"""
<b>📩 Yangi taklif yoki shikoyat</b>

<b>📝 Xabar:</b>
{feedback_text}

<b>👤 Foydalanuvchi:</b> @{message.from_user.username or "Username yo'q"}
<b>📞 Telefon raqam:</b> {user.phone_number}
"""

    for admin in admins:
        try:
            await bot.send_message(chat_id=admin.tg_id, text=feedback, entities=feedback_entities, reply_markup=kb)
            await asyncio.sleep(0.05)  # Antiflood uchun kichik pauza (50ms)
        except Exception as e:
            print(f"Xatolik {admin.tg_id} ga yuborishda: {e}")

    await state.clear()
    await message.answer("✅ Taklifingiz/shikoyatingiz adminga yuborildi. Rahmat!",
                         reply_markup=await get_main_buttons(message.from_user.id))


@router.callback_query(lambda c: c.data.startswith("feedbackAnswer_"))
async def feedback_answer(callback_query: CallbackQuery, state: FSMContext):
    action, chat_id, message_id = callback_query.data.split("_")

    # Chat ID va Message ID ni int ga aylantirib olamiz!
    await state.set_state(FeedbackStates.AnswerFeedback)
    await state.update_data(chat_id=int(chat_id), message_id=int(message_id))

    await callback_query.answer()
    await callback_query.message.answer("✏️ Foydalanuvchiga javob yozing:")


@router.message(FeedbackStates.AnswerFeedback)
async def send_feedback_answer_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    if chat_id and message_id:
        try:
            await message.bot.send_message(
                chat_id=chat_id,
                text=message.text,
                reply_to_message_id=message_id
            )
            await message.answer("✅ Javob yuborildi.")
        except TelegramBadRequest:
            await message.answer("⚠️ Foydalanuvchining chatini topib bo‘lmadi. Ehtimol, u botni bloklagan.")
    else:
        await message.answer("⚠️ Xabar yuborish uchun ma'lumotlar yetishmayapti.")

    await state.clear()

