from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def age_keyboard():
    kb = []
    row = []
    for i in range(15, 36):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"age_{i}"))
        if len(row) == 5:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def faction_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="بی‌طرف", callback_data="faction_neutral")],
        [InlineKeyboardButton(text="ارتش سرخ", callback_data="faction_red")],
        [InlineKeyboardButton(text="جهادگران اسلامی", callback_data="faction_jihad")]
    ])


def main_panel(is_owner=False):
    buttons = [
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
        [InlineKeyboardButton(text="🛒 فروشگاه", callback_data="shop")],
        [InlineKeyboardButton(text="🪖 استخدام مزدور", callback_data="mercenary")],
        [InlineKeyboardButton(text="💰 درآمد", callback_data="income")]
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton(text="👑 پنل مالک", callback_data="owner")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
