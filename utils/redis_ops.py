import json
import random
import re
from pathlib import Path
from utils.logger import get_logger
from utils.redis_client import get_redis

logger = get_logger(__name__)
redis_db = get_redis()

QUESTIONS_KEY = "quiz:questions"
USER_QUESTION_KEY = "quiz:{platform}:user:{user_id}:current_question"
USED_QUESTIONS_KEY = "quiz:{platform}:user:{user_id}:used"


def strip_html_tags(text: str) -> str:
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text).strip()


def load_questions_from_json(path: str | Path = "quiz.json"):
    """Одноразовая миграция: загружает все вопросы из JSON в Redis"""
    successful = False
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            cleaned_data = {
                strip_html_tags(q): strip_html_tags(a) for q, a in data.items()
            }
        redis_db.hset(QUESTIONS_KEY, mapping=cleaned_data)
        successful = True
        logger.info(f"Загружено {len(cleaned_data)} вопросов в Redis")
    except Exception as err:
        logger.critical(f"Ошибка миграции из JSON в Redis: {err}")
    return successful


def get_all_questions():
    """Возвращает список всех вопросов"""
    return list(redis_db.hkeys(QUESTIONS_KEY))


def get_answer_by_question(question: str):
    """Получить ответ по тексту вопроса"""
    return redis_db.hget(QUESTIONS_KEY, question)


def set_user_current_question(platform: str, user_id: int, question: str, answer: str):
    """Сохраняет текущий вопрос и ответ для пользователя на конкретной платформе"""
    key = USER_QUESTION_KEY.format(platform=platform, user_id=user_id)
    redis_db.hset(key, mapping={"question": question, "answer": answer})


def get_user_current_question(platform: str, user_id: int):
    """Возвращает текущий вопрос и ответ"""
    key = USER_QUESTION_KEY.format(platform=platform, user_id=user_id)
    data = redis_db.hgetall(key)
    return data.get("question"), data.get("answer")


def add_used_question(platform: str, user_id: int, question: str):
    """Добавляет вопрос в использованные для пользователя на платформе"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    redis_db.sadd(key, question)


def get_used_questions(platform: str, user_id: int):
    """Возвращает множество использованных вопросов"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    return redis_db.smembers(key)


def clear_used_questions(platform: str, user_id: int):
    """Очищает использованные вопросы — начать новый круг"""
    key = USED_QUESTIONS_KEY.format(platform=platform, user_id=user_id)
    redis_db.delete(key)


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
