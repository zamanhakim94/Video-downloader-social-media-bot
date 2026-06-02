import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ١. زانیاریێن خۆ ل ڤێرە دابنێ
BOT_TOKEN = "8972651261:AAG5dTiusrnNHhDNwzJ4A1-_dDoVht15M6I"
CHANNEL_USERNAME = "@YourChannelUsername"
SHRINKME_API_KEY = "YOUR_SHRIN1ea3fd2cbac85f80399a1f40ca93c3015d4cb4d7KME_API_KEY" # بچە Tools > API ل ShrinkMe

# فەنکشنا کورتکرنا لینکێ ل سەر ShrinkMe
def shorten_url(long_url):
    try:
        api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={long_url}"
        response = requests.get(api_url).json()
        if response['status'] == 'success':
            return response['shortenedUrl']
    except Exception as e:
        print(f"Error shortening URL: {e}")
    return long_url

# فەنکشنا داگرتن و کورتکرنێ
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # پشکنینا کەنالی
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    if member.status in ['left', 'kicked']:
        await update.message.reply_text("❌ Please join the channel first!")
        return

    url = update.message.text
    status_msg = await update.message.reply_text("⏳ Processing your request...")

    # کورتکرنا لینکێ بەرێ بکارئینەری
    short_link = shorten_url(url)
    
    # فرێکرنا لینکێ کورتکری بۆ بکارئینەری
    await status_msg.edit_text(f"✅ Your download link is ready!\n\nClick here to get the video:\n{short_link}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == '__main__':
    main()