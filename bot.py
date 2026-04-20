import os
import json
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== কনফিগারেশন ==========
TOKEN = os.environ.get("BOT_TOKEN")   # Render এ environment variable সেট করতে হবে
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

ADMIN_ID = 8508012498        # আপনার টেলিগ্রাম ইউজার আইডি (number)
USER_FILE = "users.json"

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ইউজার আইডি সংরক্ষণ ও লোড
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(list(users), f)

user_ids = load_users()

# ========== কমান্ড হ্যান্ডলার ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start – চ্যানেলের বাটন দেখাবে এবং ইউজারকে লিস্টে যোগ করবে """
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_users(user_ids)
        logger.info(f"নতুন ইউজার যোগ হয়েছে: {user_id}")

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
    """ /admin – শুধুমাত্র অ্যাডমিনের জন্য ব্রডকাস্ট মোড চালু করে """
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ড ব্যবহারের অনুমতি আপনার নেই।")
        return
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        "✅ এখন মেসেজ পাঠাতে পারেন। আপনি যা লিখবেন বা পাঠাবেন (টেক্সট, ছবি, ভিডিও) সব ইউজারের কাছে যাবে।"
    )

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ অ্যাডমিনের পাঠানো মেসেজ সব ইউজারের কাছে ফরওয়ার্ড করে """
    user_id = update.effective_user.id
    # শুধু অ্যাডমিন ও ব্রডকাস্ট মোড অন থাকলেই কাজ করবে
    if user_id == ADMIN_ID and context.user_data.get("broadcast_mode", False):
        # মোড অফ করে দেওয়া, যাতে পরের মেসেজ আবার ব্রডকাস্ট না হয়
        context.user_data["broadcast_mode"] = False

        if not user_ids:
            await update.message.reply_text("❌ কোনো ইউজার এখনও বট ব্যবহার করেনি।")
            return

        success = 0
        fail = 0
        for uid in user_ids:
            try:
                # মূল মেসেজ কপি করে প্রতিটি ইউজারের কাছে পাঠানো
                await update.message.copy(chat_id=uid)
                success += 1
                # রেট লিমিট এড়াতে সামান্য দেরি (প্রতি ৩০ মেসেজে ১ সেকেন্ড)
                if success % 30 == 0:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"{uid} এ পাঠাতে ব্যর্থ: {e}")
                fail += 1

        await update.message.reply_text(
            f"📢 ব্রডকাস্ট সম্পন্ন!\n✅ সফল: {success}\n❌ ব্যর্থ: {fail}"
        )
    else:
        # সাধারণ ইউজারের মেসেজ ইগনোর (বা চাইলে এখানে অন্য রিপ্লাই দিতে পারেন)
        pass

# ========== মেইন ফাংশন (পোলিং) ==========
def main():
    """ বট চালু করা – Polling পদ্ধতি (Render Background Worker এর জন্য উপযুক্ত) """
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler))

    logger.info("বট চালু হচ্ছে...")
    # Polling শুরু – Render এ এটি স্থায়ীভাবে চলবে
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
