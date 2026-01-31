import sys
import json
import random
import argparse
from utils.redis_client import redis_db, load_questions_from_json
from utils.logger import get_logger
from settings import QUESTIONS_FILE

logger = get_logger(__name__)

def migrate_json_to_redis():
    logger.info("Начинаем миграцию вопросов из quiz.json в Redis...")
    migrated = load_questions_from_json()
    if migrated:
        logger.info("Готово! Теперь можно запускать бота.")
    return
    
def clear_redis():
    keys = redis_db.keys("quiz:*")
    if keys:
        redis_db.delete(*keys)
        logger.info(f"Готово! Redis очищен от данных викторины. Удалено {len(keys)} ключей.")
    else:
        logger.info("Ключи викторины не найдены.")
    return 

def get_random_question():
    path = QUESTIONS_FILE
    with open(path, "r", encoding="utf-8") as f:
        questions_db = json.load(f)
        questions_list = list(questions_db.keys())
    
    question_text = random.choice(questions_list)
    answer_text = questions_db[question_text]
    return question_text, answer_text


def main():
    parser = argparse.ArgumentParser(
        description="Утилита для управления данными викторины",
        epilog="Пример:\n"
               "  python helpers.py migrate\n"
               "  python helpers.py clear --confirm\n",
    )

    subparsers = parser.add_subparsers(
        dest="command",          
        required=True,           
        help="Доступные команды"
    )

    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Мигрировать вопросы из JSON в Redis",
        description="Загружает данные викторины из .json файла в Redis"
    )
    
    clear_parser = subparsers.add_parser(
        "clear",
        help="Очистить Redis от данных викторины",
        description="Удаляет все ключи, связанные с викториной"
    )
    clear_parser.add_argument(
        "--confirm", "-y",
        action="store_true",
        help="Подтвердить очистку без запроса (для скриптов)"
    )

    args = parser.parse_args()

    if args.command == "migrate":
        migrate_json_to_redis() 

    elif args.command == "clear":
        if not args.confirm:
            logger.warning("Вы действительно хотите полностью очистить данные викторины в Redis?")
            logger.warning("Это действие НЕОБРАТИМО. Продолжить? [y/N]")
            if input().strip().lower() not in ("y", "yes"):
                logger.info("Отмена.")
                sys.exit(0)
        clear_redis()          

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
