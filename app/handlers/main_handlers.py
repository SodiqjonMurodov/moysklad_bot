import asyncio
from datetime import datetime
from typing import Callable, Dict, Any

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from app.core.bot import bot, DEMAND_TEMP_ID, SALESRETURN_TEMP_ID
from app.handlers.admin_handlers import parse_entities
from app.handlers.auth_handlers import Reg
from app.keyboards.admin_kb import get_feedback_answer_btn
from app.keyboards.main_kb import get_main_buttons, get_lang_buttons, get_promos_nav, get_news_nav, get_purchase_history_nav, get_cancel_feedback_button
from app.keyboards.auth_kb import get_phone_request_btn
from app.database.requests import is_user_authenticated, get_user, get_active_promo_list, get_admin_users_list, set_user_lang, get_activate_news_list
from api.counterparty import get_balance_counterparty
from api.demand import get_demands_by_counterparty, get_positions_from_demand
from api.salesreturn import get_salesreturns_by_counterparty, get_positions_from_salesreturn
from api.entities import get_object_by_url, publish_document_with_template
from app.utils.formats import pretty_sum, pretty_datetime
from app.middlewares.i18n import setup_i18n

router = Router()


@router.startup()
async def set_bot_commands():
    _ = await setup_i18n()

    commands = [
        BotCommand(command="start", description="Launch the bot / Запустить бота"),
        BotCommand(command="reg", description="Re-registration / Перерегистрация")
    ]

    await bot.set_my_commands(commands)



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    greeting_text = _("""👋 Assalomu alaykum va Telegram botimizga xush kelibsiz!

Bu bot orqali siz quyidagi bo'limlardan foydalanishingiz mumkin:

ℹ️ Biz haqimizda — kompaniyamiz faoliyati haqida qisqacha ma'lumot
💳 Mening balansim — hisobingizdagi bonuslar va qoldiqni ko'rish
🎁 Aksiyalar — hozirgi chegirmalar va maxsus takliflar
🧾 Xaridlar tarixi — amalga oshirgan xaridlaringiz ro'yxati
📰 Yangiliklar — eng so'nggi yangiliklar va e'lonlar
✍️ Taklif va shikoyatlar — bizga fikr va takliflaringizni yuboring

💚 Oilamizga marhamat!""")
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(_, chat_id)
    print(f"User {chat_id} started the bot.")

    if not await is_user_authenticated(chat_id):
        kb = await get_phone_request_btn(_)
        phone_request_text = _("📞 Iltimos, ro'yxatdan o'tish uchun telefon raqamingizni pastdagi tugmani bosgan holda yuboring:")
        await state.set_state(Reg.phone_number)
        return await message.answer(text=phone_request_text, reply_markup=kb)

    return await message.answer(text=greeting_text, reply_markup=main_kb)


@router.message(F.text.in_([
    "🌐 Tilni o'zgartirish", 
    "🌐 Изменить язык", 
    "🌐 Тілді өзгерту", 
    "🌐 Change language"
    ]))
