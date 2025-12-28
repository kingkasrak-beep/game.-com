from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import is_registered
from states import Register

router = Router()

@router.message(lambda m: m.text == "/start")
async def start(m: Message, state: FSMContext):
    if not is_registered(m.from_user.id):
        await m.answer("نام خود را (انگلیسی/عدد) وارد کنید:")
        await state.set_state(Register.first_name)
    else:
        await m.answer("پنل شما فعال است")
