import os
import json
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== কনফিগারেশন ==========
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = 8508012498      # আপনার সঠিক ইউজার আইডি দিন (সংখ্যা)
USER_FILE = "users.json"

logging.basicConfig(level=logging.INFO)

# গ্লোবাল ভেরিয়েবল
application = None
user_ids = set()

def load_users():
    global user_ids
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            user_ids = set(json.load(f))
    else:
        user_ids = set()

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(list(user_ids), f)

# ========== বট কমান্ড হ্যান্ডলার ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_users()
        logging.info(f"নতুন ইউজার যোগ হলো: {user_id}")

    keyboard = [
        [InlineKeyboardButton("১. কঁচি বাচ্চাদের ভিডিও কালেকশন 💋", url="https://t.me/+GjG_tV4FHRc5OGY1")],
        [InlineKeyboardButton("২. ইংরেজিতে ভিডিও কালেকশন 🥵💦", url="https://t.me/+1pQielc3rKw3ZWNl")],
        [InlineKeyboardButton("৩. হিন্দি ভিডিও কালেকশন 🥵💦💋", url="https://t.me/+aitr4d3UVK9kOGVl")],
        [InlineKeyboardButton("৪. দেশি ভাইরাল টিকটকার কালেকশন 🫣☺️", url="https://t.me/+yhm_stb7aDNmZmZl")],
        [InlineKeyboardButton("৫. মুভি টাইপের কালেকশন ভিডিও ☺️💋💦", url="https://t.me/+WbqdfQLMvMU0YTA9")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("নিচের বাটনে ক্লিক করে পছন্দের চ্যানেলে যোগ দিন:", reply_markup=reply_markup)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ড ব্যবহারের অনুমতি আপনার নেই।")
        return
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text("✅ এখন মেসেজ পাঠাতে পারেন। আপনি যা লিখবেন বা পাঠাবেন সব ইউজারের কাছে যাবে।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID and context.user_data.get("broadcast_mode", False):
        context.user_data["broadcast_mode"] = False
        success = 0
        fail = 0
        for uid in user_ids:
            try:
                await update.message.copy(chat_id=uid)
                success += 1
            except Exception as e:
                logging.warning(f"{uid} এ পাঠাতে ব্যর্থ: {e}")
                fail += 1
        await update.message.reply_text(f"📢 ব্রডকাস্ট সম্পন্ন!\n✅ সফল: {success}\n❌ ব্যর্থ: {fail}")
    # অন্য ইউজারের মেসেজ ইগনোর

# ========== ফ্লাস্ক ওয়েবহুক ==========
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    global application
    if application is None:
        return "Bot not ready", 500
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK", 200

def setup_bot():
    global application
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    load_users()
    return application

if __name__ == "__main__":
    setup_bot()
    port = int(os.environ.get("PORT", 5000))
    # ওয়েবহুক সেটআপ (Render এ স্বয়ংক্রিয়ভাবে ডোমেইন পাবে)
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')}/{TOKEN}"
    application.bot.set_webhook(webhook_url)
    logging.info(f"ওয়েবহুক সেট করা হয়েছে: {webhook_url}")
    flask_app.run(host="0.0.0.0", port=port)
