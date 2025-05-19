import nest_asyncio
nest_asyncio.apply()

import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("6469274617:AAGxZ5U8SP5IcFjFnBRst7MHcI3Huf3_e04")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:100]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men musiqa botiman. Qo‘shiq nomini yuboring 🎵")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"🔍 Qidirilmoqda: '{query}'...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)

            if 'entries' not in info or not info['entries']:
                await update.message.reply_text("❌ Hech narsa topilmadi.")
                return

            video = info['entries'][0]
            title = sanitize_filename(video['title'])
            file_path = f"downloads/{title}.mp3"

            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as audio:
                        await context.bot.send_audio(
                            chat_id=update.effective_chat.id,
                            audio=audio,
                            title=title,
                            performer=query
                        )
                finally:
                    os.remove(file_path)
            else:
                await update.message.reply_text("❌ Kechirasiz, faylni yuklab bo‘lmadi.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik: {str(e)}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    app.run_polling()

if __name__ == '__main__':
    main()
