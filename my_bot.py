import os
import yt_dlp
import threading
import http.server
import socketserver
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- ያንተ መረጃዎች ---
TOKEN = '7665281312:AAFl3Q71Fz_-A90jDRXHkCkjMTLugAnS3BA'
CHANNEL_ID = -1003426701331  # ያንተ ቻናል ID
CHANNEL_URL = 'https://t.me/fast_video_save_bot' # የቻናልህ ሊንክ

# Render እንዳይዘጋ Port መክፈቻ
def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# የአባልነት ፍተሻ ተግባር
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # ተጠቃሚው አባል ከሆነ 'member', 'administrator', ወይም 'creator' ይላል
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Membership check error: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("እንኳን መጡ! 🚀 የዩቲዩብ ሊንክ በመላክ ቪዲዮ ማውረድ ይችላሉ።")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. መጀመሪያ አባልነቱን ቼክ እናደርጋለን
    if not await is_user_member(update, context):
        keyboard = [[InlineKeyboardButton("ቻናላችንን ይቀላቀሉ ✅", url=CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ ይቅርታ! ቪዲዮ ለማውረድ መጀመሪያ የቻናላችን አባል መሆን አለብዎት።\n"
            "አባል ለመሆን ከታች ያለውን ቁልፍ ተጭነው ይቀላቀሉ፤ ከዚያ ሊንኩን ድጋሚ ይላኩ።",
            reply_markup=reply_markup
        )
        return

    # 2. አባል ከሆነ ቪዲዮውን ማውረድ ይጀምራል
    url = update.message.text
    if "http" not in url: return

    status_msg = await update.message.reply_text("⏳ እየወረደ ነው...")
    file_name = f"{update.effective_user.id}.mp4"
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': file_name, 'cookiefile': 'cookies.txt', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_name, 'rb') as video:
            await update.message.reply_video(video=video, caption="በስኬት ወርዷል! ✅ @fast_video_save_bot")
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
