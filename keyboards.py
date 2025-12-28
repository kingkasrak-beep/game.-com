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
        [InlineKeyboardButton(text="بی‌طرف", callback_data="faction:neutral")],
        [InlineKeyboardButton(text="ارتش سرخ", callback_data="faction:red")],
        [InlineKeyboardButton(text="جهادگران اسلامی", callback_data="faction:jihad")]
    ])


def main_panel(is_owner=False):
    kb = [
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
        [InlineKeyboardButton(text="💰 درآمد", callback_data="income")]
    ]
    if is_owner:
        kb.append([InlineKeyboardButton(text="👑 پنل مالک", callback_data="owner")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
