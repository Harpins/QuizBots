from vk_api.keyboard import VkKeyboard

def get_quiz_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос")
    keyboard.add_line()
    keyboard.add_button("Показать ответ")
    return keyboard.get_keyboard()