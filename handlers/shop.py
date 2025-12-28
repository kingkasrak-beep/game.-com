from aiogram import Router
from aiogram.types import Message
from database import cursor, conn
from constants import WEAPONS, CARS

router = Router()

@router.message(lambda m: m.text.startswith("خرید"))
async def buy(m: Message):
    _, item, count = m.text.split()
    count = int(count)

    if item in WEAPONS:
        price = WEAPONS[item]["price"] * count
    elif item in CARS:
        price = CARS[item] * count
    else:
        await m.answer("ایتم نامعتبر")
        return

    cursor.execute("SELECT money FROM users WHERE user_id=?", (m.from_user.id,))
    money = cursor.fetchone()[0]

    if money < price:
        await m.answer("پول کافی نیست")
        return

    cursor.execute("UPDATE users SET money=? WHERE user_id=?", (money - price, m.from_user.id))
    cursor.execute(
        "INSERT OR IGNORE INTO inventory VALUES (?,?,0)",
        (m.from_user.id, item)
    )
    cursor.execute(
        "UPDATE inventory SET count = count + ? WHERE user_id=? AND item=?",
        (count, m.from_user.id, item)
    )

    conn.commit()
    await m.answer("خرید انجام شد")
