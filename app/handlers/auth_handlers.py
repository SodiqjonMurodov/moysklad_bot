from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from typing import Callable

from app.keyboards.auth_kb import get_phone_request_btn
from app.keyboards.main_kb import get_main_buttons
from api.counterparty import create_counterparty, add_counterparty_to_group, check_counterparty_by_phone
from app.database.requests import is_user_authenticated, create_user
from app.database.models import User

router = Router()


class Reg(StatesGroup):
    full_name = State()
    phone_number = State()


@router.message(Command("reg"))
async def cmd_registration(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    kb = await get_phone_request_btn(_)
    phone_request_text = _("📞 Iltimos, telefon raqamingizni pastdagi tugmani bosgan holda yuboring:")
    await state.set_state(Reg.phone_number)
    await message.answer(text=phone_request_text, reply_markup=kb)


@router.message(F.contact, Reg.phone_number)
async def got_phone(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    phone = message.contact.phone_number
    counterparty = await check_counterparty_by_phone(phone)
    tag_name = "Telebot"

    if counterparty:
        existing_tags = counterparty.get("tags", [])

        if tag_name not in existing_tags:
            await add_counterparty_to_group(counterparty, tag_name)

        chat_id = message.from_user.id
        main_kb = await get_main_buttons(_, chat_id)

        await state.update_data(phone_number=phone)
        is_user_auth = await is_user_authenticated(chat_id)

        if not is_user_auth:
            user_data = User(
                tg_id=chat_id,
                api_id=counterparty.get("id", ""),
                full_name=counterparty.get("name", ""),
                phone_number=message.contact.phone_number
            )
            await create_user(query=user_data)
        await message.answer(text=_("🎉 Siz ro'yxatdan muvaffaqiyatli o'tdingiz."), reply_markup=main_kb)
        await state.clear()
    else:
        await state.update_data(phone_number=phone)
        await message.answer(text=_("👤 Endi to'liq ism va familiyangizni kiriting:"), reply_markup=ReplyKeyboardRemove())
        await state.set_state(Reg.full_name)


@router.message(Reg.full_name)
async def got_name(message: Message, state: FSMContext, **kwargs):
    _ = kwargs["_"]
    name = message.text
    data = await state.get_data()
    chat_id = message.from_user.id

    counterparty = await create_counterparty(name=name, phone=data['phone_number'])
    if counterparty is None:
        await message.answer(text=_("❌ Ro'yxatdan o'tishda xatolik yuz berdi, iltimos qayta urinib ko'ring!"), reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(full_name=name)
        user_data = User(
            tg_id=chat_id,
            api_id=counterparty.get("id", ""),
            full_name=counterparty.get("name", ""),
            phone_number=data['phone_number']
        )
        await create_user(query=user_data)
        main_kb = await get_main_buttons(_, chat_id)
        await message.answer(text=_("🎉 Siz ro'yxatdan muvaffaqiyatli o'tdingiz."), reply_markup=main_kb)
    await state.clear()

