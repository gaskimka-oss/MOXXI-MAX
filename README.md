# 🚀 MOXXI — Бот для мессенджера MAX

Игровой и управляющий бот MOXXI для российского мессенджера MAX (`business.max.ru`), синхронизированный с общей базой данных экосистемы MOXXI.

## 🌟 Возможности
- Интерактивные кнопки и инлайн-клавиатура
- Игры, экономика, дуэли, краш, казино, питомцы
- Полная интеграция с Mini App (`https://gaskimka-oss.github.io/MOXXI/`)
- Long Polling через `https://platform-api2.max.ru`
- Единый баланс и профиль с Telegram, VK и Discord

## 📦 Быстрый запуск
1. Клонируйте репозиторий:
```bash
git clone https://github.com/gaskimka-oss/MOXXI-MAX.git
cd MOXXI-MAX
```
2. Скопируйте `.env.example` в `.env` и впишите токен бота из `business.max.ru`:
```bash
cp .env.example .env
```
3. Запустите:
```bash
python main.py
```
или запустите `start.bat`.
