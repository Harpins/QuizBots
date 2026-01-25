from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.redis_client import (
    get_random_unused_question,
    set_user_current_question,
    get_user_current_question,
    get_all_questions,
    add_used_question,
    get_used_questions,
)
from tg_bot.keyboards import get_quiz_keyboard
from tg_bot.states import QuizStates

router = Router()

PLATFORM = "tg"


async def send_new_question(target: Message | CallbackQuery, state: FSMContext):
    user_id = target.from_user.id
    platform = PLATFORM

    question, answer = get_random_unused_question(platform, user_id)

    if not question:
        text = "Ошибка: вопросы не загрузились."
    else:
        text = f"<b>Вопрос:</b>\n\n{question}"

        set_user_current_question(platform, user_id, question, answer)
        add_used_question(platform, user_id, question)

    total_questions = len(get_all_questions())
    used_count = len(get_used_questions(platform, user_id))

    if used_count == total_questions and total_questions > 0:
        prefix = (
            "🎉 <b>Поздравляем!</b>\nВы прошли все вопросы!\nНачинаем новый круг:\n\n"
        )
        final_text = prefix + text
    else:
        final_text = text

    if isinstance(target, Message):
        await target.answer(
            final_text, reply_markup=get_quiz_keyboard(), parse_mode="HTML"
        )
    else:
        await target.message.edit_text(
            final_text, reply_markup=get_quiz_keyboard(), parse_mode="HTML"
        )

    await state.set_state(QuizStates.playing)


@router.message(F.text.in_({"/start", "/quiz"}))
async def cmd_quiz_start(message: Message, state: FSMContext):
    await message.answer("Начинаем викторину")
    await send_new_question(message, state)


@router.message(QuizStates.playing, F.text)
async def check_answer(message: Message, state: FSMContext):
    platform = PLATFORM
    user_id = message.from_user.id
    _, correct_answer_full = get_user_current_question(platform, user_id)

    if not correct_answer_full:
        await message.answer("Вопрос потерялся... Нажмите «Новый вопрос»")
        return

    user_answer = message.text.strip()

    if "\n\nКомментарий:" in correct_answer_full:
        without_comment = correct_answer_full.split("\n\nКомментарий:")[0]
    else:
        without_comment = correct_answer_full

    parts = without_comment.split("\n\nЗачет:")
    main_answer = parts[0].strip()
    variants = [main_answer]

    if len(parts) > 1:
        extra = parts[1].strip()
        for var in extra.split(";"):
            cleaned = var.strip().lstrip("- ").strip()
            if cleaned:
                variants.append(cleaned)
                
    user_lower = user_answer.lower()
    
    correct_variants_clean = [var.lower().rstrip(".") for var in variants]

    if user_lower in correct_variants_clean:
        await message.answer(
            "✅Правильно!\n\nБлестяще! 🔥\nНажмите «Новый вопрос» для продолжения.",
            reply_markup=get_quiz_keyboard(),
        )
    else:
        await message.answer(
            "❌Неправильно...\n\n"
            "Подумайте ещё! У вас есть ещё попытки.\n"
            "Напишите новый вариант ответа:",
            reply_markup=get_quiz_keyboard(),
        )


@router.callback_query(F.data == "new_question")
async def callback_new_question(callback: CallbackQuery, state: FSMContext):
    await send_new_question(callback, state)
    await callback.answer()


@router.callback_query(F.data == "show_answer")
async def callback_show_answer(callback: CallbackQuery, state: FSMContext):
    platform = PLATFORM
    user_id = callback.from_user.id
    _, answer_full = get_user_current_question(platform, user_id)

    if not answer_full:
        await callback.answer(
            "Вопрос не найден. Нажмите «Новый вопрос»", show_alert=True
        )
        return

    text = f"<b>Правильный ответ:</b>\n\n{answer_full}\n\nПопробуйте ответить на следующий вопрос!"

    try:
        await callback.message.edit_text(
            text, reply_markup=get_quiz_keyboard(), parse_mode="HTML"
        )
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer("Ответ уже показан 😊", show_alert=False)
        else:
            await callback.answer(
                "Не удалось обновить сообщение. Попробуйте позже.", show_alert=True
            )

    await callback.answer()
