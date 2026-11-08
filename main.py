import asyncio
import logging
import os
import sys
import json
import ssl
import re
import httpx

import config
import db
import extended
import commands_catalog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (MOXXI-MAX) %(message)s"
)
log = logging.getLogger("moxxi-max")

# SSL контекст без строгой проверки Минцифры на Windows
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class MaxBotClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = config.API_BASE
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        self.marker = None

    async def send_message(self, chat_id: int | str, text: str, buttons: list | None = None) -> bool:
        url = f"{self.base_url}/messages"
        payload = {
            "text": text
        }
        if buttons:
            payload["attachments"] = [
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": buttons
                    }
                }
            ]

        params = {}
        if isinstance(chat_id, int):
            params["chat_id"] = chat_id
        else:
            params["chat_id"] = str(chat_id)

        try:
            async with httpx.AsyncClient(verify=ssl_context, timeout=15.0) as client:
                resp = await client.post(url, headers=self.headers, params=params, json=payload)
                if resp.status_code == 200:
                    return True
                else:
                    log.warning("Ошибка отправки MAX: %d %s", resp.status_code, resp.text)
                    return False
        except Exception as e:
            log.error("Исключение при send_message в MAX: %s", e)
            return False

    async def poll_updates(self):
        url = f"{self.base_url}/updates"
        params = {}
        if self.marker:
            params["marker"] = self.marker

        try:
            # Таймаут 30 секунд для Long Polling
            async with httpx.AsyncClient(verify=ssl_context, timeout=35.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    if "marker" in data:
                        self.marker = data["marker"]
                    return data.get("updates", [])
                elif resp.status_code == 429:
                    log.warning("MAX API: лимит запросов (429), спим 2 сек...")
                    await asyncio.sleep(2.0)
                else:
                    log.warning("MAX updates error: %d %s", resp.status_code, resp.text)
        except httpx.TimeoutException:
            # Обычный таймаут long poll, если сообщений нет
            pass
        except Exception as e:
            log.error("Сбой опроса updates в MAX: %s", e)
            await asyncio.sleep(2.0)
        return []

def get_main_keyboard_max():
    """Инлайн-кнопки для быстрого управления в MAX"""
    return [
        [
            {"type": "callback", "text": "👑 Профиль", "payload": "профиль"},
            {"type": "callback", "text": "🎁 Бонус", "payload": "бонус"}
        ],
        [
            {"type": "callback", "text": "🏦 Банк", "payload": "банк"},
            {"type": "callback", "text": "🏢 Бизнесы", "payload": "бизнесы"}
        ],
        [
            {"type": "callback", "text": "🎰 Казино", "payload": "казино"},
            {"type": "callback", "text": "⛏ Шахта", "payload": "шахта"}
        ],
        [
            {"type": "callback", "text": "📖 Все 414 команд", "payload": "команды"}
        ]
    ]

async def handle_message(bot: MaxBotClient, chat_id: int | str, user_id: int, user_name: str, raw_text: str):
    clean_txt = raw_text.strip()
    if not clean_txt:
        return

    # Префикс ID для базы данных
    db_uid = config.MAX_UID_OFFSET + user_id
    db_cid = config.MAX_UID_OFFSET + (chat_id if isinstance(chat_id, int) else hash(str(chat_id)) % 10000000)

    # Инициализация пользователя в единой БД
    await db.ensure_user(db_uid, username=f"max_{user_id}", first_name=user_name)
    u_data = await db.get_user(db_uid) or {}

    p = clean_txt.split()
    cmd = p[0].lower() if p else ""
    args = clean_txt[len(cmd):].strip()

    log.info("MAX команда от [%s|%d]: cmd='%s', args='%s'", user_name, user_id, cmd, args)

    # 1. СТАРТ / ПОМОЩЬ / МЕНЮ
    if cmd in ("/start", "старт", "начать", "меню", "помощь", "хелп", "команды", "страт", "играть", "игры", "игра", "play"):
        msg = (
            f"✨ Добро пожаловать в MOXXI 3.0 Ultimate (MAX Edition)! ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👋 Привет, {user_name}! Я игровой бот для чатов и бесед.\n\n"
            f"💰 Ваш баланс: {u_data.get('balance', 0):,} 🌑 монет\n"
            f"👑 Ранг: {u_data.get('rank', 1)} ур. | XP: {u_data.get('xp', 0)}\n\n"
            f"🎮 Быстрые команды:\n"
            f"• «профиль» — ваша личная карточка\n"
            f"• «бонус» — забрать ежедневную награду (2 500 – 7 500 🌑)\n"
            f"• «банк» — открыть вклад под 5% в сутки\n"
            f"• «бизнесы» — купить предприятие (40 видов)\n"
            f"• «шахта» — добывать руду и самоцветы\n"
            f"• «казино [ставка]» — испытать удачу в слотах\n"
            f"• «команды» — оглавление из 12 разделов (414 команд!)"
        )
        await bot.send_message(chat_id, msg, buttons=get_main_keyboard_max())
        return

    # 2. ПРОФИЛЬ
    elif cmd in ("профиль", "проф", "я", "стата", "баланс"):
        b = u_data.get("balance", 0)
        bank = u_data.get("bank", 0)
        lvl = u_data.get("level", 1)
        xp = u_data.get("xp", 0)
        rank = u_data.get("rank", 1)
        msg = (
            f"👑 ПРОФИЛЬ ИГРОКА MOXXI (MAX)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Игрок: {user_name} (ID: {user_id})\n"
            f"🎖 Ранг: {rank} ур. | Уровень: {lvl} ({xp} XP)\n\n"
            f"💰 На руках: {b:,} 🌑\n"
            f"🏦 В банке: {bank:,} 🌑\n\n"
            f"🏢 Бизнесы: используйте «бизнесы»\n"
            f"🚗 Автопарк: используйте «гараж»"
        )
        await bot.send_message(chat_id, msg, buttons=get_main_keyboard_max())
        return

    # 3. БОНУС
    elif cmd in ("бонус", "bonus", "ежедневный"):
        import time
        now = int(time.time())
        last = u_data.get("last_bonus_time", 0) or 0
        if now - last < 86400:
            left = 86400 - (now - last)
            h = left // 3600
            m = (left % 3600) // 60
            await bot.send_message(chat_id, f"⏳ Вы уже забирали бонус! Приходите через {h} ч {m} мин.")
            return

        import random
        reward = random.randint(2500, 7500)
        await db.add_balance(db_uid, reward)
        await db.add_xp(db_uid, 50)
        await db.update_user(db_uid, last_bonus_time=now)
        await bot.send_message(
            chat_id,
            f"🎁 ЕЖЕДНЕВНЫЙ БОНУС ПОЛУЧЕН!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Вам начислено: +{reward:,} 🌑 монет\n"
            f"⭐ Опыт: +50 XP\n\n"
            f"Приходите завтра за новой порцией монет!",
            buttons=get_main_keyboard_max()
        )
        return

    # 4. БАНК
    elif cmd == "банк":
        bank_val = u_data.get("bank", 0)
        msg = (
            f"🏦 ГОСУДАРСТВЕННЫЙ БАНК MOXXI\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 Ваш депозит: {bank_val:,} 🌑\n"
            f"📈 Доходность: 5% каждые 24 часа\n\n"
            f"💡 Команды:\n"
            f"• «банк положить [сумма/все]» — сделать вклад\n"
            f"• «банк снять [сумма/все]» — забрать монеты"
        )
        await bot.send_message(chat_id, msg)
        return

    # 5. КАЗИНО
    elif cmd in ("казино", "слоты", "рулетка"):
        if not args:
            await bot.send_message(chat_id, "🎰 Чтобы сыграть, напишите: «казино [ставка]» (например: «казино 500»)")
            return
        try:
            bet = int(args.split()[0])
        except ValueError:
            await bot.send_message(chat_id, "❌ Укажите ставку числом, например: «казино 500»")
            return

        bal = u_data.get("balance", 0)
        if bet <= 0 or bet > bal:
            await bot.send_message(chat_id, f"❌ Недостаточно монет! Ваш баланс: {bal:,} 🌑")
            return

        import random
        symbols = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣"]
        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)

        if s1 == s2 == s3:
            mult = 7 if s1 == "7️⃣" else (5 if s1 == "💎" else 3)
            win = bet * mult
            await db.add_balance(db_uid, win - bet)
            await bot.send_message(
                chat_id,
                f"🎰 ИГРОВОЙ АВТОМАТ MOXXI 🎰\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"| {s1} | {s2} | {s3} |\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 ДЖЕКПОТ! Вы выиграли x{mult} (+{win:,} 🌑)!"
            )
        else:
            await db.add_balance(db_uid, -bet)
            await bot.send_message(
                chat_id,
                f"🎰 ИГРОВОЙ АВТОМАТ MOXXI 🎰\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"| {s1} | {s2} | {s3} |\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💔 Не повезло! Вы проиграли {bet:,} 🌑."
            )
        return

    # 6. ШАХТА
    elif cmd in ("шахта", "копать"):
        import random
        earned = random.randint(200, 800)
        await db.add_balance(db_uid, earned)
        await db.add_xp(db_uid, 15)
        await bot.send_message(chat_id, f"⛏ Вы спустились в шахту и добыли ценных ископаемых на {earned:,} 🌑 монет! (+15 XP)")
        return

    # 7. ВСЕ 12 РАЗДЕЛОВ КОМАНД
    elif cmd in ("команды", "каталог", "раздел", "разделы"):
        await bot.send_message(chat_id, commands_catalog.get_hub_text())
        return

    # Другие команды
    await bot.send_message(chat_id, f"🤖 Команда не распознана. Напишите «команды» или «помощь»!")

