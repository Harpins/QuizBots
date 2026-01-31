import logging
from telegram_handler import TelegramLoggingHandler

def get_telegram_handler(
    bot_token: str,
    chat_id: str | int,
    level: int = logging.ERROR,
    formatter: logging.Formatter | None = None,
) -> TelegramLoggingHandler:
    """
    Создаёт и настраивает TelegramLoggingHandler для отправки логов в Telegram.
    
    Args:
        bot_token: Токен бота от @BotFather
        chat_id: ID чата или username канала (без @)
        level: Уровень логирования (по умолчанию ERROR)
        formatter: Опциональный форматтер (если None — используется дефолтный)
    
    Returns:
        Настроенный TelegramLoggingHandler
    """
    handler = TelegramLoggingHandler(bot_token, chat_id)
    
    handler.setLevel(level)
    
    if formatter:
        handler.setFormatter(formatter)
    else:
        handler.setFormatter(logging.Formatter(
            "[%(levelname)s] %(asctime)s | %(name)s:%(funcName)s:%(lineno)d\n%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    return handler