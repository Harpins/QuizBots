from utils.redis_client import load_questions_from_json
from utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Начинаем миграцию вопросов из quiz.json в Redis...")
    load_questions_from_json()
    logger.info("Готово! Теперь можно запускать бота.")