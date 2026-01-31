import asyncio
from utils.logger import get_logger
from aiogram import Bot, Dispatcher
from settings import TG_BOT_TOKEN

from tg_bot.handlers.quiz import router as quiz_router

logger = get_logger(__name__)


async def main():

    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(quiz_router)

    logger.critical("Tg-бот запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Критическая ошибка при tg-polling:", exc_info=True)
    finally:
        await bot.session.close()
        logger.critical("tg-бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
