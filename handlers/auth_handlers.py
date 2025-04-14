from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.auth_kb import request_phone_number_button as phone_btn
from keyboards.main_kb import main_buttons
from api.counterparty import create_counterparty, add_counterparty_to_group, check_counterparty_by_phone
from db_handlers.db_users import is_user_authenticated, set_user_authenticated

router = Router()


class Reg(StatesGroup):
    full_name = State()
    phone_number = State()


@router.message(Command("reg"))
async def cmd_start(message: Message, state: FSMContext):
    phone_request_text = "📞 Iltimos, telefon raqamingizni pastdagi tugmani bosgan holda yuboring:"
    await state.set_state(Reg.phone_number)
    await message.answer(text=phone_request_text, reply_markup=phone_btn)


@router.message(F.contact, Reg.phone_number)
async def got_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    counterparty = await check_counterparty_by_phone(phone)
    tag_name = "Telebot"

    if counterparty:
        existing_tags = counterparty.get("tags", [])

        if tag_name not in existing_tags:
            await add_counterparty_to_group(counterparty, tag_name)

        chat_id = message.from_user.id
        await state.update_data(phone_number=phone)
        is_user_auth = await is_user_authenticated(chat_id)

        if not is_user_auth:
            user_data = {
                "full_name": counterparty.get("name", ""),
                "phone_number": message.contact.phone_number
            }
            await set_user_authenticated(chat_id=chat_id, user_data=user_data)
        await message.answer(text="🎉 Siz ro'yxatdan muvaffaqiyatli o'tdingiz.", reply_markup=main_buttons)
        await state.clear()
    else:
        await state.update_data(phone_number=phone)
        await message.answer(text="👤 Endi ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Reg.full_name)


@router.message(Reg.full_name)
async def got_name(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    chat_id = message.from_user.id

    result = await create_counterparty(name=name, phone=data['phone_number'])
    if result is None:
        await message.answer(text=f"❌ Ro'yxatdan o'tishda xatolik yuz berdi, iltimos qayta urinib ko'ring!", reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(full_name=name)
        user_data = {
            "full_name": name,
            "phone_number": data['phone_number']
        }
        await set_user_authenticated(chat_id=chat_id, user_data=user_data)
        await message.answer(text=f"🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz, {name}!", reply_markup=main_buttons)
    await state.clear()
