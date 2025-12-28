from aiogram import Router
from aiogram.types import Message
from database import cursor, conn
from constants import WEAPONS
from utils import rank_from_xp

router = Router()

@router.message(lambda m: m.text.startswith("استخدام"))
async def merc(m: Message):
    _, weapon = m.text.split()
    if weapon not in WEAPONS:
        await m.answer("سلاح نامعتبر")
        return

    cursor.execute(
        "SELECT count FROM inventory WHERE user_id=? AND item=?",
        (m.from_user.id, weapon)
    )
    r = cursor.fetchone()
    if not r or r[0] < 1:
        await m.answer("سلاح نداری")
        return

    cursor.execute("SELECT xp FROM users WHERE user_id=?", (m.from_user.id,))
    xp = cursor.fetchone()[0] + 1
    rank = rank_from_xp(xp)

    cursor.execute(
        "UPDATE users SET xp=?, rank=? WHERE user_id=?",
        (xp, rank, m.from_user.id)
    )
    conn.commit()

    await m.answer(f"مزدور استخدام شد +1 XP\nدرجه فعلی: {rank}")
