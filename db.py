"""Слой базы данных для VK-бота MOXXI 3.0 (moxxivk).
Подключается к единой базе данных SQLite (iris.db).
Поддерживает: экономику, банк с процентами, кражи/тюрьму, подарки, кейсы,
ранги (1-10), дуэли, шипперинг, кланы, браки, детей, боссов, бизнесы, автопарк, питомцев.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional
import aiosqlite
from dotenv import load_dotenv

_curr_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_curr_dir, ".env"))
load_dotenv()

DB_PATH = os.getenv("DB_PATH", "C:/Users/eiema/OneDrive/Desktop/бот2.0/data/iris.db")

_conn: Optional[aiosqlite.Connection] = None

async def init() -> None:
    global _conn
    if _conn is None:
        _conn = await aiosqlite.connect(DB_PATH)
        _conn.row_factory = aiosqlite.Row
        await _conn.execute("PRAGMA journal_mode=WAL")
        await _conn.execute("PRAGMA synchronous=NORMAL")
        # Создаем недостающие таблицы
        await _conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_pair_of_day (
                chat_id INTEGER NOT NULL,
                date_str TEXT NOT NULL,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                user1_name TEXT,
                user2_name TEXT,
                compatibility INTEGER DEFAULT 80,
                story TEXT,
                PRIMARY KEY (chat_id, date_str)
            )
        """)
        await _conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                pattern TEXT NOT NULL,
                answer TEXT NOT NULL,
                by_id INTEGER NOT NULL,
                ts INTEGER NOT NULL
            )
        """)
        await _conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_vk_settings (
                chat_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (chat_id, key)
            )
        """)
        await _conn.execute("""
            CREATE TABLE IF NOT EXISTS moxxi_gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id INTEGER NOT NULL,
                to_id INTEGER NOT NULL,
                gift_id TEXT NOT NULL,
                gift_name TEXT NOT NULL,
                message TEXT,
                ts INTEGER NOT NULL
            )
        """)
        await _conn.execute("""
            CREATE TABLE IF NOT EXISTS vk_auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                seller_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT DEFAULT 'custom',
                item_id TEXT DEFAULT '',
                start_price INTEGER NOT NULL,
                current_bid INTEGER NOT NULL,
                leader_id INTEGER DEFAULT 0,
                leader_name TEXT DEFAULT '',
                min_step INTEGER NOT NULL,
                ends_at INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at INTEGER NOT NULL
            )
        """)
        await _conn.commit()

async def close() -> None:
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None

def conn() -> aiosqlite.Connection:
    if _conn is None:
        raise RuntimeError("База данных не инициализирована. Вызовите await db.init().")
    return _conn

# ── Пользователи и Профиль ──────────────────────────────────────────────────

async def ensure_user(user_id: int, username: str = "", first_name: str = "") -> None:
    now = int(time.time())
    await conn().execute(
        """INSERT INTO users (user_id, username, first_name, created_at, balance, bank, bank_ts)
           VALUES (?, ?, ?, ?, 1000, 0, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               username = CASE WHEN excluded.username != '' THEN excluded.username ELSE users.username END,
               first_name = CASE WHEN excluded.first_name != '' THEN excluded.first_name ELSE users.first_name END""",
        (user_id, username, first_name, now, now)
    )
    await conn().commit()

async def get_user(user_id: int) -> dict | None:
    async with conn().execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def set_nick(user_id: int, nick: str) -> None:
    await conn().execute("UPDATE users SET nick = ? WHERE user_id = ?", (nick, user_id))
    await conn().commit()

async def add_balance(user_id: int, delta: int) -> None:
    await conn().execute(
        "UPDATE users SET balance = MAX(0, balance + ?) WHERE user_id = ?",
        (delta, user_id)
    )
    await conn().commit()

async def add_xp(user_id: int, delta: int) -> None:
    await conn().execute(
        "UPDATE users SET xp = xp + ? WHERE user_id = ?",
        (delta, user_id)
    )
    await conn().commit()

async def add_crystals(user_id: int, delta: int) -> None:
    await conn().execute(
        "UPDATE users SET crystals = MAX(0, crystals + ?) WHERE user_id = ?",
        (delta, user_id)
    )
    await conn().commit()

# ── Банковская система ──────────────────────────────────────────────────────

async def deposit_to_bank(user_id: int, amount: int) -> bool:
    u = await get_user(user_id)
    if not u or u["balance"] < amount:
        return False
    now = int(time.time())
    await conn().execute(
        """UPDATE users SET balance = balance - ?, bank = bank + ?,
           bank_ts = CASE WHEN bank_ts = 0 THEN ? ELSE bank_ts END
           WHERE user_id = ?""",
        (amount, amount, now, user_id)
    )
    await conn().commit()
    return True

async def withdraw_from_bank(user_id: int, amount: int) -> bool:
    u = await get_user(user_id)
    if not u or u["bank"] < amount:
        return False
    await conn().execute(
        "UPDATE users SET bank = bank - ?, balance = balance + ? WHERE user_id = ?",
        (amount, amount, user_id)
    )
    await conn().commit()
    return True

