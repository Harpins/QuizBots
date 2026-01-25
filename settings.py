import environs
from pathlib import Path

env = environs.Env()
env.read_env()

TG_BOT_TOKEN = env.str("TG_BOT_TOKEN", "")
JSON_PATH = env.str("JSON_PATH", "quiz.json")
VK_GROUP_TOKEN = env.str("VK_GROUP_TOKEN", "")
ERROR_BOT_TOKEN = env.str("ERROR_BOT_TOKEN", "")
ERROR_CHAT_ID = env.int("ERROR_CHAT_ID", None)

BASE_DIR = Path(__file__).parent
LANGUAGE_CODE = "ru-RU"
QUESTIONS_FILE = Path(JSON_PATH)