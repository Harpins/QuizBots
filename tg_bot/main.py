import asyncio
from utils.logger import get_logger
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from settings import (
    TG_BOT_TOKEN,
)
from utils.error_bot import send_error_bot_note

logger = get_logger(__name__)

async def cmd_start(message: types.Message):
    await message.answer("Привет! Просто напиши мне что-нибудь!")


async def main():

    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))

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