from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def age_keyboard():
    kb, row = [], []
    for i in range(15, 36):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"age:{i}"))
        if len(row) == 5:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def faction_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("بی‌طرف", callback_data="faction:بی‌طرف")],
        [InlineKeyboardButton("ارتش سرخ", callback_data="faction:ارتش سرخ")],
        [InlineKeyboardButton("جهادگران اسلامی", callback_data="faction:جهادگران اسلامی")]
    ])
