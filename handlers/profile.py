from aiogram import Router
from aiogram.types import Message
from database import cursor

router = Router()

@router.message(lambda m: m.text == "پروفایل")
async def profile(m: Message):
    uid = m.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    u = cursor.fetchone()

    cursor.execute("SELECT item,count FROM inventory WHERE user_id=?", (uid,))
    inv = "\n".join([f"{i} × {c}" for i, c in cursor.fetchall()])

    await m.answer(f"""
نام: {u[1]}
نام خانوادگی: {u[2]}
سن: {u[3]}
جبهه: {u[4]}
درجه: {u[8]}
لقب: {u[9]}
شهر: {u[5]}
پول: {u[6]}$
XP: {u[7]}

دارایی:
{inv}
""")
