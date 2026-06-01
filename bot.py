import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Setup basic logging to see updates in your terminal
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = '8972651261:AAG5dTiusrnNHhDNwzJ4A1-_dDoVht15M6I'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and gives simple instructions."""
    await update.message.reply_text(
        "👋 Welcome! Send me any public video link (YouTube, TikTok, Instagram, etc.), "
        "and I will try to fetch it and send it right back to you!"
    )

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Intercepts text messages, treats them as URLs, and downloads/uploads the media."""
    url = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("⚡ Processing link... Please wait.")
    
    # Configure yt-dlp configuration settings
    output_template = os.path.join('downloads', f'{chat_id}_%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Prioritize standard MP4 format for clean Telegram previews
        'outtmpl': output_template,
        'max_filesize': 50 * 1024 * 1024, # Cap at 50MB to honor default Telegram Bot API constraints
        'quiet': True
    }
    
    # Ensure storage folder exists
    os.makedirs('downloads', exist_ok=True)
    
    try:
        await status_msg.edit_text("📥 Downloading video file from source...")
        
        # yt-dlp is synchronous; run it safely inside a threadpool executor to avoid locking the bot
        loop = asyncio.get_event_loop()
        
        def run_ytdl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
        file_path = await loop.run_in_executor(None, run_ytdl)
        
        # Safety fallback check for minor extension variations (e.g., mkv vs mp4 conversions)
        if not os.path.exists(file_path):
            downloaded_files = [os.path.join('downloads', f) for f in os.listdir('downloads') if f.startswith(str(chat_id))]
            if downloaded_files:
                file_path = downloaded_files[0]
            else:
                raise FileNotFoundError("Target download payload not found.")

        await status_msg.edit_text("📤 Uploading media to Telegram servers...")
        
        # Upload file natively back to the Telegram message window
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="Done! Enjoy your video! 🎬")
            
        # Housekeeping: delete the local file after successful transfer
        os.remove(file_path)
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Process error: {e}")
        error_str = str(e)
        
        if "File size extension" in error_str or "too large" in error_str:
            await status_msg.edit_text("❌ The video file exceeds 50MB. Default bots cannot upload files larger than 50MB.")
        else:
            await status_msg.edit_text("❌ Failed to process URL. Make sure the link is correct and publicly viewable.")
            
        # Clean up any fragmented file artifacts on crash
        for file in os.listdir('downloads'):
            if file.startswith(str(chat_id)):
                try: os.remove(os.path.join('downloads', file))
                except: pass

def main():
    """Initializes the polling engine."""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers for start commands and generic text streams
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))
    
    print("Bot is initializing polling sequence...")
    app.run_polling()

if __name__ == '__main__':
    main()