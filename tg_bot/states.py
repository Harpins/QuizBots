from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    """
    Состояния для викторины
    """
    waiting_start = State()          # Пользователь в главном меню, ждёт начала
    waiting_answer = State()         # Задаётся вопрос, ждём выбор варианта
    showing_result = State()         # Показываем правильный/неправильный ответ
    finished = State()               # Викторина завершена