async def run_bot():
    token = config.MAX_BOT_TOKEN
    log.info("Запуск бота MOXXI MAX...")
    await db.init()
    bot = MaxBotClient(token)
    log.info("Подключение к платформе MAX успешно! Начало Long Polling...")

    while True:
        try:
            updates = await bot.poll_updates()
            for update in updates:
                log.info(">>> ВХОДЯЩИЙ UPDATE MAX: %s", json.dumps(update, ensure_ascii=False))
                # MAX может присылать update в разных полях
                msg = update.get("message")
                callback = update.get("callback")

                # Если это входящее текстовое сообщение
                if msg:
                    # В MAX текст сообщения хранится в msg["body"]["text"] или msg["text"]
                    body = msg.get("body", {})
                    text = body.get("text") or msg.get("text", "")
                    sender = msg.get("sender", {})
                    user_id = sender.get("user_id") or msg.get("sender_id") or 0
                    user_name = sender.get("first_name") or sender.get("name") or "Игрок"
                    recipient = msg.get("recipient", {})
                    chat_id = recipient.get("chat_id") or msg.get("chat_id") or user_id
                    log.info("Распарсено сообщение MAX: user_id=%s, chat_id=%s, text='%s'", user_id, chat_id, text)
                    if text and user_id:
                        asyncio.create_task(handle_message(bot, chat_id, user_id, user_name, text))

                # Если это клик по инлайн-кнопке
                elif callback:
                    payload = callback.get("payload", "")
                    user = callback.get("user", {})
                    user_id = user.get("user_id", 0)
                    user_name = user.get("first_name", "Игрок")
                    chat_id = callback.get("chat_id") or user_id
                    if payload and user_id:
                        asyncio.create_task(handle_message(bot, chat_id, user_id, user_name, payload))

        except Exception as e:
            log.error("Сбой в цикле Long Polling MAX: %s", e)
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(run_bot())
