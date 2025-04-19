from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.admin_kb import get_admin_panel_buttons, get_admin_promos_nav
from keyboards.main_kb import get_main_buttons
from db_handlers.db_promotions import load_promotions

router = Router()


@router.message(F.text == "🛠 Admin paneliga o'tish")
async def cmd_admin_panel(message: Message):
    admin_kb = await get_admin_panel_buttons()
    await message.answer(text="Welcome to Admin panel!" ,reply_markup=admin_kb)


@router.message(F.text == "🏠 Foydalanuvchi paneliga o'tish")
async def cmd_home_menu(message: Message):
    chat_id = message.from_user.id
    admin_kb = await get_main_buttons(chat_id)
    await message.answer(text="Welcome to User panel!" ,reply_markup=admin_kb)


# Aksiyalar bo'limi
async def send_admin_promo_page(message: Message, index: int):
    promos = await load_promotions(is_active=False)
    promos = list(promos.values())
    total = len(promos)
    if total == 0:
        return await message.answer("❌ Hozircha faol aksiyalar mavjud emas.")

    if not isinstance(index, int):
        return await message.answer("⚠️ Noto‘g‘ri sahifa indeksi.")

    if index < 0 or index >= total:
        return await message.answer("⚠️ Bunday aksiya sahifasi mavjud emas.")

    promo = promos[index]
    kb = get_admin_promos_nav(index=index, total=total, promos=promos)
    text = f"""
<b>{promo["title"]}</b>

{promo["description"]}
"""
    return await message.answer_photo(photo=FSInputFile(promo["image"]), caption=text, reply_markup=kb)


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
    action, index = callback_query.data.split("_")
    index = int(index)

    chat_id = callback_query.from_user.id



    await callback_query.message.delete()

    await callback_query.answer("")
    return await send_admin_promo_page(callback_query.message, index)
