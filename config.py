import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

# Токен бота из business.max.ru (хранится в .env файле)
MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "").strip()

# Базовый API URL для мессенджера MAX
API_BASE = os.getenv("MAX_API_BASE", "https://platform-api2.max.ru")

# Префикс ID для базы данных
# Telegram: 1..69_999_999_999
# VK: 70_000_000_000 + vk_id
# Discord: 80_000_000_000 + dc_id
# MAX: 90_000_000_000 + max_id
MAX_UID_OFFSET = 90_000_000_000
