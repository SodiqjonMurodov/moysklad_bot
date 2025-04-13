from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.auth_kb import request_phone_number_button as phone_btn
from keyboards.main_kb import main_buttons
from api.counterparty import create_counterparty, add_counterparty_to_group, check_counterparty_by_phone

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

        await state.update_data(is_authenticated=True, phone=phone)
        await message.answer(text="✅ Siz muvaffaqiyatli avtorizatsiyadan o'tdingiz.", reply_markup=main_buttons)
        await state.clear()
    else:
        await state.update_data(phone=phone)
        await message.answer(text="👤 Endi ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Reg.full_name)


@router.message(Reg.full_name)
async def got_name(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()

    await create_counterparty(name=name, phone=data['phone'])

    await state.update_data(is_authenticated=True, full_name=name)
    await message.answer(text=f"🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz, {name}!", reply_markup=main_buttons)
    await state.clear()
