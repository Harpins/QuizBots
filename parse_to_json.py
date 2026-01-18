import json
import re
from pathlib import Path


def extract_qa_pairs(filepath: Path):
    with open(filepath, "r", encoding="koi8-r") as file:
        lines = [line.rstrip() for line in file.readlines()]

    pairs = []
    current_question = ""
    current_answer = ""

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


def main(input_folder: str = "txt_files", output_file: str = "quiz.json"):
    input_path = Path(input_folder)
    quiz_dict = {}

    for txt_file in sorted(input_path.glob("*.txt")):
        pairs = extract_qa_pairs(txt_file)

        for question, answer in pairs:
            normalized_question = " ".join(question.split())
            if normalized_question:
                quiz_dict[normalized_question] = answer

    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(quiz_dict, json_file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
