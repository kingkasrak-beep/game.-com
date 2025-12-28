from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import cursor, conn
from states import Register
from keyboards import age_keyboard, faction_keyboard
from constants import STARTER_ITEMS

router = Router()

@router.message(Register.first_name)
async def first(m: Message, state: FSMContext):
    await state.update_data(first_name=m.text)
    await m.answer("نام خانوادگی:")
    await state.set_state(Register.last_name)

@router.message(Register.last_name)
async def last(m: Message, state: FSMContext):
    await state.update_data(last_name=m.text)
    await m.answer("سن را انتخاب کنید:", reply_markup=age_keyboard())
    await state.set_state(Register.age)

@router.callback_query(Register.age, F.data.startswith("age:"))
async def age(c: CallbackQuery, state: FSMContext):
    await state.update_data(age=int(c.data.split(":")[1]))
    await c.message.edit_text("جبهه:", reply_markup=faction_keyboard())
    await state.set_state(Register.faction)

@router.callback_query(Register.faction, F.data.startswith("faction:"))
async def faction(c: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    uid = c.from_user.id
    faction = c.data.split(":")[1]

    cursor.execute("""
    INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,1)
    """, (
        uid, d["first_name"], d["last_name"], d["age"],
        faction, "لس انجلس", 2600, 0,
        "سرباز تازه کار", "تازه کار", "عضو تازه کار", 0
    ))

    for item, count in STARTER_ITEMS.items():
        cursor.execute(
            "INSERT OR IGNORE INTO inventory VALUES (?,?,?)",
            (uid, item, count)
        )

    conn.commit()
    await state.clear()

    await c.message.answer(
        "سلااام!\n\nخوش اومدید به این بازی، این بازی نسخه ی آلفا هست!\n\nممنون از شما"
  )
