import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения (.env)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой AI-помощник по татуировкам. Задавай вопросы!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = await ask_gpt(user_text)
    await update.message.reply_text(response)

async def ask_gpt(prompt: str) -> str:
    try:
        if not openai_client:
            return "Ошибка: API ключ OpenAI не настроен. Обратитесь к администратору."
        
        # Using GPT-3.5-turbo as requested by the user
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — тату-мастер-консультант, который помогает клиентам с гравюрными татуировками. Дай профессиональный совет, учитывая стиль, размещение, уход и другие важные аспекты татуировок."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Ошибка при обработке запроса: {e}"



def run_bot():
    """Run the bot in a way that works with existing event loops"""
    if not TELEGRAM_TOKEN:
        logger.error("Токен Telegram не найден. Установите переменную окружения TELEGRAM_TOKEN.")
        return
    
    if not OPENAI_API_KEY:
        logger.warning("API ключ OpenAI не найден. Бот будет работать без AI функций.")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Бот запущен...")
    # Use the synchronous version for better compatibility
    app.run_polling()

if __name__ == '__main__':
    run_bot()
