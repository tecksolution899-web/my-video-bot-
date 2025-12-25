import os
import yt_dlp
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7665281312:AAFl3Q71Fz_-A90jDRXHkCkjMTLugAnS3BA'

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("እንኳን መጡ! 🚀 የዩቲዩብ ሊንክ ይላኩ።")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url: return
    status_msg = await update.message.reply_text("⏳ እየወረደ ነው...")
    file_name = f"{update.effective_user.id}.mp4"
    try:
        ydl_opts = {'format': 'best', 'outtmpl': file_name, 'cookiefile': 'cookies.txt', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(file_name, 'rb') as video:
            await update.message.reply_video(video=video, caption="በስኬት ወርዷል! ✅")
        await status_msg.delete()
    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት፦ {str(e)}")
    finally:
        if os.path.exists(file_name): os.remove(file_name)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()
