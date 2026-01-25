import json
import random
from settings import QUESTIONS_FILE

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    QUESTIONS_DB = json.load(f)
QUESTIONS_LIST = list(QUESTIONS_DB.keys())

def get_random_question():
    """Возвращает вопрос и полный ответ (с комментарием)"""
    question_text = random.choice(QUESTIONS_LIST)
    answer_text = QUESTIONS_DB[question_text]
    return question_text, answer_text