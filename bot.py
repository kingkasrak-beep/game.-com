import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import API_TOKEN, OWNER_ID
from database import cursor, conn, is_registered
from states import Register
from keyboards import age_keyboard, faction_keyboard, main_panel
from utils import calculate_rank

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_registered(user_id):
        await message.answer("نام خود را (انگلیسی و عدد) وارد کنید:")
        await state.set_state(Register.first_name)
        return

    await message.answer(
        "به پنل خود خوش آمدید",
        reply_markup=main_panel(user_id == OWNER_ID)
    )


@dp.message(Register.first_name)
async def reg_first(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("نام خانوادگی را وارد کنید:")
    await state.set_state(Register.last_name)


@dp.message(Register.last_name)
async def reg_last(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("سن خود را انتخاب کنید:", reply_markup=age_keyboard())
    await state.set_state(Register.age)


@dp.callback_query(Register.age, F.data.startswith("age_"))
async def reg_age(call: CallbackQuery, state: FSMContext):
    age = int(call.data.split("_")[1])
    await state.update_data(age=age)
    await call.message.edit_text("جبهه خود را انتخاب کنید:", reply_markup=faction_keyboard())
    await state.set_state(Register.faction)


@dp.callback_query(Register.faction)
async def reg_faction(call: CallbackQuery, state: FSMContext):
    faction_map = {
        "faction_neutral": "بی‌طرف",
        "faction_red": "ارتش سرخ",
        "faction_jihad": "جهادگران اسلامی"
    }

    data = await state.get_data()
    uid = call.from_user.id

    cursor.execute("""
    INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        data["first_name"],
        data["last_name"],
        data["age"],
        faction_map[call.data],
        "لس انجلس",
        2600,
        0,
        "سرباز تازه کار",
        "تازه کار",
        "عضو تازه کار",
        0,
        1
    ))

    starter_items = {
        "ژ3": 10,
        "تیر ژ3": 100,
        "پراید 98": 1,
        "خانه آپارتمانی": 1
    }

    for item, count in starter_items.items():
        cursor.execute("INSERT INTO inventory VALUES (?, ?, ?)", (uid, item, count))

    conn.commit()
    await state.clear()

    await call.message.answer(
        "سلااام!\n\n"
        "خوش اومدید به این بازی، این بازی نسخه ی آلفا هست!\n\n"
        "ممنون از شما",
        reply_markup=main_panel(uid == OWNER_ID)
    )


@dp.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    uid = call.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    u = cursor.fetchone()

    cursor.execute("SELECT item, count FROM inventory WHERE user_id=?", (uid,))
    inv = cursor.fetchall()

    inv_text = "\n".join([f"- {i[0]} × {i[1]}" for i in inv])

    text = f"""
👤 پروفایل

نام: {u[1]}
نام خانوادگی: {u[2]}
سن: {u[3]}
موقعیت: {u[10]}
جبهه: {u[4]}
درجه: {u[8]}
لقب: {u[9]}
شهر: {u[5]}
پول: {u[6]}$
XP: {u[7]}

دارایی:
{inv_text}

افتخارات: {u[11]}
"""
    await call.message.answer(text)


@dp.callback_query(F.data == "income")
async def income(call: CallbackQuery):
    uid = call.from_user.id

    cursor.execute("SELECT count FROM income_log WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    count = r[0] if r else 0

    if count >= 3:
        await call.message.answer("امروز بیشتر از این نمی‌تونی دزدی کنی!")
        return

    success = random.choice([True, False])

    cursor.execute("SELECT money FROM users WHERE user_id=?", (uid,))
    money = cursor.fetchone()[0]

    if success:
        money += 1000
        msg = "دزدی موفق بود 💰 +1000 دلار"
    else:
        money -= 100
        msg = "گیر افتادی ❌ -100 دلار"

    if money < 0:
        cursor.execute("DELETE FROM users WHERE user_id=?", (uid,))
        cursor.execute("DELETE FROM inventory WHERE user_id=?", (uid,))
        cursor.execute("DELETE FROM income_log WHERE user_id=?", (uid,))
        conn.commit()
        await call.message.answer("اکانت شما حذف شد! دوباره ثبت‌نام کنید.")
        return

    cursor.execute("UPDATE users SET money=? WHERE user_id=?", (money, uid))

    if r:
        cursor.execute("UPDATE income_log SET count=? WHERE user_id=?", (count+1, uid))
    else:
        cursor.execute("INSERT INTO income_log VALUES (?, ?)", (uid, 1))

    conn.commit()
    await call.message.answer(msg)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
