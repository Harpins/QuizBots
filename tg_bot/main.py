import asyncio
from utils.logger import get_logger
from aiogram import Bot, Dispatcher
from settings import TG_BOT_TOKEN
from utils.error_bot import send_error_bot_note

from tg_bot.handlers.quiz import router as quiz_router

logger = get_logger(__name__)


async def main():

    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(quiz_router)

    logger.info("Бот запущен")
    await send_error_bot_note(f"tg-бот запущен", False)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Критическая ошибка при tg-polling:", exc_info=True)
        await send_error_bot_note(f"Критическая ошибка при polling tg-бота: {e}")
    finally:
        await bot.session.close()
        stop_message = "tg-бот остановлен"
        logger.info(stop_message)
        await send_error_bot_note(stop_message, False)


if __name__ == "__main__":
    asyncio.run(main())
