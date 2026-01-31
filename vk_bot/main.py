import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import re

from settings import VK_GROUP_TOKEN
from utils.redis_client import (
    get_random_unused_question,
    set_user_current_question,
    add_used_question,
    get_user_current_question,
    clear_used_questions,
)
from vk_bot.keyboards import get_quiz_keyboard
from utils.logger import get_logger
import traceback

logger = get_logger(__name__)

PLATFORM = "vk"

def strip_html_tags(text: str) -> str:
    return re.compile('<.*?>').sub('', text).strip()

def send_new_question(vk, user_id: int, peer_id: int):
    question_raw, answer_raw = get_random_unused_question(PLATFORM, user_id)
    if not question_raw:
        clear_used_questions(PLATFORM, user_id)
        question_raw, answer_raw = get_random_unused_question(PLATFORM, user_id)

    question = strip_html_tags(question_raw)
    answer = strip_html_tags(answer_raw)

    text = f"Вопрос:\n\n{question}"

    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=get_random_id(),
        keyboard=get_quiz_keyboard()
    )

    set_user_current_question(PLATFORM, user_id, question_raw, answer_raw)
    add_used_question(PLATFORM, user_id, question_raw)


def main():
    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        user_id = event.user_id
        peer_id = event.peer_id
        text = (event.text or "").strip()

        if text.lower() in ["/start", "/quiz", "старт", "начать", "привет"]:
            vk.messages.send(
                peer_id=peer_id,
                message="🎓 Добро пожаловать в викторину «Что? Где? Когда?»!\n\n"
                        "Пишите ответ текстом. При ошибке я подскажу.\n"
                        "Если не знаете — жмите «Показать ответ».\nУдачи! 🍀",
                random_id=get_random_id(),
                keyboard=get_quiz_keyboard()
            )
            send_new_question(vk, user_id, peer_id)
            continue

        if text == "Новый вопрос":
            send_new_question(vk, user_id, peer_id)
            continue

        if text == "Показать ответ":
            _, answer_full = get_user_current_question(PLATFORM, user_id)
            if not answer_full:
                continue

            clean_answer = strip_html_tags(answer_full)

            vk.messages.send(
                peer_id=peer_id,
                message=f"Правильный ответ:\n\n{clean_answer}\n\n"
                        "Следующий вопрос уже ниже! 👇",
                random_id=get_random_id(),
                keyboard=get_quiz_keyboard()
            )
            send_new_question(vk, user_id, peer_id)
            continue

        if text:
            current_question, correct_answer_full = get_user_current_question(PLATFORM, user_id)
            if not correct_answer_full:
                continue

            translator = str.maketrans('', '', "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~«»“”‘’")
            user_clean = text.translate(translator).strip().lower()

            without_comment = correct_answer_full.split("\n\nКомментарий:")[0]
            parts = without_comment.split("\n\nЗачет:")
            main = strip_html_tags(parts[0]).translate(translator).strip().lower()
            variants = [main]

            if len(parts) > 1:
                for var in parts[1].split(";"):
                    cleaned = strip_html_tags(var).lstrip("- ").translate(translator).strip().lower()
                    if cleaned:
                        variants.append(cleaned)

            if user_clean in variants:
                vk.messages.send(
                    peer_id=peer_id,
                    message="✅ Отлично! Правильно!\n\nЖмите «Новый вопрос», чтобы продолжить.",
                    random_id=get_random_id(),
                    keyboard=get_quiz_keyboard()
                )
            else:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ Неправильно...\n\nПодумайте ещё раз или нажмите «Показать ответ».",
                    random_id=get_random_id(),
                    keyboard=get_quiz_keyboard()
                )


if __name__ == "__main__":
    vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.critical("VK-бот викторины запущен")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("VK-бот остановлен вручную")
    except Exception as e:
        error_msg = f"Ошибка в VK-боте: {type(e).__name__}: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc()) 
    