async def apply_bank_interest(user_id: int) -> int:
    u = await get_user(user_id)
    if not u or u.get("bank", 0) <= 0:
        return 0
    now = int(time.time())
    last_ts = u.get("bank_ts", 0) or 0
    if now - last_ts >= 86400:
        interest = min(100000, int(u["bank"] * 0.05))  # 5% в сутки, макс 100к
        await conn().execute(
            "UPDATE users SET bank = bank + ?, bank_ts = ? WHERE user_id = ?",
            (interest, now, user_id)
        )
        await conn().commit()
        return interest
    return 0

# ── Тюрьма и КПЗ ────────────────────────────────────────────────────────────

async def is_in_jail(user_id: int) -> int:
    async with conn().execute(
        "SELECT ts FROM cooldowns WHERE user_id = ? AND key = 'in_jail'",
        (user_id,)
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return 0
        left = int(row["ts"]) - int(time.time())
        return max(0, left)

async def send_to_jail(user_id: int, duration_sec: int = 900) -> None:
    now = int(time.time())
    until_ts = now + duration_sec
    await conn().execute(
        """INSERT INTO cooldowns (user_id, key, ts)
           VALUES (?, 'in_jail', ?)
           ON CONFLICT(user_id, key) DO UPDATE SET ts = excluded.ts""",
        (user_id, until_ts)
    )
    await conn().commit()

async def release_from_jail(user_id: int) -> None:
    await conn().execute("DELETE FROM cooldowns WHERE user_id = ? AND key = 'in_jail'", (user_id,))
    await conn().commit()

# ── Подарки (moxxi_gifts) ───────────────────────────────────────────────────

GIFT_CATALOG = {
    "1": {"id": "rose", "name": "🌹 Букет алых роз", "cost": 3000},
    "2": {"id": "bear", "name": "🧸 Плюшевый мишка", "cost": 8000},
    "3": {"id": "iphone", "name": "📱 iPhone 16 Pro Max", "cost": 50000},
    "4": {"id": "ring", "name": "💍 Кольцо с бриллиантом", "cost": 200000},
    "5": {"id": "crown", "name": "👑 Королевская корона", "cost": 1000000},
}

async def send_gift(from_id: int, to_id: int, gift_id: str, gift_name: str, message: str = "") -> None:
    now = int(time.time())
    await conn().execute(
        "INSERT INTO moxxi_gifts (from_id, to_id, gift_id, gift_name, message, ts) VALUES (?, ?, ?, ?, ?, ?)",
        (from_id, to_id, gift_id, gift_name, message, now)
    )
    await conn().commit()

async def get_user_gifts(user_id: int, limit: int = 5) -> list[dict]:
    async with conn().execute(
        "SELECT * FROM moxxi_gifts WHERE to_id = ? ORDER BY ts DESC LIMIT ?",
        (user_id, limit)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

# ── Иерархия и Ранги (1-10) ─────────────────────────────────────────────────

async def get_user_rank(chat_id: int, user_id: int) -> int:
    async with conn().execute(
        "SELECT rank FROM ranks WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id)
    ) as cur:
        row = await cur.fetchone()
        return int(row["rank"]) if row else 0

async def set_user_rank(chat_id: int, user_id: int, rank: int, granted_by: int = 0) -> None:
    now = int(time.time())
    if rank <= 0:
        await conn().execute("DELETE FROM ranks WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    else:
        await conn().execute(
            """INSERT INTO ranks (chat_id, user_id, rank, granted_by, ts)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(chat_id, user_id) DO UPDATE SET
                   rank = excluded.rank, granted_by = excluded.granted_by, ts = excluded.ts""",
            (chat_id, user_id, rank, granted_by, now)
        )
    await conn().commit()

async def get_chat_staff_list(chat_id: int) -> list[dict]:
    async with conn().execute(
        "SELECT user_id, rank, granted_by FROM ranks WHERE chat_id = ? AND rank >= 1 ORDER BY rank DESC",
        (chat_id,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

# ── Кланы ───────────────────────────────────────────────────────────────────

async def create_clan(name: str, owner_id: int) -> int:
    now = int(time.time())
    async with conn().execute(
        "INSERT INTO clans (name, owner_id, balance, descr, ts) VALUES (?, ?, 0, '', ?)",
        (name, owner_id, now)
    ) as cur:
        clan_id = cur.lastrowid
        await conn().execute(
            "INSERT INTO clan_members (clan_id, user_id, ts) VALUES (?, ?, ?)",
            (clan_id, owner_id, now)
        )
        await conn().commit()
        return int(clan_id)

async def get_clan(clan_id: int) -> dict | None:
    async with conn().execute("SELECT * FROM clans WHERE id = ?", (clan_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def get_user_clan(user_id: int) -> dict | None:
    async with conn().execute(
        """SELECT c.* FROM clans c
           JOIN clan_members cm ON c.id = cm.clan_id
           WHERE cm.user_id = ?""",
        (user_id,)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def get_top_clans(limit: int = 10) -> list[dict]:
    async with conn().execute(
        """SELECT c.*, COUNT(cm.user_id) as members_count FROM clans c
           LEFT JOIN clan_members cm ON c.id = cm.clan_id
           GROUP BY c.id ORDER BY c.balance DESC LIMIT ?""",
        (limit,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def add_clan_balance(clan_id: int, delta: int) -> None:
    await conn().execute(
        "UPDATE clans SET balance = MAX(0, balance + ?) WHERE id = ?",
        (delta, clan_id)
    )
    await conn().commit()

async def join_clan(clan_id: int, user_id: int) -> None:
    now = int(time.time())
    await conn().execute(
        "INSERT INTO clan_members (clan_id, user_id, ts) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
        (clan_id, user_id, now)
    )
    await conn().commit()

async def leave_clan(user_id: int) -> None:
    await conn().execute("DELETE FROM clan_members WHERE user_id = ?", (user_id,))
    await conn().commit()

async def get_clan_members_count(clan_id: int) -> int:
    async with conn().execute(
        "SELECT COUNT(*) as c FROM clan_members WHERE clan_id = ?",
        (clan_id,)
    ) as cur:
        row = await cur.fetchone()
        return row["c"] if row else 0

# ── Браки и Дети ────────────────────────────────────────────────────────────

async def get_marriage(user_id: int) -> dict | None:
    async with conn().execute(
        "SELECT * FROM relationships WHERE user1_id = ? OR user2_id = ?",
        (user_id, user_id)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def create_marriage(user1_id: int, user2_id: int) -> int:
    now = int(time.time())
    async with conn().execute(
        """INSERT INTO relationships (user1_id, user2_id, created_at, xp, level, soothe_points, soothe_last_ts)
           VALUES (?, ?, ?, 0, 1, 100, ?)""",
        (user1_id, user2_id, now, now)
    ) as cur:
        rel_id = cur.lastrowid
        await conn().execute("UPDATE users SET married_to = ?, married_at = ? WHERE user_id = ?", (user2_id, now, user1_id))
        await conn().execute("UPDATE users SET married_to = ?, married_at = ? WHERE user_id = ?", (user1_id, now, user2_id))
        await conn().commit()
        return int(rel_id)

async def divorce(user_id: int) -> bool:
    m = await get_marriage(user_id)
    if not m:
        return False
    rel_id = m["id"]
    u1, u2 = m["user1_id"], m["user2_id"]
    await conn().execute("DELETE FROM relationships WHERE id = ?", (rel_id,))
    await conn().execute("DELETE FROM relationship_children WHERE rel_id = ?", (rel_id,))
    await conn().execute("UPDATE users SET married_to = 0, married_at = 0 WHERE user_id IN (?, ?)", (u1, u2))
    await conn().commit()
    return True

async def get_child(rel_id: int) -> dict | None:
    async with conn().execute(
        "SELECT * FROM relationship_children WHERE rel_id = ?",
        (rel_id,)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def create_child(rel_id: int, name: str, gender: str) -> int:
    now = int(time.time())
    async with conn().execute(
        """INSERT INTO relationship_children
           (rel_id, name, gender, born_at, satiety, happiness, health, growth_stage, xp, last_fed_ts, last_play_ts)
           VALUES (?, ?, ?, ?, 100, 100, 100, 1, 0, ?, ?)""",
        (rel_id, name, gender, now, now, now)
    ) as cur:
        await conn().commit()
        return int(cur.lastrowid)

async def feed_child(child_id: int) -> None:
    now = int(time.time())
    await conn().execute(
        "UPDATE relationship_children SET satiety = MIN(100, satiety + 30), xp = xp + 20, last_fed_ts = ? WHERE id = ?",
        (now, child_id)
    )
    await conn().commit()

async def play_child(child_id: int) -> None:
    now = int(time.time())
    await conn().execute(
        "UPDATE relationship_children SET happiness = MIN(100, happiness + 30), xp = xp + 25, last_play_ts = ? WHERE id = ?",
        (now, child_id)
    )
    await conn().commit()

# ── Рейдовые Боссы беседы ───────────────────────────────────────────────────

async def get_chat_boss(chat_id: int) -> dict | None:
    async with conn().execute(
        "SELECT * FROM chat_boss WHERE chat_id = ? AND active = 1",
        (chat_id,)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def spawn_chat_boss(chat_id: int, boss_name: str, boss_icon: str, level: int, max_hp: int, reward_pool: int) -> None:
    now = int(time.time())
    await conn().execute(
        """INSERT INTO chat_boss (chat_id, boss_name, boss_icon, boss_level, max_hp, current_hp, reward_pool, reward_xp, spawn_time, active)
           VALUES (?, ?, ?, ?, ?, ?, ?, 500, ?, 1)
           ON CONFLICT(chat_id) DO UPDATE SET
               boss_name=excluded.boss_name, boss_icon=excluded.boss_icon, boss_level=excluded.boss_level,
               max_hp=excluded.max_hp, current_hp=excluded.current_hp, reward_pool=excluded.reward_pool,
               spawn_time=excluded.spawn_time, active=1""",
        (chat_id, boss_name, boss_icon, level, max_hp, max_hp, reward_pool, now)
    )
    await conn().execute("DELETE FROM boss_damage WHERE chat_id = ?", (chat_id,))
    await conn().commit()

async def attack_chat_boss(chat_id: int, user_id: int, dmg: int) -> tuple[int, bool, int]:
    now = int(time.time())
    boss = await get_chat_boss(chat_id)
    if not boss:
        return 0, False, 0

    new_hp = max(0, boss["current_hp"] - dmg)
    is_dead = new_hp <= 0

    if is_dead:
        await conn().execute("UPDATE chat_boss SET current_hp = 0, active = 0 WHERE chat_id = ?", (chat_id,))
    else:
        await conn().execute("UPDATE chat_boss SET current_hp = ? WHERE chat_id = ?", (new_hp, chat_id))

    await conn().execute(
        """INSERT INTO boss_damage (chat_id, user_id, damage, attacks_count, last_attack_ts)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(chat_id, user_id) DO UPDATE SET
               damage = damage + excluded.damage,
               attacks_count = attacks_count + 1,
               last_attack_ts = excluded.last_attack_ts""",
        (chat_id, user_id, dmg, now)
    )
    await conn().commit()
    return new_hp, is_dead, dmg

async def get_boss_ranking(chat_id: int) -> list[dict]:
    async with conn().execute(
        "SELECT * FROM boss_damage WHERE chat_id = ? ORDER BY damage DESC LIMIT 10",
        (chat_id,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

# ── Масштабная система предприятий (40 уровней до 10 000 Lvl) ───────────────

BIZ_CATALOG: dict[str, dict] = {
    # ── Tier 1: Начальные предприятия (Lvl 1 - 5) ──
    "farm": {"id": 1, "name": "🌾 Ферма", "cost": 5_000, "daily_income": 900, "req_lvl": 1, "desc": "Выращивание экологических культур"},
    "house": {"id": 2, "name": "🏠 Дом в аренду", "cost": 18_000, "daily_income": 2_800, "req_lvl": 2, "desc": "Сдача коттеджа жильцам"},
    "factory": {"id": 3, "name": "🏭 Завод электроники", "cost": 60_000, "daily_income": 8_500, "req_lvl": 3, "desc": "Производство потребительских товаров"},
    "mall": {"id": 4, "name": "🏢 Торговый центр", "cost": 200_000, "daily_income": 25_000, "req_lvl": 4, "desc": "Аренда бутиков и фудкортов"},
    "mine": {"id": 5, "name": "⛏ Крипто-шахта", "cost": 700_000, "daily_income": 80_000, "req_lvl": 5, "desc": "Добыча редких кристаллов и руды"},

    # ── Tier 2: Городская и национальная инфраструктура (Lvl 6 - 15) ──
    "power": {"id": 6, "name": "⚡ Электростанция", "cost": 2_500_000, "daily_income": 260_000, "req_lvl": 6, "desc": "Генерация энергии для мегаполисов"},
    "rig": {"id": 7, "name": "🛢 Нефтяная вышка", "cost": 8_000_000, "daily_income": 800_000, "req_lvl": 8, "desc": "Добыча и переработка чёрного золота"},
    "space": {"id": 8, "name": "🚀 Космодром", "cost": 30_000_000, "daily_income": 2_800_000, "req_lvl": 10, "desc": "Запуск коммерческих шаттлов и ракет"},
    "bank": {"id": 9, "name": "🏦 Банковский конгломерат", "cost": 85_000_000, "daily_income": 7_500_000, "req_lvl": 12, "desc": "Международные финансовые потоки"},
    "orbital": {"id": 10, "name": "🛰 Орбитальная станция", "cost": 220_000_000, "daily_income": 18_000_000, "req_lvl": 15, "desc": "Верфи на околоземной орбите"},

    # ── Tier 3: Межпланетная экспансия (Lvl 18 - 45) ──
    "megacorp": {"id": 11, "name": "💎 Межгалактическая корпорация", "cost": 500_000_000, "daily_income": 40_000_000, "req_lvl": 18, "desc": "Торговые пути через звёздные сектора"},
    "dyson": {"id": 12, "name": "🌌 Сфера Дайсона", "cost": 1_200_000_000, "daily_income": 95_000_000, "req_lvl": 22, "desc": "Мегаструктура вокруг звезды"},
    "mars_colony": {"id": 13, "name": "🪐 Колония на Марсе", "cost": 2_800_000_000, "daily_income": 210_000_000, "req_lvl": 26, "desc": "Терраформирование красной планеты"},
    "collider": {"id": 14, "name": "⚛️ Термоядерный коллайдер", "cost": 6_500_000_000, "daily_income": 480_000_000, "req_lvl": 30, "desc": "Синтез антивещества и тёмных частиц"},
    "quantum_lab": {"id": 15, "name": "🧬 Квантовый биокомплекс", "cost": 15_000_000_000, "daily_income": 1_100_000_000, "req_lvl": 35, "desc": "Исследования квантового бессмертия"},
    "star_fleet": {"id": 16, "name": "🛸 Флот Звёздных Разрушителей", "cost": 35_000_000_000, "daily_income": 2_400_000_000, "req_lvl": 40, "desc": "Защита секторов и добыча с комет"},
    "stargate": {"id": 17, "name": "🌠 Звёздные врата Варпа", "cost": 80_000_000_000, "daily_income": 5_200_000_000, "req_lvl": 45, "desc": "Мгновенные гиперпространственные переходы"},

    # ── Tier 4: Астрофизические мегаструктуры (Lvl 50 - 85) ──
    "black_hole": {"id": 18, "name": "🌀 Генератор Чёрных Дыр", "cost": 190_000_000_000, "daily_income": 12_000_000_000, "req_lvl": 50, "desc": "Гравитационная добыча энергии сингулярности"},
    "chrono_lab": {"id": 19, "name": "🔮 Хроно-лаборатория времени", "cost": 450_000_000_000, "daily_income": 28_000_000_000, "req_lvl": 55, "desc": "Манипуляции с временным континуумом"},
    "dark_matter": {"id": 20, "name": "💫 Фабрика Тёмной материи", "cost": 1_000_000_000_000, "daily_income": 60_000_000_000, "req_lvl": 60, "desc": "Переработка невидимой массы космоса"},
    "alliance": {"id": 21, "name": "🌌 Галактический Альянс", "cost": 2_500_000_000_000, "daily_income": 145_000_000_000, "req_lvl": 65, "desc": "Союз миллиардов цивилизаций"},
    "quasar": {"id": 22, "name": "☀️ Звёздный кузнец квазаров", "cost": 6_000_000_000_000, "daily_income": 340_000_000_000, "req_lvl": 70, "desc": "Ковка материи в эпицентрах квазаров"},
    "singularity": {"id": 23, "name": "🕳 Энергостанция Сингулярности", "cost": 15_000_000_000_000, "daily_income": 820_000_000_000, "req_lvl": 75, "desc": "Бесконечный источник из горизонта событий"},
    "ring_worlds": {"id": 24, "name": "🪐 «Кольцо Миров»", "cost": 38_000_000_000_000, "daily_income": 2_000_000_000_000, "req_lvl": 80, "desc": "Обитаемое кольцо вокруг звезды"},
    "mind_matrix": {"id": 25, "name": "🧬 Матрица Перерождения Разума", "cost": 95_000_000_000_000, "daily_income": 4_800_000_000_000, "req_lvl": 85, "desc": "Оцифровка сознаний целых планет"},

    # ── Tier 5: Космические Абсолюты (Lvl 90 - 100) ──
    "supercluster": {"id": 26, "name": "🌌 Сверхскопление Вселенной", "cost": 240_000_000_000_000, "daily_income": 11_500_000_000_000, "req_lvl": 90, "desc": "Связка сотен галактических скоплений"},
    "void_throne": {"id": 27, "name": "👑 Трон Властелина Пространства", "cost": 600_000_000_000_000, "daily_income": 27_500_000_000_000, "req_lvl": 93, "desc": "Управление тканью космической пустоты"},
    "multiverse_core": {"id": 28, "name": "♾ Ядро Мультивселенной", "cost": 1_500_000_000_000_000, "daily_income": 65_000_000_000_000, "req_lvl": 96, "desc": "Точка ветвления бесконечных измерений"},
    "reality_forge": {"id": 29, "name": "🌠 Творец Реальностей", "cost": 4_000_000_000_000_000, "daily_income": 165_000_000_000_000, "req_lvl": 98, "desc": "Создание новых физических законов"},
    "omniverse": {"id": 30, "name": "👑 Омниверсум Создателя", "cost": 10_000_000_000_000_000, "daily_income": 400_000_000_000_000, "req_lvl": 100, "desc": "Единое полотно всех мыслимых миров"},

    # ── Tier 6: Божественные Титаны (Lvl 250 - 10000) ──
    "god_cradle": {"id": 31, "name": "🏛 Колыбель Богов", "cost": 25_000_000_000_000_000, "daily_income": 950_000_000_000_000, "req_lvl": 250, "desc": "Зарождение высших сущностей бытия"},
    "quantum_absolute": {"id": 32, "name": "🔮 Квантовый Абсолют", "cost": 75_000_000_000_000_000, "daily_income": 2_800_000_000_000_000, "req_lvl": 500, "desc": "Преодоление законов времени и энтропии"},
    "hyper_ark": {"id": 33, "name": "🛸 Гипер-Ковчег Миров", "cost": 250_000_000_000_000_000, "daily_income": 9_000_000_000_000_000, "req_lvl": 1000, "desc": "Спасение цивилизаций сквозь Большие Взрывы"},
    "world_engine": {"id": 34, "name": "⚙️ Титанический Двигатель", "cost": 800_000_000_000_000_000, "daily_income": 28_000_000_000_000_000, "req_lvl": 2000, "desc": "Машина, вращающая оси вселенных"},
    "chrono_singularity": {"id": 35, "name": "⌛️ Хроно-Сингулярность", "cost": 2_500_000_000_000_000_000, "daily_income": 90_000_000_000_000_000, "req_lvl": 3500, "desc": "Управление стрелой времени"},
    "galactic_hive": {"id": 36, "name": "🧠 Галактический Сверхразум", "cost": 8_000_000_000_000_000_000, "daily_income": 280_000_000_000_000_000, "req_lvl": 5000, "desc": "Нейросеть квантового сознания метагалактики"},
    "infinity_matrix": {"id": 37, "name": "💠 Матрица Бесконечности", "cost": 25_000_000_000_000_000_000, "daily_income": 850_000_000_000_000_000, "req_lvl": 6500, "desc": "Моделирование параллельных мультиверсов"},
    "dark_nexus": {"id": 38, "name": "🌑 Нексус Тёмной Материи", "cost": 80_000_000_000_000_000_000, "daily_income": 2_600_000_000_000_000_000, "req_lvl": 8000, "desc": "Неисчерпаемый источник первозданной антиматерии"},
    "primordial_supernova": {"id": 39, "name": "💥 Сверхновая Первоздания", "cost": 250_000_000_000_000_000_000, "daily_income": 8_000_000_000_000_000_000, "req_lvl": 9200, "desc": "Управляемый Большой Взрыв богатств"},
    "architect_throne": {"id": 40, "name": "👑 Трон Архитектора Реальности", "cost": 1_000_000_000_000_000_000_000, "daily_income": 30_000_000_000_000_000_000, "req_lvl": 10000, "desc": "Престол Истинного Творца всего сущего во всех временах"},
}

BIZ_ALIASES: dict[str, str] = {
    "coffee": "farm", "cafe": "farm", "кофейня": "farm", "кафе": "farm",
    "pizza": "house", "pizzeria": "house", "пиццерия": "house",
    "gas": "factory", "autoservice": "factory", "азс": "factory", "автозаправка": "factory",
    "it": "mall", "тц": "mall", "торговый": "mall",
}

async def get_user_businesses(user_id: int) -> list[dict]:
    async with conn().execute(
        "SELECT * FROM user_businesses WHERE user_id = ?",
        (user_id,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def buy_business(user_id: int, biz_key: str) -> bool:
    real_key = BIZ_ALIASES.get(biz_key, biz_key)
    if real_key not in BIZ_CATALOG:
        return False
    now = int(time.time())
    await conn().execute(
        """INSERT INTO user_businesses (user_id, biz_key, count, last_collect)
           VALUES (?, ?, 1, ?)
           ON CONFLICT(user_id, biz_key) DO UPDATE SET count = count + 1""",
        (user_id, real_key, now)
    )
    await conn().commit()
    return True

async def collect_business_profit(user_id: int) -> int:
    now = int(time.time())
    b_rows = await get_user_businesses(user_id)
    if not b_rows:
        return 0

    total_profit = 0
    for b in b_rows:
        key = b["biz_key"]
        real_key = BIZ_ALIASES.get(key, key)
        if real_key in BIZ_CATALOG:
            last_c = b.get("last_collect", 0) or 0
            diff_hours = (now - last_c) / 3600.0
            if diff_hours >= 1.0:
                hours_capped = min(24.0, diff_hours)
                hourly_inc = BIZ_CATALOG[real_key]["daily_income"] / 24.0
                profit = int(hourly_inc * hours_capped * b.get("count", 1))
                total_profit += profit

    if total_profit > 0:
        await conn().execute("UPDATE user_businesses SET last_collect = ? WHERE user_id = ?", (now, user_id))
        await add_balance(user_id, total_profit)
        await add_xp(user_id, min(500, max(25, len(b_rows) * 15)))
    return total_profit

# ── Автопарк / Гараж ────────────────────────────────────────────────────────

CAR_CATALOG = {
    "vesta": {"name": "🚗 Lada Vesta Sport", "cost": 30000},
    "bmw": {"name": "🚙 BMW M5 F90 CS", "cost": 180000},
    "porsche": {"name": "🏎 Porsche 911 Turbo S", "cost": 650000},
    "lambo": {"name": "🏎 Lamborghini Aventador SVJ", "cost": 1800000},
    "bugatti": {"name": "🚀 Bugatti Chiron Super Sport", "cost": 6000000},
}

async def get_user_cars(user_id: int) -> list[dict]:
    async with conn().execute(
        "SELECT * FROM user_cars WHERE user_id = ?",
        (user_id,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def buy_car(user_id: int, car_key: str) -> bool:
    if car_key not in CAR_CATALOG:
        return False
    now = int(time.time())
    await conn().execute(
        "INSERT INTO user_cars (user_id, car_key, bought_at, is_active) VALUES (?, ?, ?, 1)",
        (user_id, car_key, now)
    )
    await conn().commit()
    return True

# ── Питомцы ─────────────────────────────────────────────────────────────────

PET_CATALOG = {
    "cat": {"name": "Котёнок", "icon": "🐱", "cost": 20000},
    "dog": {"name": "Хаски", "icon": "🐶", "cost": 45000},
    "fox": {"name": "Лисичка", "icon": "🦊", "cost": 120000},
    "dragon": {"name": "Дракончик", "icon": "🐲", "cost": 600000},
}

async def get_user_pet(user_id: int) -> dict | None:
    async with conn().execute(
        "SELECT * FROM user_pets WHERE user_id = ?",
        (user_id,)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def buy_pet(user_id: int, pet_type: str, pet_name: str) -> bool:
    if pet_type not in PET_CATALOG:
        return False
    now = int(time.time())
    await conn().execute(
        """INSERT INTO user_pets (user_id, pet_type, pet_name, level, xp, hunger, last_feed)
           VALUES (?, ?, ?, 1, 0, 100, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               pet_type=excluded.pet_type, pet_name=excluded.pet_name, level=1, xp=0, hunger=100""",
        (user_id, pet_type, pet_name, now)
    )
    await conn().commit()
    return True

async def feed_pet(user_id: int) -> None:
    now = int(time.time())
    await conn().execute(
        "UPDATE user_pets SET hunger = 100, xp = xp + 30, last_feed = ? WHERE user_id = ?",
        (now, user_id)
    )
    await conn().commit()

# ── Кулдауны, Варны, Триггеры и Общие функции ──────────────────────────────

async def cooldown_left(user_id: int, key: str, duration_sec: int) -> int:
    async with conn().execute(
        "SELECT ts FROM cooldowns WHERE user_id = ? AND key = ?",
        (user_id, key)
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return 0
        now = int(time.time())
        left = int(row["ts"]) + duration_sec - now
        return max(0, left)

async def set_cooldown(user_id: int, key: str, duration_sec: int = 0) -> None:
    now = int(time.time())
    await conn().execute(
        """INSERT INTO cooldowns (user_id, key, ts)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id, key) DO UPDATE SET ts = excluded.ts""",
        (user_id, key, now)
    )
    await conn().commit()

async def get_pair_of_day(chat_id: int, date_str: str) -> dict | None:
    async with conn().execute(
        "SELECT * FROM chat_pair_of_day WHERE chat_id = ? AND date_str = ?",
        (chat_id, date_str)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def save_pair_of_day(chat_id: int, date_str: str, u1_id: int, u2_id: int, u1_name: str, u2_name: str, compatibility: int, story: str) -> None:
    await conn().execute(
        """INSERT INTO chat_pair_of_day (chat_id, date_str, user1_id, user2_id, user1_name, user2_name, compatibility, story)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(chat_id, date_str) DO UPDATE SET
               user1_id=excluded.user1_id, user2_id=excluded.user2_id,
               user1_name=excluded.user1_name, user2_name=excluded.user2_name,
               compatibility=excluded.compatibility, story=excluded.story""",
        (chat_id, date_str, u1_id, u2_id, u1_name, u2_name, compatibility, story)
    )
    await conn().commit()

async def add_warn(chat_id: int, user_id: int, admin_id: int, reason: str = "") -> int:
    now = int(time.time())
    await conn().execute(
        "INSERT INTO warns (chat_id, user_id, admin_id, reason, ts) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_id, admin_id, reason, now)
    )
    await conn().commit()
    return await get_warns_count(chat_id, user_id)

async def remove_warn(chat_id: int, user_id: int) -> int:
    async with conn().execute(
        "SELECT id FROM warns WHERE chat_id = ? AND user_id = ? ORDER BY ts DESC LIMIT 1",
        (chat_id, user_id)
    ) as cur:
        row = await cur.fetchone()
        if row:
            await conn().execute("DELETE FROM warns WHERE id = ?", (row["id"],))
            await conn().commit()
    return await get_warns_count(chat_id, user_id)

async def get_warns_count(chat_id: int, user_id: int) -> int:
    async with conn().execute(
        "SELECT COUNT(*) as c FROM warns WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id)
    ) as cur:
        row = await cur.fetchone()
        return row["c"] if row else 0

async def reset_warns(chat_id: int, user_id: int) -> None:
    await conn().execute("DELETE FROM warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    await conn().commit()

async def set_chat_setting(chat_id: int, key: str, value: str) -> None:
    await conn().execute(
        """INSERT INTO chat_vk_settings (chat_id, key, value)
           VALUES (?, ?, ?)
           ON CONFLICT(chat_id, key) DO UPDATE SET value = excluded.value""",
        (chat_id, key, value)
    )
    await conn().commit()

async def get_chat_setting(chat_id: int, key: str, default: str = "") -> str:
    async with conn().execute(
        "SELECT value FROM chat_vk_settings WHERE chat_id = ? AND key = ?",
        (chat_id, key)
    ) as cur:
        row = await cur.fetchone()
        return row["value"] if row else default

async def add_chat_trigger(chat_id: int, pattern: str, answer: str, by_id: int) -> None:
    now = int(time.time())
    await conn().execute(
        "DELETE FROM chat_triggers WHERE chat_id = ? AND pattern = ?",
        (chat_id, pattern.lower().strip())
    )
    await conn().execute(
        "INSERT INTO chat_triggers (chat_id, pattern, answer, by_id, ts) VALUES (?, ?, ?, ?, ?)",
        (chat_id, pattern.lower().strip(), answer, by_id, now)
    )
    await conn().commit()

async def remove_chat_trigger(chat_id: int, pattern: str) -> bool:
    cur = await conn().execute(
        "DELETE FROM chat_triggers WHERE chat_id = ? AND pattern = ?",
        (chat_id, pattern.lower().strip())
    )
    await conn().commit()
    return cur.rowcount > 0

async def get_chat_triggers(chat_id: int) -> list[dict]:
    async with conn().execute(
        "SELECT * FROM chat_triggers WHERE chat_id = ? ORDER BY ts ASC LIMIT 30",
        (chat_id,)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def find_chat_trigger_answer(chat_id: int, text: str) -> str | None:
    clean = text.lower().strip()
    async with conn().execute(
        "SELECT pattern, answer FROM chat_triggers WHERE chat_id = ?",
        (chat_id,)
    ) as cur:
        rows = await cur.fetchall()
        for r in rows:
            pat = r["pattern"]
            if clean == pat or (len(pat) > 3 and pat in clean):
                return r["answer"]
    return None

async def create_support_ticket(user_id: int, user_name: str, text: str, status: str = "open", platform: str = "vk", platform_peer_id: int = 0) -> int:
    now = int(time.time())
    async with conn().execute(
        """INSERT INTO support_tickets (user_id, user_name, text, status, platform, platform_peer_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, user_name, text, status, platform, platform_peer_id, now)
    ) as cur:
        await conn().commit()
        return int(cur.lastrowid)

async def fetchall(query: str, params: tuple = ()) -> list[dict]:
    async with conn().execute(query, params) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ── Аукцион в беседе (VK Auctions) ──────────────────────────────────────────

async def create_vk_auction(
    chat_id: int,
    seller_id: int,
    seller_name: str,
    item_name: str,
    start_price: int,
    min_step: int,
    duration_sec: int = 900,
    item_type: str = "custom",
    item_id: str = ""
) -> int:
    now = int(time.time())
    ends_at = now + duration_sec
    async with conn().execute(
        """INSERT INTO vk_auctions
           (chat_id, seller_id, seller_name, item_name, item_type, item_id, start_price, current_bid, min_step, ends_at, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)""",
        (chat_id, seller_id, seller_name, item_name, item_type, item_id, start_price, start_price, min_step, ends_at, now)
    ) as cur:
        await conn().commit()
        return int(cur.lastrowid)

async def get_active_vk_auctions(chat_id: int | None = None) -> list[dict]:
    now = int(time.time())
    if chat_id:
        q = "SELECT * FROM vk_auctions WHERE chat_id = ? AND status = 'active' AND ends_at > ? ORDER BY ends_at ASC"
        params = (chat_id, now)
    else:
        q = "SELECT * FROM vk_auctions WHERE status = 'active' AND ends_at > ? ORDER BY ends_at ASC"
        params = (now,)
    async with conn().execute(q, params) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def get_vk_auction(auction_id: int) -> dict | None:
    async with conn().execute("SELECT * FROM vk_auctions WHERE id = ?", (auction_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None

async def place_vk_bid(
    auction_id: int,
    bidder_id: int,
    bidder_name: str,
    bid_amount: int
) -> tuple[bool, str, dict | None, dict | None]:
    lot = await get_vk_auction(auction_id)
    if not lot or lot["status"] != "active":
        return False, "Лот не найден или аукцион уже завершён!", None, None

    now = int(time.time())
    if lot["ends_at"] <= now:
        return False, "Время приёма ставок на этот лот истекло!", None, None

    if bidder_id == lot["seller_id"]:
        return False, "Вы не можете делать ставки на свой собственный лот!", None, None

    min_required = lot["current_bid"] + lot["min_step"] if lot["leader_id"] > 0 else lot["start_price"]
    if bid_amount < min_required:
        return False, f"Минимальная ставка: {min_required:,} 🌑!", None, None

    user = await get_user(bidder_id)
    if not user or user["balance"] < bid_amount:
        return False, "У вас недостаточно средств на балансе!", None, None

    await add_balance(bidder_id, -bid_amount)

    prev_leader_info = None
    if lot["leader_id"] > 0 and lot["leader_id"] != bidder_id:
        prev_leader_info = {"id": lot["leader_id"], "name": lot["leader_name"], "amount": lot["current_bid"]}
        await add_balance(lot["leader_id"], lot["current_bid"])

    new_ends_at = lot["ends_at"]
    if new_ends_at - now < 120:
        new_ends_at = now + 120

    await conn().execute(
        """UPDATE vk_auctions
           SET current_bid = ?, leader_id = ?, leader_name = ?, ends_at = ?
           WHERE id = ?""",
        (bid_amount, bidder_id, bidder_name, new_ends_at, auction_id)
    )
    await conn().commit()

    updated_lot = await get_vk_auction(auction_id)
    return True, "Ставка принята!", updated_lot, prev_leader_info

async def finish_vk_auction(auction_id: int) -> dict | None:
    lot = await get_vk_auction(auction_id)
    if not lot or lot["status"] != "active":
        return None

    await conn().execute("UPDATE vk_auctions SET status = 'finished' WHERE id = ?", (auction_id,))
    await conn().commit()

    if lot["leader_id"] > 0:
        payout = int(lot["current_bid"] * 0.95)
        await add_balance(lot["seller_id"], payout)
        await add_xp(lot["seller_id"], 50)
        await add_xp(lot["leader_id"], 75)
    return lot
