import asyncio
from typing import Callable

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, MessageEntity
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import get_admin_panel_buttons, get_admin_promos_nav, get_admin_news_nav
from app.keyboards.main_kb import get_main_buttons
from app.database.models import Promotion, New
from app.database.requests import (set_promo, get_promo_list, set_promo_activation, update_promo, delete_promo, get_promo,
                                   get_users_list, set_new, get_new_list, set_new_activation, update_new,
                                   delete_new, get_new)

router = Router()


@router.message(F.text.in_([
    "🛠 Admin paneliga o'tish", 
    "🛠 Перейти в панель администратора", 
    "🛠 Әкімші панеліне өтіңіз", 
    "🛠 Go to the admin panel"
    ]))
async def cmd_admin_panel(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    admin_kb = await get_admin_panel_buttons(_)
    await message.answer(text=_("Welcome to Admin panel!"), reply_markup=admin_kb)


@router.message(F.text.in_(["🏠 Foydalanuvchi paneliga o'tish", "🏠 Go to User panel", "🏠 Пайдаланушы панеліне өту", "🏠 Перейти в пользовательскую панель"]))
async def cmd_home_menu(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    chat_id = message.from_user.id
    admin_kb = await get_main_buttons(_, chat_id)
    await message.answer(text=_("Welcome to User panel!"), reply_markup=admin_kb)


async def parse_entities(entities_raw):
    if not entities_raw:
        return None
    return [MessageEntity(**e) for e in entities_raw]


# Aksiyalar bo'limi
class PromoStates(StatesGroup):
    Waiting_for_promo = State()
    Edit = State()

async def send_admin_promo_page(_: Callable, message: Message, index: int):
    promos = await get_promo_list()

    if not promos:
        return await message.answer(_("❌ Aksiyalar mavjud emas."))

    if not isinstance(index, int):
        return await message.answer(_("⚠️ Noto‘g‘ri sahifa indeksi."))

    total = len(promos)
    promo_page = None

    if index < 0 or index >= total:
        return await message.answer(_("⚠️ Bunday aksiya sahifasi mavjud emas."))

    promo = promos[index]
    kb = await get_admin_promos_nav(_, index, total)
    # Parse entities
    entities = await parse_entities(promo.caption_entities)

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
    "🎁 Aksiyalar ro'yxati", 
    "🎁 List of promotions", 
    "🎁 Акциялар тізімі", 
    "🎁 Список акций"
    ]))
