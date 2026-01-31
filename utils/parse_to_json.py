import json
import re
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_qa_pairs(filepath: Path):
    pairs = []
    current_question = ""
    current_answer = ""

    try:
        with open(filepath, "r", encoding="koi8-r") as file:
            lines = [line.rstrip() for line in file.readlines()]

        counter = 0
        while counter < len(lines):
            line = lines[counter].strip()
            if re.match(r"^Вопрос \d+:$", line):
                if current_question and current_answer:
                    pairs.append((current_question.strip(), current_answer.strip()))

                current_question = ""
                current_answer = ""

                counter += 1
                while counter < len(lines) and not lines[counter].startswith("Ответ:"):
                    current_question += lines[counter] + "\n"
                    counter += 1
                current_question = current_question.strip()
                continue

            elif line.startswith("Ответ:"):
                current_answer = line[6:].strip()
                counter += 1
                while (
                    counter < len(lines)
                    and not lines[counter].startswith("Автор:")
                    and not lines[counter].startswith("Источник:")
                    and not re.match(r"^Вопрос \d+:$", lines[counter].strip())
                    and not lines[counter].startswith("Тур:")
                ):
                    current_answer += "\n" + lines[counter].strip()
                    counter += 1
                current_answer = current_answer.strip()
            counter += 1

        if current_question and current_answer:
            pairs.append((current_question.strip(), current_answer.strip()))
        return pairs

    except UnicodeDecodeError as err:
        logger.error(
            f"Ошибка декодирования файла {filepath.name} (кодировка koi8-r): {err}"
        )
        return []
    except FileNotFoundError:
        logger.error(f"Файл не найден: {filepath}")
        return []
    except Exception as err:
        logger.exception(
            f"Неожиданная ошибка при обработке файла {filepath.name}: {err}"
        )
        return []


def main(input_folder: str = "txt_files", output_file: str = "quiz.json"):
    input_path = Path(input_folder)
    output_path = Path(output_file)

    if not input_path.is_dir():
        logger.error(
            f"Указанная папка не существует или не является директорией: {input_path}"
        )
        return

    logger.info(f"Начало обработки файлов в директории: {input_path}")
    logger.info(f"Результат будет сохранён в: {output_path}")

    quiz_dict = {}
    processed_files = 0
    total_pairs = 0

    for txt_file in sorted(input_path.glob("*.txt")):
        processed_files += 1
        logger.info(f"Обработка файла: {txt_file.name}")
        pairs = extract_qa_pairs(txt_file)

        for question, answer in pairs:
            normalized_question = " ".join(question.split())
            if not normalized_question:
                logger.warning(
                    f"Пропущен пустой/некорректный вопрос в файле {txt_file.name}"
                )
                continue
            if normalized_question in quiz_dict:
                logger.warning(
                    f"Найден дубликат вопроса: {normalized_question[:50]}..."
                )
                logger.warning(
                    f"Старый ответ: {quiz_dict[normalized_question][:50]}..."
                )
                logger.warning(f"Новый ответ: {answer[:50]}...")
            quiz_dict[normalized_question] = answer
            total_pairs += 1

    try:
        with output_path.open("w", encoding="utf-8") as json_file:
            json.dump(quiz_dict, json_file, ensure_ascii=False, indent=2)
        logger.info(
            f"Успешно сохранено {len(quiz_dict)} уникальных вопросов в {output_file}"
        )
        logger.info(f"Обработано файлов: {processed_files}, найдено пар: {total_pairs}")
    except Exception as err:
        logger.exception(f"Ошибка при записи результата в {output_file}: {err}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.critical("Критическая ошибка при запуске скрипта", exc_info=True)
        raise
