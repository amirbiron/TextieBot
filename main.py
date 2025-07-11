import os
import io
import logging
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import pytesseract
from deep_translator import GoogleTranslator
from langdetect import detect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ברוך הבא לבוט TextieBot!\nשלח לי תמונה עם טקסט ואחזיר לך את הטקסט המזוהה + תרגום.")

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

    # תרגום
    if lang == 'he':
        translation = GoogleTranslator(source='auto', target='en').translate(text)
    else:
        translation = GoogleTranslator(source='auto', target='he').translate(text)

    await update.message.reply_text(f"📝 הטקסט שזיהיתי:
{text}

🌍 תרגום:
{translation}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
