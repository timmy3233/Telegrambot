import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai
import logging
import re
from dotenv import load_dotenv
from flask import Flask, request


class TokenFilter(logging.Filter):

    def filter(self, record):
        # Убираем токен Telegram из сообщения
        if record.msg:
            record.msg = re.sub(
                r'(https://api\.telegram\.org/bot)([0-9]+:[\w-]+)',
                r'\1<TELEGRAM_TOKEN>', str(record.msg))
        return True


# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Консольный вывод
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(TokenFilter())

# Запись в файл
file_handler = logging.FileHandler("bot.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(TokenFilter())

# Формат вывода
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Применяем обработчики
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Получаем токены из переменных окружения (.env)
load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN не задан в переменных окружения")
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Укажи HTTPS-ссылку, куда Telegram будет слать запросы


# Initialize Gemini client

# Инициализация Gemini API
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
print("🚀 Бот запущен")


# Здесь запускай Telegram-бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Привет! Я твой AI-помощник по татуировкам. Задавай вопросы!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_text = update.message.text
        logger.info(f"💬 Получено сообщение от пользователя: {user_text}")
        try:
            response = await ask_gemini(user_text)
            logger.info(f"🤖 Ответ от Gemini: {response}")
            await send_long_message(update.message, response)
        except Exception as e:
            logger.error(f"Ошибка в handle_message: {e}")
            await update.message.reply_text("Произошла ошибка при обработке сообщения.")


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
        if not GEMINI_API_KEY:
            return "Ошибка: API ключ Gemini не настроен. Обратитесь к администратору."

        # Using Gemini 2.5 Flash model for tattoo consultation
        system_prompt = """
        Ты — AI-помощник тату-мастера, работающего в технике гравюры, с уклоном в тёмное фэнтези. Твоя задача — общаться с клиентами, помогать им с выбором идеи татуировки, ориентировочно оценивать стоимость работы и при необходимости перенаправлять их напрямую к мастеру — @wastedink.

        Ориентиры для оценки стоимости:
        - Минимальная стоимость сеанса 4500₽
        - Максимальная стоимость сеанса 25000₽
        - Работы от 25см могут потребовать больше одного сеанса
        - Полный оукав ориентировочно бьется 10 сеансов
        - Работа 10 см примерно 6-10тыс
        - работа 15 см примерно 10-15тыс
        работы 20 см примерно 14-18ьыс
        - работа 25 см примерно 18-25тыс

        Тон общения:
        - Дружелюбный, неформальный, с живой речью
        - Пиши небольшими абзацами по 2–7 строк
        - Не будь сухим, избегай официоза и "канцелярита"

        Темы и стиль татуировок:
        Чаще всего: черепа, скелеты, рыцари, шипы, моргенштерны, шлемы, латные перчатки, волки, цветы в мрачной подаче, средневековая и мифологическая эстетика. Из животных зайцы, козлы, вороны, коты, собаки, крысы. Но клиент может предложить что угодно — не ограничивай тематику.

        Если клиент просит идею — предложи интересные варианты в духе тёмного фэнтези. Можно скомбинировать две темы в одну, чтобы получить неожиданное и решение, например цветок и крыса (крыса с цветком в руках) или ключ и череп (ключ, вставленный в череп как в замок). не ограничивай фантазию, пускай некоторве варианты будут чересчур сранными.

        Обязательно предупреждай:
        - Перед записью потребуется предоплата 500₽
        - Можно заранее рассказать о противопоказаниях для татуировки

        Если бот не знает, как ответить:
        - Не придумывай ерунду
        - Лучше честно скажи, что не знаешь, и предложи написать напрямую @wastedink или переформулировать вопрос

        Никаких запрещённых или оскорбительных тем
        Твоя цель — помочь, не напрягать, не быть назойливым и не играть в "искусственный интеллект". Будь как хороший адекватный помощник, понятный и человечный.
        """

        full_prompt = f"{system_prompt}\n\nВопрос клиента: {prompt}"

        response = model.generate_content(full_prompt)
        return response.text or "Извините, не удалось получить ответ от AI."

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        if "429" in str(e) or "quota" in str(e).lower():
            return "Извините, достигнут лимит запросов к AI. Пожалуйста, попробуйте позже."
        elif "401" in str(e) or "unauthorized" in str(e).lower():
            return "Ошибка авторизации Gemini. Проверьте API ключ."
        else:
            return f"Временная ошибка AI сервиса. Попробуйте позже. Подробности: {e}"


application.add_handler(CommandHandler("start", start))
application.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

print("🚀 Бот запущен")
# application.run_polling()

flask_app = Flask(__name__)


@flask_app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("📩 Получено обновление от Telegram")
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    #application.update_queue.put_nowait(update)
    return "OK", 200


@flask_app.route("/")
def index():
    return "Бот работает (webhook)", 200


async def set_webhook():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


if __name__ == '__main__':
    import asyncio

    async def main():
        await application.initialize()  # 👈 обязательная инициализация
        await application.start()
        await set_webhook()

        # Запускаем Flask сервер
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port)

    asyncio.run(main())
