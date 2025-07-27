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
        await send_long_message(update.message, response)

async def send_long_message(message, text: str):
    """Send a message, splitting it if it's too long for Telegram"""
    max_length = 4000
    
    if len(text) <= max_length:
        await message.reply_text(text)
    else:
        # Split the message into chunks
        chunks = []
        current_chunk = ""
        
        # Split by sentences to avoid breaking mid-sentence
        sentences = text.split('. ')
        
        for sentence in sentences:
            if len(current_chunk + sentence + '. ') <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Send each chunk
        for i, chunk in enumerate(chunks):
            if i == 0:
                await message.reply_text(chunk)
            else:
                await message.reply_text(f"(продолжение {i+1})\n\n{chunk}")

async def ask_gemini(prompt: str) -> str:
    try:
        if not gemini_client:
            return "Ошибка: API ключ Gemini не настроен. Обратитесь к администратору."
        
        # Using Gemini 2.5 Flash model for tattoo consultation
        system_prompt = "Ты опытный и дружелюбный тату мастер, который много лет делает татуировки в стиле гравюры. Давай простые и короткие, но емкие ответы, дели сообщения на легко читаемые небольшие абзацы."
        
        full_prompt = f"{system_prompt}\n\nВопрос клиента: {prompt}"
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        return response.text or "Извините, не удалось получить ответ от AI."
        
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
