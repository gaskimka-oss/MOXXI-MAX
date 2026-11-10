"""🚀 MOXXI 3.0 — Полнофункциональный бот для мессенджера MAX (business.max.ru).
Папка: C:\\Users\\eiema\\OneDrive\\Desktop\\moxximax

Интеграция:
1. 👑 10 Рангов администрации и профиль
2. 🎮 Официальное Mini App приложение (кликалка, инвентарь, игры)
3. 🏢 Империя предприятий и пассивный доход (40 видов бизнеса)
4. 🏦 Государственный Банк: вклады под 5% в сутки и снятие
5. 🎰 Азартные игры: Казино (слоты), Кости, Краш, Рулетка
6. ⚔️ PvP Дуэли между игроками
7. 🐉 Рейдовые Боссы с наградами
8. 🚗 Автопарк и Гараж
9. 🐾 Питомцы: зоомагазин и кормление
10. ⛏ Шахта и Рыбалка с редкими ресурсами
11. 🏆 Топ богачей экосистемы
12. 📦 Кейсы и Лутбоксы
13. 📖 414 команд каталога
"""
from __future__ import annotations

import asyncio
import html
import json
import logging
import os
import random
import re
import ssl
import sys
import time
import httpx

import config
import db
import commands_catalog
import extended

# Настройка UTF-8 кодировки консоли
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (MOXXI-MAX) %(message)s"
)
log = logging.getLogger("moxxi-max")

# Отключение валидации сертификатов для Минцифры/платформы MAX
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class MaxBotClient:
    """Клиент для взаимодействия с Bot API мессенджера MAX (https://platform-api2.max.ru)"""
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

        params = {"chat_id": str(chat_id)}

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

    async def answer_callback(self, callback_id: str, notification: str = "✨ Запрос принят") -> bool:
        """Подтверждение нажатия кнопки в MAX для снятия загрузки с интерфейса"""
        if not callback_id:
            return False
        url = f"{self.base_url}/answers"
        try:
            async with httpx.AsyncClient(verify=ssl_context, timeout=10.0) as client:
                resp = await client.post(url, headers=self.headers, params={"callback_id": callback_id}, json={"notification": notification})
                return resp.status_code == 200
        except Exception as e:
            log.warning("answer_callback error: %s", e)
            return False

    async def poll_updates(self):
        url = f"{self.base_url}/updates"
        params = {}
        if self.marker:
            params["marker"] = self.marker

        try:
            async with httpx.AsyncClient(verify=ssl_context, timeout=35.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    if "marker" in data:
                        self.marker = data["marker"]
                    return data.get("updates", [])
                elif resp.status_code == 429:
                    log.warning("MAX API: лимит запросов (429), пауза 2 сек...")
                    await asyncio.sleep(2.0)
                else:
                    log.warning("MAX updates error: %d %s", resp.status_code, resp.text)
        except httpx.TimeoutException:
            pass
        except Exception as e:
            log.error("Сбой опроса updates в MAX: %s", e)
            await asyncio.sleep(2.0)
        return []


def get_main_keyboard_max():
    """Инлайн-кнопки главного меню для быстрого управления в MAX"""
    return [
        [
            {"type": "link", "text": "🎮 Играть в Mini App", "url": "https://gaskimka-oss.github.io/MOXXI/"}
        ],
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
            {"type": "callback", "text": "⚔️ Дуэль", "payload": "дуэль"},
            {"type": "callback", "text": "🐉 Босс", "payload": "босс"}
        ],
        [
            {"type": "link", "text": "➕ Добавить в группу", "url": "https://max.ru/se14948893_bot"},
            {"type": "callback", "text": "🏆 Топ", "payload": "топ"}
        ],
        [
            {"type": "callback", "text": "📖 Все команды", "payload": "команды"}
        ]
    ]



