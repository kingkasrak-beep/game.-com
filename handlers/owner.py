from aiogram import Router
from aiogram.types import Message
from config import OWNER_ID
from database import cursor, conn

router = Router()

@router.message(lambda m: m.from_user.id == OWNER_ID and m.text.startswith("مالک"))
async def owner(m: Message):
    _, uid, field, value = m.text.split()
    cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, int(uid)))
    conn.commit()
    await m.answer("اعمال شد")
