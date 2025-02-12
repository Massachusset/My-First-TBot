from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from quiz_data import quiz_data
from keyboards import generate_options_keyboard
from database import get_quiz_index, update_quiz_index, get_quiz_score, update_quiz_score

# Обработчик callback для выбора ответа
async def handle_answer(callback: types.CallbackQuery):
    # Извлекаем выбранный ответ
    chosen_answer = callback.data.split(":", 1)[1]

    # Удаляем клавиатуру из сообщения
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Выводим выбранный ответ
    await callback.message.answer(f"Вы выбрали: {chosen_answer}")


    # Получаем текущий вопрос и проверяем ответ
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    correct_answer = quiz_data[current_question_index]['options'][correct_option]
    

    if chosen_answer == correct_answer:
        await callback.message.answer("✅ Верно!")
        current_score = await get_quiz_score(user_id)
        await update_quiz_score(user_id, current_score + 1)
    else:
        await callback.message.answer(f"❌ Неправильно. Правильный ответ: {correct_answer}")

    # Переходим к следующему вопросу
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

# Обработчик команды /start
async def cmd_start(message: types.Message):
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Функция для отправки вопроса
async def get_question(message: types.Message, user_id: int):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    opts = question_data['options']
    kb = generate_options_keyboard(opts, opts[question_data['correct_option']])
    await message.answer(question_data['question'], reply_markup=kb)

# Запуск нового квиза
async def new_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

# Обработчик команды /quiz и текст "Начать игру"
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

# Обработчик команды /stats
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    score = await get_quiz_score(user_id)
    await message.answer(f"📊 Ваш последний результат: {score} правильных ответов.")