# ═══════════════════════════════════════════════════════════════
# 🌉 ОМНИКАНАЛЬНЫЙ МОСТ В TELEGRAM И DISCORD
# ═══════════════════════════════════════════════════════════════
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "").strip() or "8545937596:AAF0PuDMmgdu4fbUJpJbwJeTSLByPWive4w"
TG_OWNERS = [8036974481, 8412527198]

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
if not DISCORD_TOKEN:
    for p in [r"C:\Users\eiema\OneDrive\Desktop\MOXXI Support\.env", r"C:\Users\eiema\OneDrive\Desktop\moxxidc\.env"]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    for l in fl:
                        if l.startswith("DISCORD_BOT_TOKEN="):
                            DISCORD_TOKEN = l.split("=", 1)[1].strip()
                            break
            except Exception:
                pass


async def notify_telegram_about_ticket_max(user_id: int, user_name: str, question: str, category: str = "Общее"):
    if not TG_BOT_TOKEN:
        return
    admin_text = (
        f"🆘 🔔 <b>НОВОЕ ОБРАЩЕНИЕ ИЗ MAX MESSENGER</b>\n"
        f"🌐 <b>Платформа:</b> ⚡️ MAX\n"
        f"📂 <b>Категория:</b> {html.escape(category)}\n"
        f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        f"👤 <b>Пользователь:</b> {html.escape(user_name)}\n"
        f"🆔 <b>MAX ID:</b> <code>{user_id}</code>\n\n"
        f"📝 <b>Вопрос / Суть:</b>\n«{html.escape(question)}»"
    )
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=5) as client:
        for rid in TG_OWNERS:
            try:
                payload = {"chat_id": rid, "text": admin_text, "parse_mode": "HTML"}
                await client.post(url, json=payload)
            except Exception as e:
                log.warning("Ошибка отправки MAX тикета в TG: %s", e)


async def notify_discord_about_ticket_max(user_id: int, user_name: str, question: str, category: str = "Общее"):
    if not DISCORD_TOKEN:
        return
    queue_ch_id = 1569227215160221797
    payload = {
        "embeds": [
            {
                "title": f"🎫 ОБРАЩЕНИЕ ИЗ MAX • [{category}]",
                "description": (
                    f"👤 **Пользователь:** `{user_name}` (MAX ID: `{user_id}`)\n"
                    f"📱 **Платформа:** `⚡️ MAX Messenger`\n"
                    f"📂 **Категория:** `{category}`\n"
                    f"⏱ **Время:** <t:{int(time.time())}:R>\n\n"
                    f"───────────────────────────────\n"
                    f"📝 **Вопрос / Суть обращения:**\n{question[:1500]}\n"
                    f"───────────────────────────────"
                ),
                "color": 15844367,
                "footer": {"text": "MOXXI Omnichannel Desk • MAX ⇄ Discord"}
            }
        ]
    }
    url = f"https://discord.com/api/v10/channels/{queue_ch_id}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            await client.post(url, json=payload, headers=headers)
        except Exception as e:
            log.warning("Ошибка отправки MAX тикета в Discord: %s", e)


