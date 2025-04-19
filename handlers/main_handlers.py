from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_kb import get_main_buttons, get_promos_nav, get_news_nav, get_purchase_history_nav
from keyboards.auth_kb import phone_btn
from db_handlers.db_users import is_user_authenticated, get_user_data
from db_handlers.db_promotions import load_promotions
from db_handlers.db_news import load_news
from handlers.auth_handlers import Reg
from api.counterparty import get_balance_counterparty
from api.demand import get_demands_by_counterparty, get_positions_from_demand
from api.salesreturn import get_salesreturns_by_counterparty, get_positions_from_salesreturn
from api.objects import get_object_by_url

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
    main_kb = await get_main_buttons(chat_id)

    if not await is_user_authenticated(chat_id=int(message.from_user.id)):
        phone_request_text = "📞 Iltimos, ro'yxatdan o'tish uchun telefon raqamingizni pastdagi tugmani bosgan holda yuboring:"
        await state.set_state(Reg.phone_number)
        return await message.answer(text=phone_request_text, reply_markup=phone_btn)

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
    user = await get_user_data(chat_id=message.from_user.id)
    counterparty = await get_balance_counterparty(counterparty_id=str(user.get("counterparty_id")))
    balance_text = f"""
💳 <b>Mening balansim</b>

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
    chat_id = str(message.from_user.id)
    main_kb = await get_main_buttons(chat_id)
    await message.answer(text=balance_text, reply_markup=main_kb)


# Aksiyalar bo'limi
async def send_promo_page(message: Message, index: int):
    promos = await load_promotions()
    total = len(promos)
    if total == 0:
        return await message.answer("❌ Hozircha faol aksiyalar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday aksiya sahifasi mavjud emas.")

    promo = promos[index]
    kb = get_promos_nav(index=index, total=total)
    text = f"""
<b>{promo["title"]}</b>

{promo["description"]}
"""
    return await message.answer_photo(photo=FSInputFile(promo["image"]), caption=text, reply_markup=kb)


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
    news = load_news()
    total = len(news)
    if total == 0:
        return await message.answer("❌ Hozircha yangiliklar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday yangilik sahifasi mavjud emas.")

    new = news[index]
    kb = get_news_nav(index=index, total=total)
    text = f"""
<b>{new["title"]}</b>

{new["description"]}
"""
    return await message.answer_photo(photo=FSInputFile(new["image"]), caption=text, reply_markup=kb)


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
    user = await get_user_data(message.from_user.id)
    if not user:
        return await message.answer(text="Iltimos ro'yxatdan o'tganingizga ishonch hosil qiling")

    demands = await get_demands_by_counterparty(user["counterparty_id"])
    sales_returns = await get_salesreturns_by_counterparty(user["counterparty_id"])
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
    kb = get_purchase_history_nav(index=index, total=total)

    if total == 0:
        await wait_msg.delete()
        return await message.answer("❌ Sizda hozircha xaridlar tarixi mavjud emas.")

    if not isinstance(index, int):
        await wait_msg.delete()
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        await wait_msg.delete()
        return await message.answer("⚠️ Bunday sahifasi mavjud emas.")

    data = sorted_data[index]
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

            strpositions += f"📌 {product_order}.<b>{product['name']}</b>\n\t\t 🔢 Miqdori: {position['quantity']} {uomname['name']}\n\t\t 💰 Narxi: {position['price']} {currency['name']}\n"
            product_order += 1

            # Skidka borligini tekshirish
            if not position['discount'] == 0:
                strpositions += f"\t\t 🎁 Skidka: {position['discount']}\n\n"
            else:
                strpositions += "\n"

    history_text = f"""
📃 <b>{doc_type} №{data["name"]}</b>
🕒 <i>{data["moment"]}</i>

📦 <b>Tovarlar ro'yxati:</b>
{strpositions}
💵 <b>{doc_type}lar summasi:</b> {data["sum"]} {currency["name"]}
    """
    await wait_msg.delete()
    return await message.answer(text=history_text, reply_markup=kb)


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
    await message.answer(text=feedback_txt, reply_markup=main_kb)



