import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from llama_cpp import Llama

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загрузка модели: контекст 128 токенов, 1 поток — экономим память
llm = Llama(
    model_path="./model.gguf",
    n_ctx=128,
    n_threads=1,
    verbose=False
)

# Память: user_id -> правильный ответ
user_answers = {}


def generate_qa():
    """Генерирует английский вопрос и ответ через TinyStories."""
    prompt = (
        "Q: The opposite of up is down. A: down.\n"
        "Q: The opposite of big is small. A: small.\n"
        "Q: A cat says meow. A: meow.\n"
        "Q: The opposite of hot is"
    )
    try:
        output = llm(prompt, max_tokens=15, stop=["\n", "Q:"], echo=False)
        text = output["choices"][0]["text"].strip()

        if "A:" in text:
            parts = text.split("A:", 1)
            question = parts[0].replace("Q:", "").strip()
            answer = parts[1].strip()
        else:
            question = "The opposite of cold is"
            answer = "hot"

        if not question.endswith("?"):
            question += "?"

        return f"Fill in the blank: {question}", answer
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        return "Fill in the blank: The opposite of cold is?", "hot"


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    question, correct_answer = generate_qa()
    user_answers[message.from_user.id] = correct_answer
    await message.answer(f"🇬🇧 {question}")


@dp.message()
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_answers:
        await message.answer("Напиши /start, чтобы начать.")
        return

    correct = user_answers[user_id].lower().strip()
    user_text = message.text.lower().strip()

    if correct in user_text or user_text in correct:
        await message.answer(f"✅ Верно! Ответ: {correct}")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {correct}")

    question, new_answer = generate_qa()
    user_answers[user_id] = new_answer
    await message.answer(f"🇬🇧 {question}")


if name == "main":
    dp.run_polling(bot)