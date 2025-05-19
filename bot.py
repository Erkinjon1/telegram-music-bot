import nest_asyncio
nest_asyncio.apply()

from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp
import os
from telegram import Update

import logging
logging.basicConfig(level=logging.INFO)

import asyncio
TOKEN = os.getenv("TOKEN")  # Render.env orqali olamiz

async def start(update: Update, context):
    await update.message.reply_text("Salom! Men musiqa botiman. Qo‘shiq nomini yuboring.")

async def search_music(update: Update, context):
    query = update.message.text
    await update.message.reply_text(f"🔎 '{query}' qidirilmoqda...")

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
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                title = video['title']
                file_path = f"downloads/{title}.mp3"

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as audio:
                        await context.bot.send_audio(
                            chat_id=update.effective_chat.id,
                            audio=audio,
                            title=title,
                            performer=video.get('uploader', 'Topildi')
                        )
                    os.remove(file_path)
                else:
                    await update.message.reply_text("Kechirasiz, faylni topib bo‘lmadi.")
            else:
                await update.message.reply_text("Kechirasiz, hech narsa topilmadi.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {str(e)}")

def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    application.run_polling()

if __name__ == '__main__':
    main()
