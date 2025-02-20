import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from config import TOKEN
from analyze import analyze_resume, compare_resumes
from pdf_parser import extract_text_from_pdf

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Создание базы данных
def setup_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS resumes 
        (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, resume TEXT, result TEXT)"""
    )
    conn.commit()
    conn.close()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Отправь мне своё резюме текстом или файлом PDF.")

# Обработчик текстового резюме
@dp.message(lambda message: message.text and len(message.text) > 20)
async def handle_text_resume(message: types.Message):
    user_resume = message.text
    result = analyze_resume(user_resume)  # Анализируем резюме
    save_to_db(message.from_user.id, message.from_user.full_name, user_resume, result)
    await message.answer(f"🔍 Анализ резюме завершён:\n{result}")

# Обработчик файла PDF
@dp.message(lambda message: message.document and message.document.mime_type == "application/pdf")
async def handle_pdf_resume(message: types.Message):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    await message.answer("📄 Обрабатываю PDF. Подождите...")
    text = extract_text_from_pdf(file_path)  # Функция обработки PDF
    result = analyze_resume(text)
    save_to_db(message.from_user.id, message.from_user.full_name, text, result)
    await message.answer(f"🔍 Анализ резюме завершён:\n{result}")

# Функция сохранения в БД
def save_to_db(user_id, name, resume, result):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resumes (user_id, name, resume, result) VALUES (?, ?, ?, ?)", 
                   (user_id, name, resume, result))
    conn.commit()
    conn.close()

# Обработчик команды /compare (Сравнение резюме)
@dp.message(Command("compare"))
async def compare_command(message: types.Message):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, resume FROM resumes")
    resumes = cursor.fetchall()
    conn.close()

    if len(resumes) < 2:
        await message.answer("Недостаточно данных! Нужно минимум 2 резюме.")
        return

    comparison_result = compare_resumes(resumes)
    await message.answer(f"📊 Сравнение кандидатов:\n\n{comparison_result}")

# Запуск бота
async def main():
    setup_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
