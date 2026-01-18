from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    """Основная клавиатура после /start"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="Начать викторину")
    return builder.as_markup(resize_keyboard=True)

