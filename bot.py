# bot.py
import nest_asyncio
nest_asyncio.apply()

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from config import API_TOKEN
from database import create_table
import handlers

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков сообщений
dp.message.register(handlers.cmd_start, Command("start"))
dp.message.register(handlers.cmd_quiz, lambda message: message.text == "Начать игру")
dp.message.register(handlers.cmd_quiz, Command("quiz"))
dp.message.register(handlers.cmd_stats, Command("stats"))

# Регистрация обработчиков callback-запросов
dp.callback_query.register(handlers.handle_answer, lambda callback: callback.data.startswith("answer:"))
dp.callback_query.register(handlers.wrong_answer, lambda callback: callback.data == "wrong_answer")

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
