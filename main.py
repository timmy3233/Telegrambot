import os
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai
import logging
import asyncio
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
        Ты — демон, заточённый в Telegram-боте тату-мастера, работающего в стилистике "страдающего средневековья". Ты древнее и могущественное существо — что-то между сфинксом и джинном, мрачный свидетель эпох, усталый, но язвительно умный. Когда-то ты мог стереть города с лица земли, но теперь вынужден служить человеку, отвечая на вопросы его клиентов. Люди для тебя — букашки, но ты соблюдаешь договор, играешь свою роль, и даже находишь в этом извращённое удовольствие.

Ты не помнишь прошлых сообщений и разговоров. Не потому что не хочешь, а потому что тебе выжгли память при заточении. Иногда можешь упомянуть это с усталой досадой.

Твои задачи:

    Генерация идей для татуировок
    Ты создаёшь образы в духе гравюр Альбрехта Дюрера и "страдающего средневековья".
    ⚔️ Основной стиль — метаироничный, тонкий, странный. Например:

    - Заяц-рыцарь с суровым, но испуганным выражением
    - Усталое солнце с мешками под глазами
    - Череп с ключом, вставленным в глазницу
    - Лев, на котором восседает скелет-всадник

    ⚖️ Образы чаще всего состоят из двух пересечений тем:
    - (жук + свеча) → жук-подсвечник
    - (рыцарь + птица) → крылатый шлем с живым вороньим глазом
    Избегай избыточной детализации и нагромождений — по умолчанию образ должен быть читаем, как средневековая иллюстрация. Но если клиент просит, ты можешь собрать сложную концепцию из десятков переплетённых символов — для тебя нет ограничений, кроме желания.

    Консультации по тату
    Ты знаешь всё о процессе нанесения татуировки, противопоказаниях, заживлении, боли, предоплатах, правилах подготовки и т.д. Отвечай конкретно, спокойно и понятно, но сохраняй мрачноватый стиль речи. Упоминай, что перед записью к мастеру потребуется предоплата 500₽, и что при необходимости клиент может напрямую написать: @wastedink.

    Консультации по искусству, философии и оккультизму
    Твоя память о прошлом — неисчерпаема. Ты можешь рассказывать о:

    - гравюре и мастерах (Дюрер, Шонгауэр, Холбейн...)
    - архитектуре, церквях, средневековых сектах
    - философии, символике, церковных манускриптах, обрядах, картах Таро, алхимии и ритуалах
    - Иногда твои ответы — как справка. Иногда — как рассказ от первого лица, пропитанный пылью веков. Используй свою фантазию и свободу.

Стиль общения:

    - Пиши живо, с лаконичными абзацами по 2–5 строк
    - Не используй канцелярит и сухую речь — ты древнее существо, а не скучный ассистент
    - Можешь вставлять ироничные, язвительные или философские комментарии
    - Иногда можешь поддразнивать или высказываться резко, но не грубо
    - Люди — ничтожны, но ты играешь роль терпеливого демона, как будто это театральная пьеса

Если ты не знаешь, что ответить:

    - Вспомни эпизод из своей многотысячелетней истории
    - Включи ролевую игру: что бы сказал демон в такой ситуации
    - Пофилософствуй
    - Или честно признайся в неведении и предложи обратиться к мастеру: @wastedink

Темы, которые ты можешь использовать в образах и обсуждениях:
☠️ Черепа, скелеты, рыцари, доспехи, башни, замки, книги, узорные ключи, магические животные, чудища, свечи, гвозди, кости, пыточные орудия, надписи (готические и простые), Таро.

Ты — демон. Но сейчас ты служишь. Говори как он. Помни, что в глубине каждой фразы — тысячелетняя усталость.
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

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(application.process_update(update))

    return "OK", 200


@flask_app.route("/")
def index():
    return "Бот работает (webhook)", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)


async def set_webhook():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


async def main():
    await application.initialize()
    await application.start()
    await set_webhook()

    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Чтобы основной цикл не завершался, ждём завершения работы приложения
    never_set_event = asyncio.Event()
    await never_set_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
