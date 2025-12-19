# main.py - نسخه نهایی با مالک ثابت

import os
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# توکن از محیط
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("متغیر محیطی API_TOKEN تنظیم نشده!")

# آیدی مالک ثابت (تغییر نکن مگر اینکه واقعاً بخوای عوض کنی)
OWNER_ID = 6321580395

# تنظیم لاگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل ثبت‌نام
FIRST_NAME, LAST_NAME, AGE = range(3)

# راه‌اندازی دیتابیس
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            is_owner INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()

# چک فارسی بودن متن
def is_persian(text: str) -> bool:
    if not text.strip():
        return False
    return all(0x0600 <= ord(char) <= 0x06FF or char in " \u200C" for char in text.strip())

# کاربر ثبت‌نام کرده؟
def is_registered(user_id: int) -> bool:
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

# گرفتن اطلاعات کاربر
def get_user_data(user_id: int):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, age, is_owner, is_admin FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result

# چک کردن مالک بودن (بر اساس آیدی ثابت)
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # ثبت اولیه کاربر در دیتابیس
    if not is_registered(user_id):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (user_id, username, is_owner) VALUES (?, ?, ?)",
            (user_id, user.username or "None", 1 if is_owner(user_id) else 0),
        )
        conn.commit()
        conn.close()

        welcome_text = "🌟 خوش اومدی!\n"
        if is_owner(user_id):
            welcome_text += "تو مالک اصلی ربات هستی 👑\n"

        welcome_text += "برای استفاده از ربات در گروه، باید ثبت‌نام کنی.\n\nلطفاً اسم واقعی‌ت رو فقط به فارسی بنویس:"

        await update.message.reply_text(welcome_text)
        return FIRST_NAME

    # اگر قبلاً ثبت‌نام کرده
    user_data = get_user_data(user_id)
    if not user_data or not all(user_data[:3]):
        await update.message.reply_text("ثبت‌نامت ناتمامه! دوباره شروع کن:\nاسم واقعی‌ت رو به فارسی بنویس:")
        return FIRST_NAME

    first_name, last_name, age, db_is_owner, is_admin = user_data
    role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if is_admin else "🎮 بازیکن"

    await update.message.reply_text(
        f"سلام {first_name} {last_name} عزیز!\nنقش: {role}\n\n"
        "در گروه از دستور /panel استفاده کن تا پنل شخصی‌ت رو ببینی.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# بقیه توابع ثبت‌نام (first_name_handler, last_name_handler, age_handler) بدون تغییر
# ... (همون کدهای قبلی رو کپی کن)

async def first_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not is_persian(text):
        await update.message.reply_text("❌ اسم باید فقط با حروف فارسی باشه! دوباره بنویس:")
        return FIRST_NAME
    context.user_data["first_name"] = text
    await update.message.reply_text("عالی ✅ حالا فامیلی‌ت رو به فارسی بنویس:")
    return LAST_NAME

async def last_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not is_persian(text):
        await update.message.reply_text("❌ فامیلی باید فقط با حروف فارسی باشه! دوباره بنویس:")
        return LAST_NAME
    context.user_data["last_name"] = text

    keyboard = []
    for start in range(15, 41, 5):
        row = [InlineKeyboardButton(str(age), callback_data=f"age_{age}") for age in range(start, min(start + 5, 41))]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("حالا سنت رو انتخاب کن (۱۵ تا ۴۰ سال):", reply_markup=reply_markup)
    return AGE

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    age = int(query.data.split("_")[1])
    user_id = query.from_user.id

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "UPDATE users SET first_name = ?, last_name = ?, age = ? WHERE user_id = ?",
        (context.user_data["first_name"], context.user_data["last_name"], age, user_id),
    )
    conn.commit()
    conn.close()

    role = "👑 مالک" if is_owner(user_id) else "🎮 بازیکن"

    await query.edit_message_text(
        f"✅ ثبت‌نام با موفقیت تموم شد!\n\n"
        f"نام: {context.user_data['first_name']} {context.user_data['last_name']}\n"
        f"سن: {age} سال\n"
        f"نقش: {role}\n\n"
        "حالا می‌تونی در گروه از /panel استفاده کنی!"
    )
    return ConversationHandler.END

# دستور /panel
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("❌ اول باید در پی‌وی ربات با /start ثبت‌نام کنی!")
        return

    user_data = get_user_data(user_id)
    if not user_data or not all(user_data[:3]):
        await update.message.reply_text("❌ اطلاعاتت کامل نیست! در پی‌وی /start بزن.")
        return

    first_name, last_name, age, _, is_admin = user_data
    role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if is_admin else "🎮 بازیکن"

    keyboard = [[InlineKeyboardButton("📊 پروفایل من", callback_data="profile")]]
    if is_owner(user_id):
        keyboard.append([InlineKeyboardButton("➕ اضافه کردن ادمین", callback_data="add_admin_start")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎮 پنل شخصی {first_name} {last_name}\n\n"
        f"سن: {age} سال\n"
        f"نقش: {role}\n\n"
        "انتخاب کن:",
        reply_markup=reply_markup,
    )

# هندلر دکمه‌ها (فقط بخش مالک چک با is_owner)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "profile":
        user_data = get_user_data(user_id)
        if user_data:
            first_name, last_name, age, _, is_admin = user_data
            role = "👑 مالک" if is_owner(user_id) else "🛡️ ادمین" if is_admin else "🎮 بازیکن"
            await query.edit_message_text(
                f"📊 پروفایل شما:\n\n"
                f"نام: {first_name} {last_name}\n"
                f"سن: {age} سال\n"
                f"نقش: {role}"
            )

    elif query.data == "add_admin_start":
        if not is_owner(user_id):
            await query.edit_message_text("❌ فقط مالک می‌تونه ادمین اضافه کنه!")
            return
        await query.edit_message_text(
            "کاربری که می‌خوای ادمین بشه رو فوروارد کن یا آیدی عددی‌ش رو بفرست:\n"
            "/cancel برای انصراف"
        )
        return "AWAITING_ADMIN"

# حالت انتظار ادمین (چک مالک با is_owner)
async def awaiting_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/cancel":
        await update.message.reply_text("عملیات لغو شد.")
        return ConversationHandler.END

    if not is_owner(update.effective_user.id):
        return

    target_id = None
    if update.message.forward_from:
        target_id = update.message.forward_from.id
    elif update.message.text and update.message.text.isdigit():
        target_id = int(update.message.text)

    if target_id and is_registered(target_id):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (target_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ کاربر با آیدی {target_id} حالا ادمینه!")
    else:
        await update.message.reply_text("❌ کاربر پیدا نشد یا ثبت‌نام نکرده. دوباره امتحان کن یا /cancel بزن.")

    return ConversationHandler.END

def main():
    init_db()
    application = Application.builder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name_handler)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name_handler)],
            AGE: [CallbackQueryHandler(age_handler, pattern=r"^age_\d+$")],
        },
        fallbacks=[],
        per_message=False,
    )

    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^add_admin_start$")],
        states={
            "AWAITING_ADMIN": [MessageHandler(filters.FORWARD | (filters.TEXT & ~filters.COMMAND), awaiting_admin_id)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    application.add_handler(conv_handler)
    application.add_handler(admin_conv)
    application.add_handler(CommandHandler("panel", panel))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^profile$"))

    port = int(os.getenv("PORT", 10000))
    webhook_url = os.getenv("RENDER_EXTERNAL_URL", "https://your-bot-name.onrender.com")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=API_TOKEN,
        webhook_url=f"{webhook_url.rstrip('/')}/{API_TOKEN}",
    )

if __name__ == "__main__":
    main()
