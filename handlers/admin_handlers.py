from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, MessageEntity
from aiogram.fsm.context import FSMContext
from pyexpat.errors import messages

from keyboards.admin_kb import get_admin_panel_buttons, get_admin_promos_nav
from keyboards.main_kb import get_main_buttons
from database.models import Promotion
from database.requests import set_promo, get_promo_list, set_promo_activation, update_promo, delete_promo, get_promo

router = Router()


@router.message(F.text == "🛠 Admin paneliga o'tish")
async def cmd_admin_panel(message: Message):
    admin_kb = await get_admin_panel_buttons()
    await message.answer(text="Welcome to Admin panel!", reply_markup=admin_kb)


@router.message(F.text == "🏠 Foydalanuvchi paneliga o'tish")
async def cmd_home_menu(message: Message):
    chat_id = message.from_user.id
    admin_kb = await get_main_buttons(chat_id)
    await message.answer(text="Welcome to User panel!", reply_markup=admin_kb)


# Aksiyalar bo'limi
async def parse_entities(entities_raw):
    if not entities_raw:
        return None
    return [MessageEntity(**e) for e in entities_raw]


async def send_admin_promo_page(message: Message, index: int):
    promos = await get_promo_list()

    if not promos:
        return await message.answer("❌ Aksiyalar mavjud emas.")

    total = len(promos)
    promo_page = None

    if total == 0:
        return await message.answer("❌ Hozircha faol aksiyalar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday aksiya sahifasi mavjud emas.")

    promo = promos[index]
    kb = await get_admin_promos_nav(index=index, total=total)
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


@router.message(F.text == "🎁 Aksiyalar ro'yxati")
async def promos_admin_list(message: Message):
    return await send_admin_promo_page(message, index=0)


@router.callback_query(lambda c: c.data.startswith(("prevAdminPromo_", "nextAdminPromo_")))
async def navigate_posts(callback_query: CallbackQuery):
    action, index, total = callback_query.data.split("_")
    index, total = int(index), int(total)

    if 0 <= index <= total:
        await callback_query.message.delete()

    await callback_query.answer("")
    return await send_admin_promo_page(callback_query.message, index)


@router.callback_query(lambda c: c.data.startswith(("promoActivate_", "promoDeactivate_")))
async def navigate_posts(callback_query: CallbackQuery):
    action, index, promo_id = callback_query.data.split("_")
    index, promo_id = int(index), int(promo_id)

    if action == "promoActivate":
        await set_promo_activation(promo_id, activate=True)
    elif action == "promoDeactivate":
        await set_promo_activation(promo_id, activate=False)

    await callback_query.message.delete()
    await callback_query.answer("")
    return await send_admin_promo_page(callback_query.message, index)


class PromoEditableStates(StatesGroup):
    Edit = State()


@router.callback_query(lambda c: c.data.startswith("promoEdit_"))
async def navigate_posts(callback_query: CallbackQuery, state: FSMContext):
    action, promo_id = callback_query.data.split("_")
    promo_id = int(promo_id)

    await state.update_data(promo_id=promo_id)

    await state.set_state(PromoEditableStates.Edit)
    await callback_query.answer("")
    return await callback_query.message.answer(text="Yangi o'zgartirilgan aksiya matnini yuboring:")


@router.message(PromoEditableStates.Edit)
async def update_promo_in_db(message: Message, state: FSMContext):
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
        return await message.answer(text="Iltimos faqat matn, rasm yoki video ko'rinishidagi xabarlarni yuboring!")

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
    admin_kb = await get_admin_panel_buttons()

    await state.clear()
    return await message.answer("✅ Aksiya saqlandi", reply_markup=admin_kb)



@router.callback_query(lambda c: c.data.startswith("promoDelete_"))
async def navigate_posts(callback_query: CallbackQuery):
    action, promo_id = callback_query.data.split("_")
    promo_id = int(promo_id)

    result = await delete_promo(promo_id)

    if result:
        await callback_query.message.delete()
        await callback_query.answer("")
        return await callback_query.message.answer(text="Xabar muvaffaqiyatli o'chirildi")
    else:
        return await callback_query.message.answer(text="Xabar o'chishida xatolik yuz berdi")


# Aksiya qo'shish
class PromoStates(StatesGroup):
    Waiting_for_promo = State()


@router.message(F.text == "➕ Aksiya qo'shish")
async def get_promo_from_admin(message: Message, state: FSMContext):
    await message.answer(text="Iltimos yangi aksiyani yozib yuboring:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PromoStates.Waiting_for_promo)


@router.message(PromoStates.Waiting_for_promo)
async def save_promo_to_db(message: Message, state: FSMContext):
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
        return await message.answer(text="Iltimos faqat matn, rasm yoki video ko'rinishidagi xabarlarni yuboring!")

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
    admin_kb = await get_admin_panel_buttons()

    await state.clear()
    return await message.answer("✅ Aksiya saqlandi", reply_markup=admin_kb)


