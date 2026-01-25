from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quiz_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Новый вопрос", callback_data="new_question")],
        [InlineKeyboardButton(text="Показать ответ", callback_data="show_answer")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)