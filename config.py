import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

# Токен бота из business.max.ru (хранится в .env файле)
MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "").strip()

# Базовый API URL для мессенджера MAX
API_BASE = os.getenv("MAX_API_BASE", "https://platform-api2.max.ru")

# Изолированная база данных мессенджера MAX (moxxi_max.db)
MAX_UID_OFFSET = 0
