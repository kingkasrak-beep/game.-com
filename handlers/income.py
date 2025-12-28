from aiogram import Router
from aiogram.types import Message
from database import cursor, conn
import random

router = Router()

@router.message(lambda m: m.text == "دزدی")
async def income(m: Message):
    uid = m.from_user.id

    cursor.execute("SELECT used FROM income WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    used = r[0] if r else 0

    if used >= 3:
        await m.answer("امروز تمومه")
        return

    cursor.execute("SELECT money FROM users WHERE user_id=?", (uid,))
    money = cursor.fetchone()[0]

    if random.choice([True, False]):
        money += 1000
        msg = "+1000 دلار"
    else:
        money -= 100
        msg = "-100 دلار"

    if money < 0:
        cursor.execute("DELETE FROM users WHERE user_id=?", (uid,))
        cursor.execute("DELETE FROM inventory WHERE user_id=?", (uid,))
        cursor.execute("DELETE FROM income WHERE user_id=?", (uid,))
        conn.commit()
        await m.answer("اکانت حذف شد")
        return

    cursor.execute("UPDATE users SET money=? WHERE user_id=?", (money, uid))

    if r:
        cursor.execute("UPDATE income SET used=? WHERE user_id=?", (used + 1, uid))
    else:
        cursor.execute("INSERT INTO income VALUES (?,1)", (uid,))

    conn.commit()
    await m.answer(msg)
