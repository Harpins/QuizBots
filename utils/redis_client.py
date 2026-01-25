import redis
import json
import random
import re
from settings import JSON_PATH, QUESTIONS_FILE
from utils.logger import get_logger

logger = get_logger(__name__)
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

QUESTIONS_KEY = "quiz:questions"
USER_QUESTION_KEY = "quiz:{platform}:user:{user_id}:current_question"
USED_QUESTIONS_KEY = "quiz:{platform}:user:{user_id}:used"

def strip_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def load_questions_from_json():
    """Одноразовая миграция: загружает все вопросы из JSON в Redis"""
    path = QUESTIONS_FILE
    if not path.exists():
        raise FileNotFoundError(f"Файл с {JSON_PATH} не найден")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        cleaned_data = {strip_html_tags(q): strip_html_tags(a) for q, a in data.items()}
    r.hset(QUESTIONS_KEY, mapping=cleaned_data)
    logger.info(f"Загружено {len(cleaned_data)} вопросов в Redis")


def get_all_questions():
    """Возвращает список всех вопросов"""
    return list(r.hkeys(QUESTIONS_KEY))


def get_answer_by_question(question: str):
    """Получить ответ по тексту вопроса"""
    return r.hget(QUESTIONS_KEY, question)


def set_user_current_question(platform: str, user_id: int, question: str, answer: str):
    """Сохраняет текущий вопрос и ответ для пользователя на конкретной платформе"""
    key = USER_QUESTION_KEY.format(platform=platform, user_id=user_id)
    r.hset(key, mapping={"question": question, "answer": answer})


def get_user_current_question(platform: str, user_id: int):
    """Возвращает текущий вопрос и ответ"""
    key = USER_QUESTION_KEY.format(platform=platform, user_id=user_id)
    data = r.hgetall(key)
    return data.get("question"), data.get("answer")


def add_used_question(platform: str, user_id: int, question: str):
    """Добавляет вопрос в использованные для пользователя на платформе"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    r.sadd(key, question)


def get_used_questions(platform: str, user_id: int):
    """Возвращает множество использованных вопросов"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    return r.smembers(key)


def clear_used_questions(platform: str, user_id: int):
    """Очищает использованные вопросы — начать новый круг"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    r.delete(key)


def get_random_unused_question(platform: str, user_id: int):
    """Возвращает случайный неиспользованный вопрос"""
    all_questions = get_all_questions()
    if not all_questions:
        return None, None

    used = get_used_questions(platform, user_id)
    unused = [question for question in all_questions if question not in used]

    if not unused:
        clear_used_questions(platform, user_id)
        unused = all_questions

    question = random.choice(unused)
    answer = get_answer_by_question(question)
    return question, answer


