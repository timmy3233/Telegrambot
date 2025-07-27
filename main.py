import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from google import genai
from google.genai import types
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения (.env)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = "AIzaSyCZHcxs1MPSu9DI5BMOV--Md_qNFzd_amI"

# Initialize Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Привет! Я твой AI-помощник по татуировкам. Задавай вопросы!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_text = update.message.text
        response = await ask_gemini(user_text)
        await update.message.reply_text(response)

async def ask_gemini(prompt: str) -> str:
    try:
        if not gemini_client:
            return "Ошибка: API ключ Gemini не настроен. Обратитесь к администратору."
        
        # Using Gemini 2.5 Flash model for tattoo consultation
        system_prompt = "Ты — тату-мастер-консультант, который помогает клиентам с гравюрными татуировками. Дай краткий профессиональный совет, учитывая стиль, размещение, уход и другие важные аспекты татуировок. Отвечай в 2-3 абзацах максимум."
        
        full_prompt = f"{system_prompt}\n\nВопрос клиента: {prompt}"
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        result = response.text or "Извините, не удалось получить ответ от AI."
        
        # Telegram has a 4096 character limit for messages
        if len(result) > 4000:
            result = result[:3900] + "...\n\n(Ответ сокращен из-за ограничений Telegram)"
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        if "429" in str(e) or "quota" in str(e).lower():
            return "Извините, достигнут лимит запросов к AI. Пожалуйста, попробуйте позже."
        elif "401" in str(e) or "unauthorized" in str(e).lower():
            return "Ошибка авторизации Gemini. Проверьте API ключ."
        else:
            return f"Временная ошибка AI сервиса. Попробуйте позже. Подробности: {e}"



def run_bot():
    """Run the bot in a way that works with existing event loops"""
    if not TELEGRAM_TOKEN:
        logger.error("Токен Telegram не найден. Установите переменную окружения TELEGRAM_TOKEN.")
        return
    
    if not GEMINI_API_KEY:
        logger.warning("API ключ Gemini не найден. Бот будет работать без AI функций.")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Бот запущен...")
    # Use the synchronous version for better compatibility
    app.run_polling()

if __name__ == '__main__':
    run_bot()
