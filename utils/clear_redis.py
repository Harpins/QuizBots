from utils.redis_client import r  
from utils.logger import get_logger

logger = get_logger()

keys = r.keys("quiz:*")

if keys:
    r.delete(*keys)
    logger.info(f"Удалено {len(keys)} ключей.")
else:
    logger.info("Ключи викторины не найдены.")

print("Готово! Redis очищен от данных викторины.")