async def promos_admin_list(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    return await send_admin_promo_page(_, message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevAdminPromo_", "nextAdminPromo_")))
async def navigate_promo_pages(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_admin_promo_page(_, callback_query.message, index)


@router.callback_query(lambda c: c.data.startswith(("promoActivate_", "promoDeactivate_")))
async def activate_deactivate_promo(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, promo_id = callback_query.data.split("_")
    index, promo_id = int(index), int(promo_id)

    if action == "promoActivate":
        await set_promo_activation(promo_id, activate=True)
    elif action == "promoDeactivate":
        await set_promo_activation(promo_id, activate=False)

    await callback_query.message.delete()
    await callback_query.answer("")
    return await send_admin_promo_page(_, callback_query.message, index)


@router.callback_query(lambda c: c.data.startswith("promoEdit_"))
async def edit_promo(callback_query: CallbackQuery, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    action, promo_id = callback_query.data.split("_")
    promo_id = int(promo_id)

    await state.update_data(promo_id=promo_id)
    await callback_query.answer("")
    await callback_query.message.answer(text=_("📝 Iltimos, yangi o'zgartirilgan aksiya matnini yuboring!"))
    await state.set_state(PromoStates.Edit)


@router.message(PromoStates.Edit)
async def update_promo_in_db(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    data = await state.get_data()
    promo_id = data.get("promo_id")
    file_id = None

    if message.text:
        content_type = "text"
        caption = message.text
        entities = message.entities
    elif message.photo:
        file_id = message.photo[-1].file_id
        content_type = "photo"
        caption = message.caption
        entities = message.caption_entities
    elif message.video:
        file_id = message.video.file_id
        content_type = "video"
        caption = message.caption
        entities = message.caption_entities
    else:
        await state.clear()
        await state.set_state(PromoStates.Waiting_for_promo)
        return await message.answer(text=_("📄 Iltimos, faqat matn, rasm yoki video ko'rinishidagi xabar yuboring!"))

    if content_type != "text":
        await update_promo(
            promo_id=promo_id,
            query=Promotion(
                content_type=content_type,
                caption=caption,
                file_id=file_id,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    else:
        await update_promo(
            promo_id=promo_id,
            query=Promotion(
                content_type=content_type,
                caption=caption,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    admin_kb = await get_admin_panel_buttons(_)

    await state.clear()
    return await message.answer(_("✅ Aksiya saqlandi"), reply_markup=admin_kb)


@router.callback_query(lambda c: c.data.startswith("promoDelete_"))
async def delete_promo_from_db(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, promo_id = callback_query.data.split("_")
    promo_id = int(promo_id)

    result = await delete_promo(promo_id)

    if result:
        await callback_query.message.delete()
        await callback_query.answer("")
        return await callback_query.message.answer(text=_("✅ Xabar muvaffaqiyatli o'chirildi!"))
    else:
        return await callback_query.message.answer(text=_("❌ Xabarni o'chirishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring!"))


@router.callback_query(lambda c: c.data.startswith("promoShare_"))
async def share_promo_to_users(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, promo_id = callback_query.data.split("_")
    promo = await get_promo(int(promo_id))
    users = await get_users_list()

    for user in users:
        try:
            if promo.content_type == "text":
                await callback_query.bot.send_message(
                    chat_id=user.tg_id,
                    text=promo.caption,
                    entities=promo.caption_entities
                )
                await asyncio.sleep(0.05)
            elif promo.content_type == "photo":
                await callback_query.bot.send_photo(
                    chat_id=user.tg_id,
                    photo=promo.file_id,
                    caption=promo.caption,
                    caption_entities=promo.caption_entities
                )
                await asyncio.sleep(0.05)
            elif promo.content_type == "video":
                await callback_query.bot.send_video(
                    chat_id=user.tg_id,
                    video=promo.file_id,
                    caption=promo.caption,
                    caption_entities=promo.caption_entities
                )
                await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Xatolik {user.tg_id} ga yuborishda: {e}")

    await callback_query.answer("")
    return await callback_query.message.answer(
        text=_("✅ Xabar barcha foydalanuvchilarga muvaffaqiyatli yuborildi!"))


# Aksiya qo'shish
@router.message(F.text.in_([
    "➕ Aksiya qo'shish", 
    "➕ Добавить акцию", 
    "➕ Акция қосу", 
    "➕ Add promotion"
    ]))
async def get_promo_from_admin(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    await message.answer(text=_("📝 Iltimos, yangi aksiyani yozib yuboring:"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(PromoStates.Waiting_for_promo)


@router.message(PromoStates.Waiting_for_promo)
async def save_promo_to_db(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    file_id = None

    if message.text:
        content_type = "text"
        caption = message.text
        entities = message.entities
    elif message.photo:
        file_id = message.photo[-1].file_id
        content_type = "photo"
        caption = message.caption
        entities = message.caption_entities
    elif message.video:
        file_id = message.video.file_id
        content_type = "video"
        caption = message.caption
        entities = message.caption_entities
    else:
        await state.clear()
        await state.set_state(PromoStates.Waiting_for_promo)
        return await message.answer(text=_("⚠️ Iltimos faqat matn, rasm yoki video ko'rinishidagi xabarlarni yuboring!"))

    if content_type != "text":
        await set_promo(
            Promotion(
                content_type=content_type,
                caption=caption,
                file_id=file_id,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    else:
        await set_promo(
            Promotion(
                content_type=content_type,
                caption=caption,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    admin_kb = await get_admin_panel_buttons(_)

    await state.clear()
    return await message.answer(_("✅ Aksiya saqlandi"), reply_markup=admin_kb)


# Yangiliklar bo'limi
class NewStates(StatesGroup):
    Waiting_for_new = State()
    Edit = State()


async def send_admin_new_page(_: Callable, message: Message, index: int):
    news = await get_new_list()

    if not news:
        return await message.answer(_("❌ Yangiliklar mavjud emas."))

    if not isinstance(index, int):
        return await message.answer(_("⚠️ Noto‘g‘ri sahifa indeksi."))

    new_page = None
    total = len(news)

    if index < 0 or index >= total:
        return await message.answer(_("⚠️ Bunday aksiya sahifasi mavjud emas."))

    new = news[index]
    kb = await get_admin_news_nav(_, index, total)
    # Parse entities
    entities = await parse_entities(new.caption_entities)

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
    "📰 Yangiliklar ro'yxati", 
    "📰 List of news", 
    "📰 Жаңалықтар тізімі", 
    "📰 Список новостей"
    ]))
async def news_admin_list(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    return await send_admin_new_page(_, message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevAdminNew_", "nextAdminNew_")))
async def navigate_new_pages(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_admin_new_page(_, callback_query.message, index)


@router.callback_query(lambda c: c.data.startswith(("newActivate_", "newDeactivate_")))
async def activate_deactivate_new(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, index, new_id = callback_query.data.split("_")
    index, new_id = int(index), int(new_id)

    if action == "newActivate":
        await set_new_activation(new_id, activate=True)
    elif action == "newDeactivate":
        await set_new_activation(new_id, activate=False)

    await callback_query.message.delete()
    await callback_query.answer("")
    return await send_admin_new_page(_, callback_query.message, index)


@router.callback_query(lambda c: c.data.startswith("newEdit_"))
async def edit_new(callback_query: CallbackQuery, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    action, new_id = callback_query.data.split("_")
    new_id = int(new_id)

    await state.update_data(new_id=new_id)

    await state.set_state(NewStates.Edit)
    await callback_query.answer("")
    return await callback_query.message.answer(text=_("📝 Iltimos, o'zgartirilgan yangilik matnini yuboring!"))


@router.message(NewStates.Edit)
async def update_new_in_db(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    data = await state.get_data()
    new_id = data.get("new_id")
    file_id = None

    if message.text:
        content_type = "text"
        caption = message.text
        entities = message.entities
    elif message.photo:
        file_id = message.photo[-1].file_id
        content_type = "photo"
        caption = message.caption
        entities = message.caption_entities
    elif message.video:
        file_id = message.video.file_id
        content_type = "video"
        caption = message.caption
        entities = message.caption_entities
    else:
        await state.clear()
        await state.set_state(NewStates.Waiting_for_new)
        return await message.answer(text=_("📄 Iltimos, faqat matn, rasm yoki video ko'rinishidagi xabar yuboring!"))

    if content_type != "text":
        await update_new(
            new_id=new_id,
            query=New(
                content_type=content_type,
                caption=caption,
                file_id=file_id,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    else:
        await update_new(
            new_id=new_id,
            query=New(
                content_type=content_type,
                caption=caption,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    admin_kb = await get_admin_panel_buttons(_)

    await state.clear()
    return await message.answer(_("✅ Yangilik saqlandi"), reply_markup=admin_kb)


@router.callback_query(lambda c: c.data.startswith("newDelete_"))
async def delete_new_from_db(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, new_id = callback_query.data.split("_")
    new_id = int(new_id)

    result = await delete_new(new_id)

    if result:
        await callback_query.message.delete()
        await callback_query.answer("")
        return await callback_query.message.answer(text=_("✅ Xabar muvaffaqiyatli o'chirildi!"))
    else:
        return await callback_query.message.answer(text=_("❌ Xabarni o'chirishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring!"))


@router.callback_query(lambda c: c.data.startswith("newShare_"))
async def share_new_to_users(callback_query: CallbackQuery, **kwargs):
    _ = kwargs["_"]
    action, new_id = callback_query.data.split("_")
    new = await get_new(int(new_id))
    users = await get_users_list()

    for user in users:
        try:
            if new.content_type == "text":
                await callback_query.bot.send_message(
                    chat_id=user.tg_id,
                    text=new.caption,
                    entities=new.caption_entities
                )
                await asyncio.sleep(0.05)
            elif new.content_type == "photo":
                await callback_query.bot.send_photo(
                    chat_id=user.tg_id,
                    photo=new.file_id,
                    caption=new.caption,
                    caption_entities=new.caption_entities
                )
                await asyncio.sleep(0.05)
            elif new.content_type == "video":
                await callback_query.bot.send_video(
                    chat_id=user.tg_id,
                    video=new.file_id,
                    caption=new.caption,
                    caption_entities=new.caption_entities
                )
                await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Xatolik {user.tg_id} ga yuborishda: {e}")

    await callback_query.answer("")
    return await callback_query.message.answer(
        text=_("✅ Xabar barcha foydalanuvchilarga muvaffaqiyatli yuborildi!"))


# Yangilik qo'shish
@router.message(F.text.in_([
    "➕ Yangilik qo'shish", 
    "➕ Добавить новость", 
    "➕ Жаңалық қосу", 
    "➕ Add news"
    ]))
async def get_new_from_admin(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    await state.clear()
    await message.answer(text=_("📝 Iltimos yangilikni yozib yuboring:"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(NewStates.Waiting_for_new)


@router.message(NewStates.Waiting_for_new)
async def save_new_to_db(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    file_id = None

    if message.text:
        content_type = "text"
        caption = message.text
        entities = message.entities
    elif message.photo:
        file_id = message.photo[-1].file_id
        content_type = "photo"
        caption = message.caption
        entities = message.caption_entities
    elif message.video:
        file_id = message.video.file_id
        content_type = "video"
        caption = message.caption
        entities = message.caption_entities
    else:
        await state.clear()
        await state.set_state(NewStates.Waiting_for_new)
        return await message.answer(text=_("⚠️ Iltimos faqat matn, rasm yoki video ko'rinishidagi xabarlarni yuboring!"))

    if content_type != "text":
        await set_new(
            New(
                content_type=content_type,
                caption=caption,
                file_id=file_id,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    else:
        await set_new(
            New(
                content_type=content_type,
                caption=caption,
                caption_entities=[e.model_dump() for e in (entities or [])]
            )
        )
    admin_kb = await get_admin_panel_buttons(_)

    await state.clear()
    return await message.answer(_("✅ Yangilik saqlandi"), reply_markup=admin_kb)