async def handle_message(bot: MaxBotClient, chat_id: int | str, user_id: int, user_name: str, raw_text: str):
    clean_txt = raw_text.strip()
    if not clean_txt:
        return

    # Префикс ID для базы данных
    db_uid = config.MAX_UID_OFFSET + user_id
    db_cid = config.MAX_UID_OFFSET + (int(chat_id) if str(chat_id).isdigit() else hash(str(chat_id)) % 100000000)

    # Инициализация пользователя в единой БД
    await db.ensure_user(db_uid, username=f"max_{user_id}", first_name=user_name)
    # Запись активности чата
    try:
        await db.record_chat_activity(chat_id)
    except Exception:
        pass
    u_data = await db.get_user(db_uid) or {}

    p = clean_txt.split()
    cmd = p[0].lower() if p else ""
    args = clean_txt[len(p[0]):].strip() if p else ""

    log.info("MAX действие от [%s|%d]: cmd='%s', args='%s'", user_name, user_id, cmd, args)

    # ═══════════════════════════════════════════════════════════
    # ➕ ДОБАВИТЬ В ГРУППУ / БЕСЕДУ
    # ═══════════════════════════════════════════════════════════
    if cmd in ("добавить", "группа", "группу", "беседа", "беседу", "пригласить", "invite", "инвайт") or (cmd == "в" and args in ("группу", "беседу", "чат")):
        msg = (
            f"🌟 КАК ДОБАВИТЬ MOXXI 3.0 В СВОЮ ГРУППУ / БЕСЕДУ MAX:\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"1. Нажмите на кнопку «➕ Добавить бота в группу» ниже\n"
            f"2. Либо откройте профиль бота @se14948893_bot и выберите «Добавить в беседу»\n"
            f"3. Выберите нужную группу и выдайте боту права администратора!\n\n"
            f"🎮 В беседах доступны: рейдовые боссы, дуэли, кланы, казино и общие рейтинги!\n"
            f"💡 После добавления напишите в группе «старт» или «команды»."
        )
        buttons = [
            [{"type": "link", "text": "➕ Добавить бота в группу", "url": "https://max.ru/se14948893_bot"}],
            [{"type": "callback", "text": "📖 Все команды", "payload": "команды"}]
        ]
        await bot.send_message(chat_id, msg, buttons=buttons)
        return

    # ═══════════════════════════════════════════════════════════
    # 0. МИНИ-ПРИЛОЖЕНИЕ (WEB APP)
    # ═══════════════════════════════════════════════════════════
    if cmd in ("приложение", "апп", "app", "веб", "кликер", "мини"):
        msg = (
            f"🎮 ОФИЦИАЛЬНОЕ МИНИ-ПРИЛОЖЕНИЕ MOXXI 🎮\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Открывайте полноценную интерактивную игру MOXXI прямо внутри MAX!\n\n"
            f"🔥 В приложении вас ждут:\n"
            f"• 💎 Увлекательный кликер и майнинг\n"
            f"• 🎰 Интерактивное казино и рулетка\n"
            f"• 🎒 Инвентарь и прокачка персонажа\n"
            f"• 💰 Единый баланс с ботом в чате\n\n"
            f"👇 Нажмите кнопку ниже, чтобы запустить приложение:"
        )
        buttons = [
            [{"type": "link", "text": "🎮 Запустить Mini App", "url": "https://gaskimka-oss.github.io/MOXXI/"}]
        ]
        await bot.send_message(chat_id, msg, buttons=buttons)
        return

    # ═══════════════════════════════════════════════════════════
    # 1. СТАРТ / ПОМОЩЬ / МЕНЮ
    # ═══════════════════════════════════════════════════════════
    if cmd in ("/start", "старт", "начать", "меню", "помощь", "хелп", "страт", "играть", "игры", "игра", "play"):
        msg = (
            f"✨ Добро пожаловать в MOXXI 3.0 Ultimate (MAX Edition)! ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👋 Привет, {user_name}! Я кроссплатформенный игровой бот.\n\n"
            f"💰 Ваш баланс: {u_data.get('balance', 0):,} 🌑 монет\n"
            f"👑 Ранг: {u_data.get('rank', 1)} ур. | Опыт: {u_data.get('xp', 0)} XP\n\n"
            f"🎮 Быстрые действия доступны по кнопкам ниже:\n"
            f"• «профиль» — карточка персонажа и имущество\n"
            f"• «бонус» — забрать ежедневные монеты (до 7 500 🌑)\n"
            f"• «банк» — пассивный доход 5% в сутки\n"
            f"• «бизнесы» — покупка предприятий и пассивный доход\n"
            f"• «казино [ставка]» — испытать удачу в слотах\n"
            f"• «шахта» / «рыбалка» — добыча ценных ресурсов\n"
            f"• «дуэль [id] [ставка]» — битва между игроками\n"
            f"• «босс» — атаковать рейдового босса беседы\n"
            f"• «команды» — полный каталог из 414 команд!"
        )
        await bot.send_message(chat_id, msg, buttons=get_main_keyboard_max())
        return

    # ═══════════════════════════════════════════════════════════
    # 2. ПРОФИЛЬ
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("профиль", "проф", "я", "стата", "баланс"):
        b = u_data.get("balance", 0)
        bank = u_data.get("bank", 0)
        lvl = u_data.get("level", 1)
        xp = u_data.get("xp", 0)
        rank = u_data.get("rank", 1)
        u_biz = await db.get_user_businesses(db_uid)
        biz_count = len(u_biz) if u_biz else 0

        msg = (
            f"👑 ПРОФИЛЬ ИГРОКА MOXXI (MAX)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Игрок: {user_name} (ID: {user_id})\n"
            f"🎖 Ранг: {rank} ур. | Уровень: {lvl} ({xp} XP)\n\n"
            f"💰 На руках: {b:,} 🌑\n"
            f"🏦 В банке: {bank:,} 🌑\n"
            f"🏢 Предприятий: {biz_count} шт.\n\n"
            f"💡 Для просмотра предприятий напишите «бизнесы»\n"
            f"💡 Для просмотра авто напишите «гараж»"
        )
        await bot.send_message(chat_id, msg, buttons=get_main_keyboard_max())
        return

    # ═══════════════════════════════════════════════════════════
    # 3. БОНУС
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("бонус", "bonus", "ежедневный"):
        now = int(time.time())
        last = u_data.get("last_bonus_time", 0) or 0
        if now - last < 86400:
            left = 86400 - (now - last)
            h = left // 3600
            m = (left % 3600) // 60
            await bot.send_message(chat_id, f"⏳ Вы уже забирали бонус! Приходите через {h} ч {m} мин.", buttons=get_main_keyboard_max())
            return

        reward = random.randint(2500, 7500)
        await db.add_balance(db_uid, reward)
        await db.add_xp(db_uid, 50)
        await db.update_user(db_uid, last_bonus_time=now)
        await bot.send_message(
            chat_id,
            f"🎁 ЕЖЕДНЕВНЫЙ БОНУС ПОЛУЧЕН!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Начислено: +{reward:,} 🌑 монет\n"
            f"⭐ Опыт: +50 XP\n\n"
            f"Приходите завтра за следующей наградой!",
            buttons=get_main_keyboard_max()
        )
        return

    # ═══════════════════════════════════════════════════════════
    # 4. БАНК И ДЕПОЗИТЫ
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("банк", "депозит"):
        sub = args.lower().strip()
        bank_val = u_data.get("bank", 0)
        bal_val = u_data.get("balance", 0)

        if sub.startswith("положить"):
            parts = sub.split()
            amount_str = parts[1] if len(parts) > 1 else ""
            if amount_str in ("все", "всё"):
                amt = bal_val
            else:
                try:
                    amt = int(amount_str)
                except ValueError:
                    amt = 0

            if amt <= 0 or amt > bal_val:
                await bot.send_message(chat_id, f"❌ Недостаточно средств на руках! У вас: {bal_val:,} 🌑.")
                return

            await db.deposit_to_bank(db_uid, amt)
            await bot.send_message(chat_id, f"🏦 Вы успешно положили в банк {amt:,} 🌑! Баланс в банке: {bank_val + amt:,} 🌑.")
            return

        elif sub.startswith("снять"):
            parts = sub.split()
            amount_str = parts[1] if len(parts) > 1 else ""
            if amount_str in ("все", "всё"):
                amt = bank_val
            else:
                try:
                    amt = int(amount_str)
                except ValueError:
                    amt = 0

            if amt <= 0 or amt > bank_val:
                await bot.send_message(chat_id, f"❌ Недостаточно средств в банке! У вас в банке: {bank_val:,} 🌑.")
                return

            await db.withdraw_from_bank(db_uid, amt)
            await bot.send_message(chat_id, f"🏦 Вы успешно сняли из банка {amt:,} 🌑! На руках: {bal_val + amt:,} 🌑.")
            return

        msg = (
            f"🏦 ГОСУДАРСТВЕННЫЙ БАНК MOXXI\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 Ваш депозит: {bank_val:,} 🌑\n"
            f"💰 На руках: {bal_val:,} 🌑\n"
            f"📈 Доходность: 5% каждые 24 часа\n\n"
            f"💡 Команды:\n"
            f"• «банк положить [сумма/все]» — сделать вклад\n"
            f"• «банк снять [сумма/все]» — забрать монеты"
        )
        await bot.send_message(chat_id, msg, buttons=get_main_keyboard_max())
        return

    # ═══════════════════════════════════════════════════════════
    # 5. БИЗНЕСЫ И ПАССИВНЫЙ ДОХОД
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("бизнесы", "бизнес", "предприятия", "прибыль"):
        if cmd == "прибыль" or args.lower().strip() in ("собрать", "прибыль", "доход"):
            profit = await db.collect_business_profit(db_uid)
            if profit > 0:
                await bot.send_message(chat_id, f"💰 Вы собрали накопившуюся прибыль с предприятий: +{profit:,} 🌑!")
            else:
                await bot.send_message(chat_id, "Прибыль ещё не накопилась (начисления производятся каждый час).")
            return

        user_xp = u_data.get("xp", 0)
        user_level = max(1, user_xp // 100)
        u_biz = await db.get_user_businesses(db_uid)

        lines = [
            "🏢 ИМПЕРИЯ ПРЕДПРИЯТИЙ MOXXI 🏢",
            "━━━━━━━━━━━━━━━━━━━━",
            f"👤 Владелец: {user_name} ({user_level} Lvl)",
        ]

        if u_biz:
            total_daily = 0
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("💼 Ваши предприятия:")
            for b in u_biz:
                k = b["biz_key"]
                real_k = db.BIZ_ALIASES.get(k, k)
                if real_k in db.BIZ_CATALOG:
                    b_info = db.BIZ_CATALOG[real_k]
                    inc = b_info["daily_income"] * b["count"]
                    total_daily += inc
                    lines.append(f"• {b_info['name']} (x{b['count']}) ➔ +{inc:,} 🌑/день")
            lines.append(f"📈 Суммарный доход: +{total_daily:,} 🌑/день")

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("📦 Топовые предприятия для покупки:")
        all_items = list(db.BIZ_CATALOG.items())[:8]
        for idx, (k, info) in enumerate(all_items):
            num = idx + 1
            status_ico = "✅" if user_level >= info["req_lvl"] else f"🔒 Lvl {info['req_lvl']}"
            lines.append(f"{num}. {info['name']} — {info['cost']:,} 🌑 (+{info['daily_income']:,}/день | {status_ico})")

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 Команды:")
        lines.append("• «купить_бизнес [1-40]» — купить предприятие")
        lines.append("• «прибыль» — забрать накопленный доход")

        buttons = [
            [{"type": "callback", "text": "💰 Собрать прибыль", "payload": "прибыль"}],
            [{"type": "callback", "text": "👑 В главное меню", "payload": "меню"}]
        ]
        await bot.send_message(chat_id, "\n".join(lines), buttons=buttons)
        return

    elif cmd in ("купить_бизнес", "купитьбизнес"):
        keys = list(db.BIZ_CATALOG.keys())
        idx_match = re.search(r"\b(\d+)\b", args)
        b_key = None
        if idx_match:
            idx_val = int(idx_match.group(1))
            if 1 <= idx_val <= len(keys):
                b_key = keys[idx_val - 1]

        if not b_key or b_key not in db.BIZ_CATALOG:
            await bot.send_message(chat_id, "Укажите номер предприятия от 1 до 40! Пример: «купить_бизнес 1» (Каталог: «бизнесы»).")
            return

        b_info = db.BIZ_CATALOG[b_key]
        user_bal = u_data.get("balance", 0)
        user_xp = u_data.get("xp", 0)
        user_lvl = max(1, user_xp // 100)

        if user_lvl < b_info["req_lvl"]:
            await bot.send_message(chat_id, f"🔒 Для покупки «{b_info['name']}» требуется {b_info['req_lvl']} уровень!")
            return

        if user_bal < b_info["cost"]:
            await bot.send_message(chat_id, f"❌ Недостаточно монет! Стоимость: {b_info['cost']:,} 🌑, у вас: {user_bal:,} 🌑.")
            return

        await db.add_balance(db_uid, -b_info["cost"])
        await db.buy_business(db_uid, b_key)
        await db.add_xp(db_uid, 30)
        await bot.send_message(chat_id, f"🎉 Поздравляем! Вы приобрели предприятие «{b_info['name']}»! Доход: +{b_info['daily_income']:,} 🌑/день.")
        return

    # ═══════════════════════════════════════════════════════════
    # 6. КАЗИНО И СЛОТЫ
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("казино", "слоты"):
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
                f"🎉 ДЖЕКПОТ! Вы выиграли x{mult} (+{win:,} 🌑)!",
                buttons=get_main_keyboard_max()
            )
        else:
            await db.add_balance(db_uid, -bet)
            await bot.send_message(
                chat_id,
                f"🎰 ИГРОВОЙ АВТОМАТ MOXXI 🎰\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"| {s1} | {s2} | {s3} |\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💔 Не повезло! Вы проиграли {bet:,} 🌑.",
                buttons=get_main_keyboard_max()
            )
        return

    # ═══════════════════════════════════════════════════════════
    # 7. ШАХТА И РЫБАЛКА
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("шахта", "копать"):
        earned = random.randint(250, 950)
        await db.add_balance(db_uid, earned)
        await db.add_xp(db_uid, 20)
        await bot.send_message(chat_id, f"⛏ Вы спустились в шахту и добыли ценных самоцветов на +{earned:,} 🌑 монет! (+20 XP)", buttons=get_main_keyboard_max())
        return

    elif cmd in ("рыбалка", "рыбачить"):
        earned = random.randint(300, 1100)
        await db.add_balance(db_uid, earned)
        await db.add_xp(db_uid, 25)
        fish = random.choice(["Золотого Осетра", "Неонового Карпа", "Тайменя", "Электрического Угря", "Судака"])
        await bot.send_message(chat_id, f"🎣 Вы поймали редкого «{fish}» и продали его за +{earned:,} 🌑 монет! (+25 XP)", buttons=get_main_keyboard_max())
        return

    # ═══════════════════════════════════════════════════════════
    # 8. РЕЙДОВЫЙ БОСС
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("босс", "рейд"):
        boss = await db.get_chat_boss(db_cid)
        if not boss:
            await bot.send_message(chat_id, "🐉 В беседе сейчас нет активного босса. Напишите «призвать босса»!")
            return

        sub = args.lower().strip()
        if sub in ("ударить", "атака", "бить") or cmd == "ударить":
            dmg = random.randint(350, 1200)
            res = await db.attack_chat_boss(db_cid, db_uid, dmg)
            if res.get("killed"):
                rew = res.get("reward", 50000)
                await bot.send_message(chat_id, f"🎉 БОСС ПОВЕРЖЕН! Вы нанесли финальный удар на {dmg} урона и получили награду: +{rew:,} 🌑 монет!")
            else:
                left_hp = res.get("hp_left", 0)
                await bot.send_message(chat_id, f"⚔️ Вы нанесли {dmg} урона боссу! У босса осталось: {left_hp:,} HP.")
            return

        hp = boss.get("hp", 0)
        max_hp = boss.get("max_hp", 50000)
        percent = max(0, min(100, int((hp / max_hp) * 100)))
        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))

        msg = (
            f"🐉 РЕЙДОВЫЙ БОСС БЕСЕДЫ 🐉\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👹 Имя: {boss.get('name', 'Древний Дракон')}\n"
            f"❤️ Здоровье: [{bar}] {percent}% ({hp:,} / {max_hp:,} HP)\n\n"
            f"⚔️ Атакуйте босса вместе с друзьями и забирайте общую казну!"
        )
        buttons = [
            [{"type": "callback", "text": "⚔️ Нанести удар", "payload": "босс бить"}],
            [{"type": "callback", "text": "👑 Меню", "payload": "меню"}]
        ]
        await bot.send_message(chat_id, msg, buttons=buttons)
        return

    # ═══════════════════════════════════════════════════════════
    # 9. ТОП БОГАЧЕЙ
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("топ", "богачи", "лидеры"):
        top_list = await db.fetchall(
            "SELECT user_id, first_name, username, balance FROM users ORDER BY balance DESC LIMIT 10"
        )
        lines = [
            "🏆 ТОП-10 САМЫХ БОГАТЫХ ИГРОКОВ MOXXI 🏆",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, row in enumerate(top_list):
            med = medals[idx] if idx < len(medals) else f"{idx+1}."
            name = row["first_name"] or row["username"] or f"ID {row['user_id']}"
            lines.append(f"{med} {name} — {row['balance']:,} 🌑")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("💰 Зарабатывайте монеты в шахте, бизнесе и казино, чтобы попасть в топ!")
        await bot.send_message(chat_id, "\n".join(lines), buttons=get_main_keyboard_max())
        return

    # ═══════════════════════════════════════════════════════════
    # 10. ВСЕ 12 РАЗДЕЛОВ КОМАНД
    # ═══════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════
    # 🆘 СЛУЖБА ПОДДЕРЖКИ, РЕПОРТЫ И ИДЕИ
    # ═══════════════════════════════════════════════════════════
    elif cmd in ("поддержка", "тикет", "ticket", "баг", "ошибка", "репорт", "жалоба", "идея", "предложение"):
        if not args:
            await bot.send_message(
                chat_id,
                "🆘 Служба заботы и поддержки MOXXI (MAX):\n\n"
                "• Чтобы сообщить о проблеме или баге:\n"
                "  👉 Напишите: «поддержка [описание]» или «баг [описание]»\n\n"
                "• Чтобы предложить крутую идею или улучшение:\n"
                "  👉 Напишите: «идея [текст идеи]»\n\n"
                "• Discord Сервер: https://discord.gg/7hDq4R2q\n"
                "• Telegram Чат: https://t.me/moxxi_chat",
                buttons=get_main_keyboard_max()
            )
            return

        is_idea = cmd in ("идея", "предложение")
        is_bug = cmd in ("баг", "ошибка", "репорт", "жалоба")
        cat = "💡 Идея / Предложение" if is_idea else ("🛠 Баг / Ошибка" if is_bug else "Общее")

        asyncio.create_task(notify_telegram_about_ticket_max(user_id, user_name, args, category=cat))
        asyncio.create_task(notify_discord_about_ticket_max(user_id, user_name, args, category=cat))

        icon = "💡" if is_idea else ("🛠" if is_bug else "🆘")
        label = "Идея" if is_idea else ("Багрепорт" if is_bug else "Тикет")
        await bot.send_message(
            chat_id,
            f"{icon} {label} успешно отправлен администрации!\n\n"
            f"📝 Обращение передано дежурной администрации в Telegram и Discord.\n"
            f"Спасибо за ваш вклад в развитие MOXXI! ❤️",
            buttons=get_main_keyboard_max()
        )
        return

    elif cmd in ("команды", "каталог", "раздел", "разделы"):
        await bot.send_message(chat_id, commands_catalog.get_hub_text(), buttons=get_main_keyboard_max())
        return

    # Другие команды
    await bot.send_message(chat_id, f"🤖 Команда не распознана. Нажмите на кнопки меню или напишите «команды»!", buttons=get_main_keyboard_max())



async def max_support_broadcast_loop(bot: MaxBotClient):
    """Фоновая рассылка каждые 3 часа во все активные чаты MAX."""
    log.info("Запущен воркер автосообщений техподдержки и идей MAX (интервал: 3 часа)...")
    await asyncio.sleep(60)
    while True:
        try:
            now = int(time.time())
            interval = 3 * 3600  # 3 часа = 10800 секунд
            chats = await db.get_all_max_chats()

            broadcast_text = (
                "💜✨ СЛУЖБА ЗАБОТЫ И ПОДДЕРЖКИ MOXXI ✨💜\n"
                "──────────────────────────────────\n"
                "Нашли баг, ошибку или хотите предложить крутую идею для обновления?\n"
                "Мы всегда на связи и ценим каждого игрока нашего сообщества!\n\n"
                "📝 Как обратиться к разработчикам и администрации:\n"
                "• 🆘 Сообщить о баге или проблеме:\n"
                "  👉 Напишите в чат: «поддержка [описание]» или «баг [описание]»\n\n"
                "• 💡 Предложить новую идею или фичу:\n"
                "  👉 Напишите в чат: «идея [текст идеи]»\n\n"
                "🌐 Официальные каналы связи:\n"
                "• 🎮 Discord Сервер Поддержки: https://discord.gg/7hDq4R2q\n"
                "• ✈️ Telegram Чат Игроков: https://t.me/moxxi_chat\n\n"
                "⚡️ Все ваши обращения мгновенно отправляются дежурной команде модераторов в Telegram и Discord! ❤️"
            )

            for ch in chats:
                cid = ch["chat_id"]
                last_ts = ch.get("last_broadcast_ts") or 0
                if (now - last_ts) >= interval:
                    try:
                        await bot.send_message(cid, broadcast_text, buttons=get_main_keyboard_max())
                        await db.update_max_chat_broadcast_ts(cid, now)
                        await asyncio.sleep(1.0)
                    except Exception as e:
                        log.debug("Ошибка авторассылки в чат MAX %s: %s", cid, e)

        except Exception as e:
            log.warning("Исключение в max_support_broadcast_loop: %s", e)
        await asyncio.sleep(60)


async def run_bot():
    token = config.MAX_BOT_TOKEN
    log.info("Запуск бота MOXXI MAX...")
    await db.init()
    bot = MaxBotClient(token)
    log.info("Подключение к платформе MAX успешно! Начало Long Polling...")
    asyncio.create_task(max_support_broadcast_loop(bot))

    while True:
        try:
            updates = await bot.poll_updates()
            for update in updates:
                log.info(">>> ВХОДЯЩИЙ UPDATE MAX: %s", json.dumps(update, ensure_ascii=False))
                
                # 1. ОБРАБОТКА ИНЛАЙН-КНОПОК (CALLBACK)
                upd_type = update.get("update_type")
                callback = update.get("callback")

                if upd_type == "message_callback" or callback:
                    cb = callback or {}
                    cb_id = cb.get("callback_id")
                    if cb_id:
                        asyncio.create_task(bot.answer_callback(cb_id))

                    user = cb.get("user", {})
                    user_id = user.get("user_id", 0)
                    user_name = user.get("first_name") or user.get("name") or "Игрок"
                    payload = cb.get("payload", "").strip()

                    msg_obj = update.get("message", {})
                    recipient = msg_obj.get("recipient", {})
                    chat_id = recipient.get("chat_id") or user_id

                    if payload and user_id and chat_id:
                        log.info("Клик по инлайн-кнопке MAX от [%s|%d]: payload='%s', chat_id=%s", user_name, user_id, payload, chat_id)
                        asyncio.create_task(handle_message(bot, chat_id, user_id, user_name, payload))
                    continue

                # 2. ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ
                msg = update.get("message")
                if msg:
                    sender = msg.get("sender", {})
                    # Игнорируем сообщения от самого бота, чтобы избежать зацикливания!
                    if sender.get("is_bot"):
                        continue

                    user_id = sender.get("user_id") or msg.get("sender_id") or 0
                    user_name = sender.get("first_name") or sender.get("name") or "Игрок"
                    recipient = msg.get("recipient", {})
                    chat_id = recipient.get("chat_id") or msg.get("chat_id") or user_id

                    body = msg.get("body", {})
                    text = body.get("text") or msg.get("text", "")
                    if text and user_id:
                        asyncio.create_task(handle_message(bot, chat_id, user_id, user_name, text))

        except Exception as e:
            log.error("Сбой в цикле Long Polling MAX: %s", e)
            await asyncio.sleep(2.0)


if __name__ == "__main__":
    asyncio.run(run_bot())
