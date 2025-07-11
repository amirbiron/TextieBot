import os
import io
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import pytesseract
from deep_translator import GoogleTranslator
from langdetect import detect

# לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# טוקן מהסביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ברוך הבא לבוט TextieBot!\nשלח לי תמונה עם טקסט ואחזיר לך את הטקסט המזוהה + תרגום.")

# טיפול בתמונה
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))

    text = pytesseract.image_to_string(image, lang='heb+eng').strip()
    if not text:
        await update.message.reply_text("❌ לא זיהיתי טקסט בתמונה.")
        return

    try:
        lang = detect(text)
    except:
        lang = 'unknown'

    if lang == 'he':
        translation = GoogleTranslator(source='auto', target='en').translate(text)
    else:
        translation = GoogleTranslator(source='auto', target='he').translate(text)

    await update.message.reply_text(f"📝 הטקסט שזיהיתי:\n{text}\n\n🌍 תרגום:\n{translation}")

# אתחול הבוט
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

# שרת מדומה עבור Render
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"✅ TextieBot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    logger.info(f"🌐 Dummy HTTP server running on port {port}")
    server.serve_forever()

# הרצה
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server).start()
    main()
