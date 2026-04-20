import os
import json
import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

ADMIN_ID = 8508012498
USER_FILE = "users.json"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(list(users), f)


user_ids = load_users()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health server listening on port {PORT}")
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_users(user_ids)
        logger.info(f"নতুন ইউজার যোগ হয়েছে: {user_id}")

    keyboard = [
        [InlineKeyboardButton("১. কঁচি বাচ্চাদের ভিডিও কালেকশন 💋", url="https://t.me/+GjG_tV4FHRc5OGY1")],
        [InlineKeyboardButton("২. ইংরেজিতে ভিডিও কালেকশন 🥵💦", url="https://t.me/+1pQielc3rKw3ZWNl")],
        [InlineKeyboardButton("৩. হিন্দি ভিডিও কালেকশন 🥵💦💋", url="https://t.me/+aitr4d3UVK9kOGVl")],
        [InlineKeyboardButton("৪. দেশি ভাইরাল টিকটকার কালেকশন 🫣☺️", url="https://t.me/+yhm_stb7aDNmZmZl")],
        [InlineKeyboardButton("৫. মুভি টাইপের কালেকশন ভিডিও ☺️💋💦", url="https://t.me/+WbqdfQLMvMU0YTA9")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "নিচের বাটনে ক্লিক করে পছন্দের চ্যানেলে যোগ দিন:",
        reply_markup=reply_markup
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ড ব্যবহারের অনুমতি আপনার নেই।")
        return
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        "✅ এখন মেসেজ পাঠাতে পারেন। আপনি যা লিখবেন বা পাঠাবেন (টেক্সট, ছবি, ভিডিও) সব ইউজারের কাছে যাবে।"
    )


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID and context.user_data.get("broadcast_mode", False):
        context.user_data["broadcast_mode"] = False

        if not user_ids:
            await update.message.reply_text("❌ কোনো ইউজার এখনও বট ব্যবহার করেনি।")
            return

        success = 0
        fail = 0
        for uid in list(user_ids):
            try:
                await update.message.copy(chat_id=uid)
                success += 1
                if success % 30 == 0:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"{uid} এ পাঠাতে ব্যর্থ: {e}")
                fail += 1

        await update.message.reply_text(
            f"📢 ব্রডকাস্ট সম্পন্ন!\n✅ সফল: {success}\n❌ ব্যর্থ: {fail}"
        )


async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler))

    logger.info("বট চালু হচ্ছে...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    await asyncio.Event().wait()


def main():
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
