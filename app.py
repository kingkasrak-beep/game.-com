# app.py - کاملاً سازگار با Python 3.13.4 و python-telegram-bot 21.5

import os
import sqlite3
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# توکن ربات از متغیر محیطی (روی Render تنظیم می‌شه)
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("متغیر محیطی API_TOKEN تنظیم نشده! در Render اضافه کن.")

# آیدی مالک ثابت - فقط این کاربر مالکه
OWNER_ID = 6321580395

# تنظیم لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# مراحل ثبت‌نام
FIRST_NAME, LAST_NAME, AGE = range(3)

# راه‌اندازی دیتابیس
def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                is_owner INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        """)

# چک کردن فارسی بودن متن
def is_persian(text: str) -> bool:
    if not text or not (clean := text.strip()):
        return False
    return all(0x0600 <= ord(c) <= 0x06FF or c in " \u200C" for c in clean)

# توابع کمکی دیتابیس
def is_registered(user_id: int) -> bool:
    with sqlite3.connect("users.db") as conn:
        return conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone() is not None

def get_user_data(user_id: int):
    with sqlite3.connect("users.db") as conn:
        return conn.execute(
            "SELECT first_name, last_name, age, is_owner, is_admin FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# دستور /start - ثبت‌نام در پی‌وی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    if not is_registered(user_id):
        with sqlite3.connect("users.db") as conn:
            conn.execute(
                "INSERT INTO users (user_id, username, is_owner) VALUES (?, ?, ?)",
                (user_id, update.effective_user.username or "None", 1 if is_owner(user_id) else 0),
            )

        msg = "🌟 خوش اومدی!\n"
        if is_owner(user_id):
            msg += "تو مالک اصلی ربات هستی 👑\n"
        msg += "برای بازی در گروه باید ثبت‌نام کنی.\n\nاسم واقعی‌ت رو فقط به فارسی بنویس:"
        await update.message.reply_text(msg)
        return FIRST_NAME

    data = get_user_data(user_id)
    if not data or not all(data[:3]):
        await update.message.reply_text("ثبت‌نامت ناتمامه! دوباره اسم رو به فارسی بنویس:")
        return FIRST_NAME

    first, last, age, _, admin = data
    role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if admin else "🎮 بازیکن"
    await update.message.reply_text(
        f"سلام {first} {last}!\nنقش: {role}\n\nدر گروه از /panel استفاده کن.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def first_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_persian(update.message.text):
        await update.message.reply_text("❌ فقط حروف فارسی مجاز است! دوباره بنویس:")
        return FIRST_NAME
    context.user_data["first_name"] = update.message.text.strip()
    await update.message.reply_text("عالی! حالا فامیلی‌ت رو به فارسی بنویس:")
    return LAST_NAME

async def last_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_persian(update.message.text):
        await update.message.reply_text("❌ فقط حروف فارسی مجاز است! دوباره بنویس:")
        return LAST_NAME
    context.user_data["last_name"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton(str(a), callback_data=f"age_{a}") for a in range(s, min(s + 5, 41))]
        for s in range(15, 41, 5)
    ]
    await update.message.reply_text("سن خودت رو انتخاب کن (۱۵ تا ۴۰ سال):", reply_markup=InlineKeyboardMarkup(keyboard))
    return AGE

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    age = int(query.data.split("_")[1])
    user_id = query.from_user.id

    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "UPDATE users SET first_name = ?, last_name = ?, age = ? WHERE user_id = ?",
            (context.user_data["first_name"], context.user_data["last_name"], age, user_id),
        )

    role = "👑 مالک" if is_owner(user_id) else "🎮 بازیکن"
    await query.edit_message_text(
        f"✅ ثبت‌نام با موفقیت انجام شد!\n\n"
        f"نام: {context.user_data['first_name']} {context.user_data['last_name']}\n"
        f"سن: {age} سال\n"
        f"نقش: {role}\n\n"
        f"حالا برو تو گروه و دستور /panel رو بزن!"
    )
    return ConversationHandler.END

# دستور /panel - پنل شخصی در گروه
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("❌ اول در پی‌وی ربات /start بزن و ثبت‌نام کن!")
        return

    data = get_user_data(user_id)
    if not data or not all(data[:3]):
        await update.message.reply_text("❌ اطلاعاتت کامل نیست! در پی‌وی ثبت‌نام کن.")
        return

    first, last, age, _, admin = data
    role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if admin else "🎮 بازیکن"

    keyboard = [[InlineKeyboardButton("📊 پروفایل من", callback_data="profile")]]
    if is_owner(user_id):
        keyboard.append([InlineKeyboardButton("➕ اضافه کردن ادمین", callback_data="add_admin_start")])

    await update.message.reply_text(
        f"🎮 پنل شخصی {first} {last}\n\nسن: {age} سال\nنقش: {role}\n\nانتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# هندلر دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "profile":
        data = get_user_data(user_id)
        first, last, age, _, admin = data
        role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if admin else "🎮 بازیکن"
        await query.edit_message_text(
            f"📊 پروفایل شما:\n\nنام: {first} {last}\nسن: {age} سال\nنقش: {role}"
        )

    elif query.data == "add_admin_start":
        if not is_owner(user_id):
            await query.edit_message_text("❌ فقط مالک می‌تونه ادمین اضافه کنه!")
            return
        await query.edit_message_text(
            "کاربری که می‌خوای ادمین بشه رو فوروارد کن یا آیدی عددی‌ش رو بفرست:\n/cancel برای انصراف"
        )
        return "AWAITING_ADMIN"

# اضافه کردن ادمین
async def awaiting_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.lower() == "/cancel":
        await update.message.reply_text("عملیات لغو شد.")
        return ConversationHandler.END

    if not is_owner(update.effective_user.id):
        return ConversationHandler.END

    target_id = update.message.forward_from.id if update.message.forward_from else None
    if not target_id and update.message.text and update.message.text.isdigit():
        target_id = int(update.message.text)

    if target_id and is_registered(target_id):
        with sqlite3.connect("users.db") as conn:
            conn.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (target_id,))
        await update.message.reply_text(f"✅ کاربر با آیدی {target_id} حالا ادمینه!")
    else:
        await update.message.reply_text("❌ کاربر ثبت‌نام نکرده یا پیدا نشد. دوباره امتحان کن یا /cancel بزن.")

    return ConversationHandler.END

# تابع اصلی اجرا
async def main():
    init_db()

    app = Application.builder().token(API_TOKEN).build()

    # هندلرهای ثبت‌نام
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name_handler)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name_handler)],
            AGE: [CallbackQueryHandler(age_handler, pattern=r"^age_\d+$")],
        },
        fallbacks=[],
    ))

    # هندلر اضافه کردن ادمین
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^add_admin_start$")],
        states={"AWAITING_ADMIN": [MessageHandler(filters.FORWARD | filters.TEXT, awaiting_admin)]},
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    ))

    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^profile$"))

    # شروع webhook
    await app.initialize()
    await app.start()

    port = int(os.getenv("PORT", 10000))
    webhook_url = os.getenv("RENDER_EXTERNAL_URL", "https://your-service-name.onrender.com")

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=API_TOKEN,
        webhook_url=f"{webhook_url.rstrip('/')}/{API_TOKEN}",
    )

    logger.info("ربات با موفقیت شروع شد و آنلاینه 🚀")
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