async def change_user_lang(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    kb = await get_lang_buttons(_)
    return await message.answer(text=_("🌐 Tilni o'zgartirish uchun quyidagi tugmalardan birini tanlang:"), reply_markup=kb)


@router.message(F.text.in_([
    "🇷🇺 Русский",
    "🇬🇧 English",
    "🇺🇿 O'zbekcha",
    "🇰🇿 Қазақша"
]))
async def cmd_set_user_lang(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    chat_id = message.from_user.id

    if message.text == "🇷🇺 Русский":
        lang_code = "ru"
    elif message.text == "🇬🇧 English":
        lang_code = "en"
    elif message.text == "🇺🇿 O'zbekcha":
        lang_code = "uz"
    elif message.text == "🇰🇿 Қазақша":
        lang_code = "kz"
    else:
        return await message.answer(_("❌ Tanlangan til mavjud emas."))

    # Tilni yangilash
    success = await set_user_lang(chat_id, lang_code)
    if success:
        _ = await setup_i18n(lang_code)
        main_kb = await get_lang_buttons(_)
        await message.answer(_("✅ Til muvaffaqiyatli o'zgartirildi."), reply_markup=main_kb)

    

@router.message(F.text.in_([
    "🔙 Orqaga",
    "🔙 Назад",
    "🔙 Back",
    "🔙 Артқа"
    ]))
async def cmd_back(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    chat_id = message.from_user.id
    greeting_text = _("""👋 Assalomu alaykum va Telegram botimizga xush kelibsiz!

Bu bot orqali siz quyidagi bo'limlardan foydalanishingiz mumkin:

ℹ️ Biz haqimizda — kompaniyamiz faoliyati haqida qisqacha ma'lumot
💳 Mening balansim — hisobingizdagi bonuslar va qoldiqni ko'rish
🎁 Aksiyalar — hozirgi chegirmalar va maxsus takliflar
🧾 Xaridlar tarixi — amalga oshirgan xaridlaringiz ro'yxati
📰 Yangiliklar — eng so'nggi yangiliklar va e'lonlar
✍️ Taklif va shikoyatlar — bizga fikr va takliflaringizni yuboring

💚 Oilamizga marhamat!""")
    main_kb = await get_main_buttons(_, chat_id)
    return await message.answer(text=greeting_text, reply_markup=main_kb)


# Biz haqimizda bo'limi
@router.message(F.text.in_([
    "ℹ️ Biz haqimizda", 
    "ℹ️ О нас", 
    "ℹ️ About us", 
    "ℹ️ Біз туралы"
    ]))
async def cmd_about_us(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    about_us_text = _("""<b>ℹ️ Biz haqimizda</b>

Biz — <b>[Sizning kompaniya nomi]</b>, mijozlarimizga yuqori sifatli xizmat va mahsulotlar taqdim etishga intiladigan jamoamiz. 

Kompaniyamiz quyidagi yo'nalishlarda faoliyat yuritadi:
    ✅ Sifatli mahsulotlar savdosi  
    ✅ Mijozlarga sodiqlik tizimi (bonus va chegirmalar)  
    ✅ Onlayn xizmatlar orqali tezkor va qulay xizmat ko'rsatish  

<b>🎯 Bizning maqsadimiz:</b>  
    Har bir mijozga qulaylik yaratish va ishonchli xizmat ko'rsatish orqali uzoq muddatli hamkorlikka erishish.

<b>💡 Biz nimasi bilan ajralib turamiz?</b>  
    • Sifatli xizmat  
    • Tezkor aloqa  
    • Hamyonbop narxlar  
    • Mijozlarga individual yondashuv  

<b>📞 Biz bilan bog'lanish:</b>  
    📱 Telefon: +998 78 113 78 90  
    ✉️ Email: ferrosoft@mail.ru
    📍 Manzil: Buxoro shahri, 5-mikrorayon, A.Jomiy ko'chasi 215 
    🌐 Veb-sayt: www.ferrosoft.uz  
    📱 Telegram: @ferro_soft

<b>💚 Sizga xizmat ko'rsatishdan mamnunmiz!</b>""")
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(_, chat_id)
    await message.answer(text=about_us_text, reply_markup=main_kb)


# Mening balansim bo'limi
@router.message(F.text.in_([
    "💳 Mening balansim", 
    "💳 My balance", 
    "💳 Менің балансым", 
    "💳 Мой баланс"
    ]))
async def cmd_counterparty_balance(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    chat_id = message.from_user.id
    main_kb = await get_main_buttons(_, chat_id)
    user = await get_user(chat_id)
    counterparty = await get_balance_counterparty(counterparty_id=user.api_id)
    my_balance_text = f"""💳 <b>{_("Mening balansim")}</b>

🧑‍💼 <b>{_("F.I.Sh:")}</b> {user.full_name}
📞 <b>{_("Telefon:")}</b> {user.phone_number}

💰 <b>{_("Joriy balans:")}</b> {pretty_sum(amount=counterparty.get("balance"))} {_("so'm")}
🎁 <b>{_("Yig'ilgan bonuslar:")}</b> {pretty_sum(amount=counterparty.get("bonusBalance"))} {_("so'm")}

🛍 <b>{_("Xaridlar soni:")}</b> {counterparty.get("demandsCount")}
💵 <b>{_("Xaridlar summasi:")}</b> {pretty_sum(amount=counterparty.get("demandsSum"))} {_("so'm")}
📆 <b>{_("Oxirgi xarid sanasi:")}</b> {pretty_datetime(counterparty.get("lastDemandDate"))}

🎯 <b>{_("Skidkalar summasi:")}</b> {pretty_sum(amount=counterparty.get("discountsSum"))} {_("so'm")}

↩️ <b>{_("Vozvratlar soni:")}</b> {counterparty.get("returnsCount")}
💸 <b>{_("Vozvratlar summasi:")}</b> {pretty_sum(amount=counterparty.get("returnsSum"))} {_("so'm")}

❗️{_("Agar balansingizda xatolik bo'lsa, operator bilan bog'laning: @ferro_soft")}"""
    await message.answer(text=my_balance_text, reply_markup=main_kb)


# Aksiyalar bo'limi
async def send_promo_page(_: Callable, message: Message, index: int):
    promos = await get_active_promo_list()

    if promos is None:
        return await message.answer(text=_("❌ Hozircha aksiyalar mavjud emas."))

    if not isinstance(index, int):
        return await message.answer(text=_("⚠️ Noto'g'ri sahifa indeksi."))

    total = len(promos)

    if index < 0 or index >= total:
        return await message.answer(text=_("⚠️ Bunday aksiya sahifasi mavjud emas."))

    promo = promos[index]
    kb = await get_promos_nav(_, index, total)
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


@router.message(F.text.in_([
    "🎁 Aksiyalar", 
    "🎁 Акции", 
    "🎁 Акциялар", 
    "🎁 Promotions"
    ]))
async def show_promotions(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    await send_promo_page(_, message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevPromo_", "nextPromo_")))
async def navigate_posts(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_promo_page(_, callback_query.message, index)


# Yangiliklar bo'limi
async def send_new_page(_: Callable, message: Message, index: int):
    news = await get_activate_news_list()

    if news is None:
        return await message.answer(_("❌ Hozircha yangiliklar mavjud emas."))

    if not isinstance(index, int):
        return await message.answer(_("⚠️ Noto'g'ri sahifa indeksi."))

    total = len(news)

    if index < 0 or index >= total:
        return await message.answer(_("⚠️ Bunday aksiya sahifasi mavjud emas."))

    new = news[index]
    kb = await get_news_nav(_, index, total)
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


@router.message(F.text.in_([
    "📰 Yangiliklar", 
    "📰 News", 
    "📰 Жаңалықтар", 
    "📰 Новости"
    ]))
async def show_news(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    await send_new_page(_, message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevNew_", "nextNew_")))
async def navigate_news(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_new_page(_, callback_query.message, index)


# Xaridlar tarixi bo'limi
async def get_sorted_history_data(_: Callable, message: Message):
    """
    Xaridlar tarixini vaqti bo'yicha sortirovkalash

    """
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer(text=_("🔒 Iltimos, ro'yxatdan o'tganingizga ishonch hosil qiling!"))
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


async def send_purchase_history_page(_: Callable, message: Message, sorted_data: list, index: int):
    wait_msg = await message.answer(_("⏳ Iltimos, kuting..."))
    total = len(sorted_data)

    if total == 0:
        return await wait_msg.edit_text(_("❌ Sizda hozircha xaridlar tarixi mavjud emas."))

    if not isinstance(index, int):
        return await wait_msg.edit_text(_("⚠️ Noto'g'ri sahifa indeksi."))

    if index < 0 or index >= total:
        return await wait_msg.edit_text(_("⚠️ Bunday sahifa indeksi mavjud emas."))

    data = sorted_data[index]
    kb = await get_purchase_history_nav(_, index, total)
    positions = []
    doc_type = ""
    publication = {
        "href": "N/B"
    }

    # Dokument turini aniqlash
    if "salesreturn" in data["meta"]["href"]:
        doc_type = _("Vozvrat")
        positions = await get_positions_from_salesreturn(data["id"])
        publication = await publish_document_with_template(
            doc_type="salesreturn",
            doc_id=data["id"],
            template_id=SALESRETURN_TEMP_ID
        )
    elif "demand" in data["meta"]["href"]:
        doc_type = _("Xarid")
        positions = await get_positions_from_demand(data["id"])
        publication = await publish_document_with_template(
            doc_type="demand",
            doc_id=data["id"],
            template_id=DEMAND_TEMP_ID
        )

    strpositions = "" # Dokumentdagi tovarlar ro'yxati
    product_order = 1 # Tovarlarni tartib raqami

    # Valyutasini olish
    currency_url = data["rate"]["currency"]["meta"]["href"]
    currency = await get_object_by_url(currency_url)
    currency = currency['name']

    if positions:
        for position in positions:
            # Mahsulot ma'lumotlarini olish
            product_url = position["assortment"]["meta"]["href"]
            product = await get_object_by_url(product_url)

            # O'lchov birligini olish
            try:
                uomname_url = product["uom"]["meta"]["href"]
                uomname = await get_object_by_url(uomname_url)
                uomname = uomname['name']
            except:
                uomname = ""

            strpositions += f"📌 {product_order}.{product['name']}\n\t\t 🔢 {_('Miqdori')}: {position['quantity']} <i>{uomname}</i>\n\t\t 💰 {_('Narxi')}: {pretty_sum(position['price'])} <i>{currency}</i>\n"
            product_order += 1

            # Skidka borligini tekshirish
            if not position['discount'] == 0:
                position_sum = position['price'] * position['quantity'] * (1 - position['discount'] / 100)
                strpositions += f"\t\t 🎁 {_('Skidka')}: {position['discount']} %\n\t\t 💵 {_('Summa')}: {pretty_sum(position_sum)} <i>{currency}</i>\n\n"
            else:
                strpositions += f"\t\t 💵 {_('Summa')}: {pretty_sum(position['price'] * position['quantity'])} <i>{currency}</i>\n\n"
    history_text = f"""
📃 <b>{doc_type}</b> № {data["name"]}
🕒 <i>{pretty_datetime(data["moment"])}</i>

📦 <b>{_("Tovarlar ro'yxati:")}</b>
{strpositions} 🧾 <b>{_("Umumiy summa:")}</b> {pretty_sum(data["sum"])} <i>{currency}</i>
🔗 <b>{_("Elektron chek:")}</b> {publication['href']}
    """
    return await wait_msg.edit_text(text=history_text, reply_markup=kb)


@router.message(F.text.in_([
    "🧾 Xaridlar tarixi", 
    "🧾 История покупок", 
    "🧾 Сатып алу тарихы", 
    "🧾 Purchase history"
    ]))
async def show_purchase_history(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    sorted_data = await get_sorted_history_data(_, message)
    await state.update_data(sorted_data=sorted_data)
    await send_purchase_history_page(_, message, sorted_data, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevSaleHistory_", "nextSaleHistory_")))
async def navigate_purchase_history(callback_query: CallbackQuery, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    data = await state.get_data()
    sorted_data = data.get("sorted_data", [])

    if not sorted_data:
        return await callback_query.message.answer(_("❌ Sizda hozircha xaridlar tarixi mavjud emas."))

    await callback_query.answer("")
    return await send_purchase_history_page(_, callback_query.message, sorted_data, index)


# Taklif va shikoyatlar bo'limi
class FeedbackStates(StatesGroup):
    AwaitFeedback = State()
    AnswerFeedback = State()


@router.message(F.text.in_([
    "✍️ Taklif va shikoyatlar", 
    "✍️ Suggestions and complaints", 
    "✍️ Ұсыныстар мен шағымдар", 
    "✍️ Предложения и жалобы"
    ]))
async def show_feedback(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    main_kb = await get_cancel_feedback_button(_)
    feedback_request_text = _("""✍️ <b>Taklif va shikoyatlar bo'limi</b>

Sizning fikringiz biz uchun juda muhim!
Iltimos, o'zingizni qiziqtirgan masala, taklif yoki shikoyatingizni shu yerga yozib qoldiring.

📌 Biz barcha xabarlarni diqqat bilan ko'rib chiqamiz va imkon qadar tez orada javob beramiz.""")
    await state.set_state(FeedbackStates.AwaitFeedback)
    await message.answer(text=feedback_request_text, reply_markup=main_kb)


@router.message(FeedbackStates.AwaitFeedback)
async def send_feedback_to_admins(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    admins = await get_admin_users_list()
    feedback_text = message.text
    feedback_entities = message.entities
    user = await get_user(message.from_user.id)
    kb = await get_feedback_answer_btn(_, message_id=message.message_id, chat_id=message.from_user.id)

    if not user:
        await message.answer(text=_("🔒 Iltimos, ro'yxatdan o'tganingizga ishonch hosil qiling!"))
        return None

    if not message.text:
        return await message.answer(_("🔔 Iltimos, faqat matn shaklidagi ma'lumot yuboring!"))

    feedback = f"""<b>📩 {_('Yangi taklif yoki shikoyat')}</b>

<b>📝 {_('Xabar')}:</b>
{feedback_text}

<b>👤 {_('Foydalanuvchi:')}</b> @{message.from_user.username or _("Username yo'q")}
<b>📞 {_('Telefon raqam:')}</b> {user.phone_number}"""

    for admin in admins:
        try:
            await bot.send_message(chat_id=admin.tg_id, text=feedback, entities=feedback_entities, reply_markup=kb)
            await asyncio.sleep(0.05)  # Antiflood uchun kichik pauza (50ms)
        except Exception as e:
            print(f"Xatolik {admin.tg_id} ga yuborishda: {e}")

    await state.clear()
    await message.answer(_("✅ Taklifingiz/shikoyatingiz adminga yuborildi. Rahmat!"),
                         reply_markup=await get_main_buttons(_, message.from_user.id))


@router.callback_query(lambda c: c.data.startswith("feedbackAnswer_"))
async def feedback_answer(_: Callable, callback_query: CallbackQuery, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    action, chat_id, message_id = callback_query.data.split("_")

    # Chat ID va Message ID ni int ga aylantirib olamiz!
    await state.set_state(FeedbackStates.AnswerFeedback)
    await state.update_data(chat_id=int(chat_id), message_id=int(message_id))

    await callback_query.answer()
    await callback_query.message.answer(_("✏️ Foydalanuvchiga javob yozing:"))


@router.message(FeedbackStates.AnswerFeedback)
async def send_feedback_answer_to_user(_: Callable, message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
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
            await message.answer(_("✅ Javob yuborildi."))
        except TelegramBadRequest:
            await message.answer(_("⚠️ Foydalanuvchining chatini topib bo'lmadi. Ehtimol, u botni bloklagan."))
    else:
        await message.answer(_("⚠️ Xabar yuborish uchun ma'lumotlar yetishmayapti."))

    await state.clear()


@router.callback_query(F.data == "cancelFeedbackMessage")
async def cancel_feedback_message(callback_query: CallbackQuery, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    await callback_query.answer()
    await callback_query.message.answer(_("❌ Taklif yoki shikoyat yuborish bekor qilindi."))

