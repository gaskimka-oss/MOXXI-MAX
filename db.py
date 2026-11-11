"""Слой базы данных для VK-бота MOXXI 3.0 (moxxivk).
Подключается к единой базе данных SQLite (moxxi_max.db).
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

DB_PATH = os.getenv("DB_PATH") or os.path.join(_curr_dir, "data", "moxxi_max.db")

_conn: Optional[aiosqlite.Connection] = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, cmd TEXT,
    rank INTEGER, enabled INTEGER, by_id INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS ai_pass (
    user_id INTEGER PRIMARY KEY, until INTEGER
);

CREATE TABLE IF NOT EXISTS announcement_votes (
    ann_id      INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    user_name   TEXT NOT NULL,
    vote        TEXT NOT NULL,
    updated_at  INTEGER NOT NULL,
    PRIMARY KEY (ann_id, user_id)
);

CREATE TABLE IF NOT EXISTS announcements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    msg_id      INTEGER NOT NULL DEFAULT 0,
    creator_id  INTEGER NOT NULL,
    title       TEXT NOT NULL,
    text        TEXT NOT NULL,
    event_type  TEXT NOT NULL DEFAULT 'general',
    created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER,
    title TEXT, by_id INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS bans (
    chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL, reason TEXT,
    by_id INTEGER, until INTEGER DEFAULT 0, ts INTEGER,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS blacklisted_chats (
    chat_id     INTEGER PRIMARY KEY,
    reason      TEXT,
    banned_by   INTEGER,
    ts          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT,
    link TEXT, ts INTEGER);

CREATE TABLE IF NOT EXISTS boss_daily_count (
    chat_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, day));

CREATE TABLE IF NOT EXISTS boss_damage (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    damage INTEGER NOT NULL DEFAULT 0,
    attacks_count INTEGER NOT NULL DEFAULT 0,
    last_attack_ts INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS boss_knockouts (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    knocked_out_ts INTEGER NOT NULL,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS bot_daily_activity (
    date    TEXT NOT NULL,
    metric  TEXT NOT NULL,
    val     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, metric)
);

CREATE TABLE IF NOT EXISTS bot_staff (
    user_id     INTEGER PRIMARY KEY,
    rank        INTEGER NOT NULL DEFAULT 1,
    granted_by  INTEGER,
    title       TEXT,
    ts          INTEGER NOT NULL
, warns INTEGER NOT NULL DEFAULT 0, muted_until INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS business_partners (
    chat_id INTEGER NOT NULL,
    biz_key TEXT NOT NULL,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    PRIMARY KEY(chat_id, biz_key, user1_id)
);

CREATE TABLE IF NOT EXISTS business_upgrades (
    user_id INTEGER NOT NULL,
    biz_key TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(user_id, biz_key)
);

CREATE TABLE IF NOT EXISTS casino_big_wins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    game_name TEXT NOT NULL,
    bet INTEGER NOT NULL,
    win_amount INTEGER NOT NULL,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS casino_blacklist (user_id INTEGER PRIMARY KEY, banned_at INTEGER, reason TEXT, by_admin INTEGER);

CREATE TABLE IF NOT EXISTS chat_activity (
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        msg_count INTEGER DEFAULT 0,
        last_msg_ts INTEGER NOT NULL,
        PRIMARY KEY (chat_id, user_id)
    );

CREATE TABLE IF NOT EXISTS chat_antiraid (
    chat_id INTEGER PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    threshold INTEGER NOT NULL DEFAULT 5,
    media_block_seconds INTEGER NOT NULL DEFAULT 0,
    anti_links INTEGER NOT NULL DEFAULT 0,
    slowmode_auto INTEGER NOT NULL DEFAULT 0,
    shield_until INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_birthdays (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    by_id INTEGER NOT NULL DEFAULT 0,
    ts INTEGER NOT NULL,
    UNIQUE(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_boss (
    chat_id INTEGER PRIMARY KEY,
    boss_name TEXT NOT NULL,
    boss_icon TEXT NOT NULL,
    boss_level INTEGER NOT NULL DEFAULT 1,
    max_hp INTEGER NOT NULL,
    current_hp INTEGER NOT NULL,
    reward_pool INTEGER NOT NULL,
    reward_xp INTEGER NOT NULL,
    spawn_time INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    last_msg_id INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS chat_crypto (
    rate REAL NOT NULL DEFAULT 100.0,
    last_update INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_features_2_2 (chat_id INTEGER, feature TEXT, enabled INTEGER DEFAULT 0, PRIMARY KEY (chat_id, feature));

CREATE TABLE IF NOT EXISTS chat_hourly_activity (chat_id INTEGER, day_of_week INTEGER, hour INTEGER, count INTEGER DEFAULT 0, PRIMARY KEY(chat_id, day_of_week, hour));

CREATE TABLE IF NOT EXISTS chat_jackpot (
    chat_id INTEGER PRIMARY KEY,
    pool INTEGER NOT NULL DEFAULT 5000,
    last_winner_id INTEGER,
    last_winner_name TEXT,
    last_winner_amount INTEGER,
    last_win_ts INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_lottery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    tickets INTEGER NOT NULL DEFAULT 1,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_members (
    chat_id   INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    status    TEXT NOT NULL DEFAULT 'member',
    is_member INTEGER NOT NULL DEFAULT 1,
    updated_at INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_mutes (
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        until_ts INTEGER NOT NULL,
        reason TEXT,
        by_id INTEGER NOT NULL,
        PRIMARY KEY (chat_id, user_id)
    );

CREATE TABLE IF NOT EXISTS chat_nicks (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    nick    TEXT NOT NULL,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS chat_pair_of_day (
    chat_id INTEGER NOT NULL,
    date_str TEXT NOT NULL,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    user1_name TEXT NOT NULL,
    user2_name TEXT NOT NULL,
    compatibility INTEGER NOT NULL,
    story TEXT NOT NULL,
    PRIMARY KEY(chat_id, date_str)
);

CREATE TABLE IF NOT EXISTS chat_profiles (
    chat_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    about       TEXT,
    city        TEXT,
    age         TEXT,
    birthday    TEXT,
    hobby       TEXT,
    contact     TEXT,
    real_name   TEXT,
    country     TEXT,
    tz          TEXT,
    family      TEXT,
    nick2       TEXT,
    gender      TEXT,
    custom      TEXT,
    custom_by   INTEGER,
    custom_ts   INTEGER,
    filled      INTEGER NOT NULL DEFAULT 0,
    filled_ts   INTEGER,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_quiz (
    chat_id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options TEXT,
    reward_coins INTEGER NOT NULL DEFAULT 200,
    reward_xp INTEGER NOT NULL DEFAULT 30,
    created_at INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1);

CREATE TABLE IF NOT EXISTS chat_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    quote_text TEXT NOT NULL,
    author_name TEXT NOT NULL,
    adder_name TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_schedule (
    chat_id INTEGER PRIMARY KEY,
    open_at TEXT, close_at TEXT,          -- 'HH:MM' или NULL
    tz_offset INTEGER NOT NULL DEFAULT 3, -- часовой пояс (МСК по умолчанию)
    enabled INTEGER NOT NULL DEFAULT 0,
    last_open TEXT, last_close TEXT);

CREATE TABLE IF NOT EXISTS chat_stats (
    chat_id   INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    messages  INTEGER NOT NULL DEFAULT 0,
    xp        INTEGER NOT NULL DEFAULT 0,
    last_seen INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_themes (chat_id INTEGER PRIMARY KEY, theme TEXT NOT NULL DEFAULT 'rainbow', updated_at INTEGER NOT NULL DEFAULT 0, updated_by INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS chat_treasury (chat_id INTEGER PRIMARY KEY, balance INTEGER NOT NULL DEFAULT 0, updated_at INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS chat_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                pattern TEXT NOT NULL,
                answer TEXT NOT NULL,
                by_id INTEGER NOT NULL,
                ts INTEGER NOT NULL
            );

CREATE TABLE IF NOT EXISTS chat_vk_settings (
                chat_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (chat_id, key)
            );

CREATE TABLE IF NOT EXISTS chats (
    chat_id   INTEGER PRIMARY KEY,
    title     TEXT,
    added_at  INTEGER NOT NULL DEFAULT 0,
    silent    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS clan_alliances (
    clan1_id INTEGER NOT NULL,
    clan2_id INTEGER NOT NULL,
    ts INTEGER NOT NULL,
    PRIMARY KEY(clan1_id, clan2_id)
);

CREATE TABLE IF NOT EXISTS clan_crossban_lock (
    user_id INTEGER PRIMARY KEY,
    ts INTEGER NOT NULL);

CREATE TABLE IF NOT EXISTS clan_districts (
    district_id TEXT PRIMARY KEY,
    clan_id INTEGER NOT NULL,
    captured_ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS clan_groups (
    role TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL UNIQUE,
    title TEXT,
    updated_by INTEGER,
    ts INTEGER);

CREATE TABLE IF NOT EXISTS clan_members (
    clan_id INTEGER NOT NULL, user_id INTEGER NOT NULL PRIMARY KEY, ts INTEGER);

CREATE TABLE IF NOT EXISTS clan_upgrades (
    clan_id INTEGER PRIMARY KEY,
    armory_lvl INTEGER NOT NULL DEFAULT 0,
    treasury_lvl INTEGER NOT NULL DEFAULT 0,
    outpost_lvl INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS clan_wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan1_id INTEGER NOT NULL,
    clan2_id INTEGER NOT NULL,
    clan1_score INTEGER NOT NULL DEFAULT 0,
    clan2_score INTEGER NOT NULL DEFAULT 0,
    prize_pool INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active');

CREATE TABLE IF NOT EXISTS clans (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, owner_id INTEGER,
    balance INTEGER DEFAULT 0, descr TEXT, ts INTEGER);

CREATE TABLE IF NOT EXISTS clown_punishments (chat_id INTEGER, user_id INTEGER, until_ts INTEGER, by_admin INTEGER, PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS cmd_access (
    chat_id INTEGER NOT NULL, cmd TEXT NOT NULL, rank INTEGER NOT NULL DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1, PRIMARY KEY (chat_id, cmd));

CREATE TABLE IF NOT EXISTS cmd_personal (
    chat_id INTEGER NOT NULL, cmd TEXT NOT NULL, user_id INTEGER NOT NULL,
    mode TEXT NOT NULL DEFAULT 'allow',   -- allow | deny
    by_id INTEGER, ts INTEGER, PRIMARY KEY (chat_id, cmd, user_id));

CREATE TABLE IF NOT EXISTS cooldowns (
    user_id INTEGER NOT NULL,
    key     TEXT    NOT NULL,
    ts      INTEGER NOT NULL,
    PRIMARY KEY (user_id, key)
);

CREATE TABLE IF NOT EXISTS daily_quests (
    user_id    INTEGER NOT NULL,
    quest_id   TEXT NOT NULL,
    date       TEXT NOT NULL,
    title      TEXT NOT NULL,
    reward_coins INTEGER NOT NULL,
    reward_xp  INTEGER NOT NULL,
    progress   INTEGER NOT NULL DEFAULT 0,
    target     INTEGER NOT NULL DEFAULT 1,
    claimed    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, quest_id, date)
);

CREATE TABLE IF NOT EXISTS daily_roulette_spins (
    user_id   INTEGER PRIMARY KEY,
    last_spin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_stats (
    day TEXT NOT NULL, chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
    messages INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (day, chat_id, user_id));

CREATE TABLE IF NOT EXISTS daily_streaks (user_id INTEGER PRIMARY KEY, streak INTEGER DEFAULT 1, max_streak INTEGER DEFAULT 1, last_ts INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS daily_user_activity (
    date    TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (date, user_id)
);

CREATE TABLE IF NOT EXISTS daily_wheel_spins (
        user_id INTEGER PRIMARY KEY,
        last_spin INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE IF NOT EXISTS deleted_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    text TEXT NOT NULL,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS disabled_chats (
    chat_id     INTEGER PRIMARY KEY,
    disabled_by INTEGER,
    ts          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS drunk_punishments (chat_id INTEGER, user_id INTEGER, until_ts INTEGER, by_admin INTEGER, PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS duels_stats (
    user_id INTEGER PRIMARY KEY,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    total_earned INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS first_seen (
    chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
    ts INTEGER NOT NULL, PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    UNIQUE(user1_id, user2_id)
);

CREATE TABLE IF NOT EXISTS game_stats (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0,
    games_won INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS giveaway_members (
    gid INTEGER NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY (gid, user_id));

CREATE TABLE IF NOT EXISTS giveaways (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, prize TEXT,
    owner_id INTEGER, until INTEGER, done INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS heist_cooldowns (
        user_id INTEGER PRIMARY KEY,
        last_heist INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE IF NOT EXISTS hidden_chats (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    hidden_by INTEGER,
    ts INTEGER
);

CREATE TABLE IF NOT EXISTS lift_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL, log_id INTEGER, punish_id INTEGER,
    target_id INTEGER, target_name TEXT,
    kind TEXT, reason TEXT,            -- за что было наказание
    by_id INTEGER, by_name TEXT,       -- кто выдал
    lifted_by INTEGER, lifted_name TEXT,   -- кто снял
    ts INTEGER);

CREATE TABLE IF NOT EXISTS log (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action  TEXT,
    amount  INTEGER,
    meta    TEXT,
    ts      INTEGER
);

CREATE TABLE IF NOT EXISTS market (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, kind TEXT,
    amount INTEGER, price INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS market_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL,
    seller_name TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    price INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS marry_requests (
    from_id INTEGER NOT NULL,
    to_id   INTEGER NOT NULL,
    ts      INTEGER NOT NULL,
    PRIMARY KEY (from_id, to_id)
);

CREATE TABLE IF NOT EXISTS mentorships (
    teacher_id INTEGER NOT NULL,
    student_id INTEGER PRIMARY KEY,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS mine_cooldowns (
        user_id INTEGER PRIMARY KEY,
        last_mine INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE IF NOT EXISTS mod_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL, punish_id INTEGER,
    target_id INTEGER, target_name TEXT,
    by_id INTEGER, by_name TEXT,
    kind TEXT, reason TEXT, seconds INTEGER DEFAULT 0,
    context TEXT,              -- переписка вокруг нарушения
    source TEXT,               -- 'админ' | 'автомодерация'
    reviewed INTEGER NOT NULL DEFAULT 0,
    ai_verdict TEXT,           -- ok | soft | harsh | wrong
    ai_score INTEGER DEFAULT 0,
    ai_reason TEXT,
    ai_advice TEXT,
    ts INTEGER);

CREATE TABLE IF NOT EXISTS moxxi_artifacts (
        user_id INTEGER,
        artifact_id INTEGER,
        level INTEGER DEFAULT 1,
        acquired_ts INTEGER,
        PRIMARY KEY (user_id, artifact_id)
    );

CREATE TABLE IF NOT EXISTS moxxi_battle_pass (
        user_id INTEGER PRIMARY KEY,
        season INTEGER DEFAULT 1,
        points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        has_premium INTEGER DEFAULT 0,
        claimed_levels TEXT DEFAULT '[]'
    );

CREATE TABLE IF NOT EXISTS moxxi_corporations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER UNIQUE,
        name TEXT,
        balance INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        branches TEXT DEFAULT '[]',
        last_collect INTEGER DEFAULT 0,
        created_ts INTEGER
    );

CREATE TABLE IF NOT EXISTS moxxi_deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        term_days INTEGER,
        yield_pct REAL,
        open_ts INTEGER,
        expire_ts INTEGER,
        claimed INTEGER DEFAULT 0
    );

CREATE TABLE IF NOT EXISTS moxxi_gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id INTEGER,
        to_id INTEGER,
        gift_id INTEGER,
        gift_name TEXT,
        message TEXT,
        ts INTEGER
    );

CREATE TABLE IF NOT EXISTS moxxi_loans (
        user_id INTEGER PRIMARY KEY,
        amount INTEGER,
        due_amount INTEGER,
        due_ts INTEGER,
        status TEXT DEFAULT 'active'
    );

CREATE TABLE IF NOT EXISTS msg_buffer (
    chat_id INTEGER NOT NULL, msg_id INTEGER NOT NULL,
    user_id INTEGER, user_name TEXT, text TEXT, ts INTEGER,
    PRIMARY KEY (chat_id, msg_id));

CREATE TABLE IF NOT EXISTS mutes (
    chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL, reason TEXT,
    by_id INTEGER, until INTEGER DEFAULT 0, ts INTEGER,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS net_chats (
    net_id INTEGER NOT NULL, chat_id INTEGER NOT NULL, num INTEGER,
    PRIMARY KEY (net_id, chat_id));

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER,
    name TEXT, text TEXT, ts INTEGER);

CREATE TABLE IF NOT EXISTS party_words_game (
    chat_id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    hint TEXT NOT NULL,
    reward_coins INTEGER NOT NULL DEFAULT 200,
    reward_xp INTEGER NOT NULL DEFAULT 25,
    active INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pending_punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    kind TEXT NOT NULL,
    reason TEXT,
    seconds INTEGER NOT NULL DEFAULT 0,
    by_id INTEGER NOT NULL DEFAULT 0,
    ts INTEGER NOT NULL,
    UNIQUE(chat_id, username, kind));

CREATE TABLE IF NOT EXISTS profile_wall (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    text TEXT NOT NULL,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY, about TEXT, city TEXT, age TEXT,
    birthday TEXT, hobby TEXT, contact TEXT,
    real_name TEXT, country TEXT, tz TEXT, family TEXT, nick2 TEXT,
    gender TEXT,               -- пол, если человек его указал
    custom TEXT,               -- описание, вписанное админом вручную
    custom_by INTEGER, custom_ts INTEGER,
    filled INTEGER NOT NULL DEFAULT 0, filled_ts INTEGER);

CREATE TABLE IF NOT EXISTS promocode_activations (
    code TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    ts INTEGER NOT NULL,
    PRIMARY KEY(code, user_id)
);

CREATE TABLE IF NOT EXISTS promocodes (
    code TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    reward INTEGER NOT NULL,
    uses_left INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
    kind TEXT NOT NULL,                   -- mute | ban | warn | kick
    reason TEXT, rule TEXT, seconds INTEGER DEFAULT 0,
    by_id INTEGER, ts INTEGER, active INTEGER NOT NULL DEFAULT 1,
    lifted_by INTEGER, lifted_ts INTEGER);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item TEXT,
    stars INTEGER, amount INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS rank_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER,
    rank INTEGER, by_id INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS ranks (
    chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
    rank INTEGER NOT NULL DEFAULT 0, granted_by INTEGER, ts INTEGER,
    PRIMARY KEY (chat_id, user_id));

CREATE TABLE IF NOT EXISTS relations (
    user_id INTEGER NOT NULL, target_id INTEGER NOT NULL, kind TEXT NOT NULL,
    ts INTEGER, count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, target_id, kind));

CREATE TABLE IF NOT EXISTS relationship_bank (
    rel_id INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    updated_at INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS relationship_children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rel_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    born_at INTEGER NOT NULL,
    care_last_ts INTEGER NOT NULL DEFAULT 0
, satiety INTEGER NOT NULL DEFAULT 80, happiness INTEGER NOT NULL DEFAULT 80, health INTEGER NOT NULL DEFAULT 100, growth_stage INTEGER NOT NULL DEFAULT 1, xp INTEGER NOT NULL DEFAULT 0, toys_count INTEGER NOT NULL DEFAULT 0, clothes_count INTEGER NOT NULL DEFAULT 0, food_count INTEGER NOT NULL DEFAULT 0, last_fed_ts INTEGER NOT NULL DEFAULT 0, last_play_ts INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS relationship_cooldowns (
    rel_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action_key TEXT NOT NULL,
    last_ts INTEGER NOT NULL,
    PRIMARY KEY (rel_id, user_id, action_key)
);

CREATE TABLE IF NOT EXISTS relationship_property (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rel_id INTEGER NOT NULL,
    item_key TEXT NOT NULL,
    item_name TEXT NOT NULL,
    price INTEGER NOT NULL DEFAULT 0,
    bought_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS relationship_rings (
    rel_id INTEGER PRIMARY KEY,
    ring_key TEXT NOT NULL,
    giver_id INTEGER NOT NULL,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    offended_by INTEGER DEFAULT NULL,
    soothe_points INTEGER NOT NULL DEFAULT 0,
    soothe_last_ts INTEGER NOT NULL DEFAULT 0,
    UNIQUE(user1_id, user2_id)
);

CREATE TABLE IF NOT EXISTS rep_daily_count (
    user_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day));

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER,
    target_id INTEGER, text TEXT, status TEXT DEFAULT 'open', ts INTEGER);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT,
    rating INTEGER NOT NULL DEFAULT 5,
    text TEXT NOT NULL,
    item_purchased TEXT,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS royal_decrees (chat_id INTEGER PRIMARY KEY, rule_text TEXT, rule_type TEXT, keyword TEXT, until_ts INTEGER, by_admin INTEGER, punished_count INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS safe_jackpot (
        id INTEGER PRIMARY KEY DEFAULT 1,
        current_code INTEGER DEFAULT 42,
        jackpot_pool INTEGER DEFAULT 50000
    );

CREATE TABLE IF NOT EXISTS scheduled_announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, run_at_ts INTEGER NOT NULL, text TEXT NOT NULL, status TEXT DEFAULT 'pending', created_by INTEGER, created_at INTEGER, sent_chats INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS settings (
    chat_id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT,
    PRIMARY KEY (chat_id, key));

CREATE TABLE IF NOT EXISTS spam_base (
    user_id INTEGER PRIMARY KEY, reason TEXT, by_id INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS staff (
    chat_id  INTEGER NOT NULL,
    username TEXT    NOT NULL,
    name     TEXT,
    rank     INTEGER NOT NULL DEFAULT 1,
    user_id  INTEGER DEFAULT 0,
    left_chat INTEGER NOT NULL DEFAULT 0,
    pos      INTEGER NOT NULL DEFAULT 0,
    ts       INTEGER,
    PRIMARY KEY (chat_id, username));

CREATE TABLE IF NOT EXISTS staff_norms (
    chat_id INTEGER PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    quota INTEGER NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS staff_spy (
    chat_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    by_id INTEGER NOT NULL,
    ts INTEGER NOT NULL,
    PRIMARY KEY(chat_id, target_id)
);

CREATE TABLE IF NOT EXISTS staff_vacations (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    until_ts INTEGER NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS suggestion_votes (
    suggestion_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    vote INTEGER NOT NULL,
    PRIMARY KEY (suggestion_id, user_id)
);

CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    upvotes INTEGER NOT NULL DEFAULT 0,
    downvotes INTEGER NOT NULL DEFAULT 0,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_at INTEGER NOT NULL,
    answered_by INTEGER,
    answered_name TEXT,
    answer_text TEXT,
    answered_at INTEGER,
    ai_answered INTEGER NOT NULL DEFAULT 0
, platform TEXT NOT NULL DEFAULT 'tg', platform_peer_id INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS timers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER,
    text TEXT, fire_at INTEGER, done INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS tournament_members (
    tour_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status  TEXT NOT NULL,                  -- 'yes' | 'no'
    ts      INTEGER NOT NULL,
    PRIMARY KEY (tour_id, user_id)
);

CREATE TABLE IF NOT EXISTS tournament_posts (
    tour_id    INTEGER NOT NULL,
    chat_id    INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    PRIMARY KEY (tour_id, chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS tournaments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,          -- домашний чат турнира
    title       TEXT NOT NULL,
    descr       TEXT,
    start_ts    INTEGER NOT NULL,          -- unix-время начала
    tz_offset   INTEGER NOT NULL DEFAULT 3,
    video_id    TEXT,                       -- file_id видео из Telegram
    created_by  INTEGER,
    active      INTEGER NOT NULL DEFAULT 1, -- идёт сбор
    done        INTEGER NOT NULL DEFAULT 0, -- созыв выполнен
    reminded    INTEGER NOT NULL DEFAULT 0, -- 30-минутное напоминание отправлено
    ts          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, pattern TEXT,
    answer TEXT, action TEXT, by_id INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id INTEGER NOT NULL,
    ach_id TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, ach_id));

CREATE TABLE IF NOT EXISTS user_battlepass (
    user_id INTEGER PRIMARY KEY,
    season INTEGER NOT NULL DEFAULT 1,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    claimed_levels TEXT NOT NULL DEFAULT '',
    is_premium INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_bios (
    user_id INTEGER PRIMARY KEY,
    bio TEXT NOT NULL,
    updated_ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_businesses (
    user_id INTEGER NOT NULL,
    biz_key TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    last_collect INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, biz_key)
);

CREATE TABLE IF NOT EXISTS user_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    car_key TEXT NOT NULL,
    bought_at INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_compliments (
    user_id INTEGER PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0,
    last_given INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_crypto (
    user_id INTEGER PRIMARY KEY,
    amount REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS user_daily_quests (
    user_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    quest_id TEXT NOT NULL,
    quest_title TEXT NOT NULL,
    target_count INTEGER NOT NULL DEFAULT 1,
    current_count INTEGER NOT NULL DEFAULT 0,
    reward_coins INTEGER NOT NULL DEFAULT 500,
    reward_xp INTEGER NOT NULL DEFAULT 100,
    completed INTEGER NOT NULL DEFAULT 0,
    claimed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day, quest_id));

CREATE TABLE IF NOT EXISTS user_deposits (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0,
    last_interest INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS user_dungeon_progress (
    user_id INTEGER PRIMARY KEY,
    floor INTEGER NOT NULL DEFAULT 1,
    room INTEGER NOT NULL DEFAULT 1,
    hp INTEGER NOT NULL DEFAULT 100,
    max_hp INTEGER NOT NULL DEFAULT 100,
    gold_found INTEGER NOT NULL DEFAULT 0,
    xp_found INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 0,
    state_data TEXT,
    last_action_ts INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_fish_catch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fish_type TEXT NOT NULL,
    fish_name TEXT NOT NULL,
    fish_price INTEGER NOT NULL,
    caught_at INTEGER NOT NULL);

CREATE TABLE IF NOT EXISTS user_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    extra TEXT,
    ts INTEGER NOT NULL,
    UNIQUE(user_id, item_id));

CREATE TABLE IF NOT EXISTS user_jobs (
    user_id INTEGER PRIMARY KEY,
    job_key TEXT NOT NULL,
    last_worked INTEGER NOT NULL DEFAULT 0,
    total_earned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_pets (
    user_id INTEGER PRIMARY KEY,
    pet_type TEXT NOT NULL,
    pet_name TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    hunger INTEGER NOT NULL DEFAULT 100,
    last_feed INTEGER NOT NULL DEFAULT 0,
    expedition_until INTEGER NOT NULL DEFAULT 0,
    expedition_type TEXT NOT NULL DEFAULT '',
    expedition_reward TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS user_quests (
        user_id INTEGER NOT NULL,
        day_str TEXT NOT NULL,
        q1_id TEXT,
        q1_cur INTEGER DEFAULT 0,
        q1_done INTEGER DEFAULT 0,
        q2_id TEXT,
        q2_cur INTEGER DEFAULT 0,
        q2_done INTEGER DEFAULT 0,
        q3_id TEXT,
        q3_cur INTEGER DEFAULT 0,
        q3_done INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, day_str)
    );

CREATE TABLE IF NOT EXISTS user_realty (
        user_id INTEGER PRIMARY KEY,
        house_id TEXT NOT NULL,
        purchased_at INTEGER NOT NULL,
        last_rent_ts INTEGER DEFAULT 0
    );

CREATE TABLE IF NOT EXISTS user_titles (
    user_id INTEGER NOT NULL,
    title_id TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, title_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    nick        TEXT,
    balance     INTEGER NOT NULL DEFAULT 0,
    bank        INTEGER NOT NULL DEFAULT 0,
    bank_ts     INTEGER NOT NULL DEFAULT 0,
    xp          INTEGER NOT NULL DEFAULT 0,
    rep         INTEGER NOT NULL DEFAULT 0,
    messages    INTEGER NOT NULL DEFAULT 0,
    married_to  INTEGER,
    married_at  INTEGER,
    banned      INTEGER NOT NULL DEFAULT 0,
    verified    INTEGER NOT NULL DEFAULT 0,
    grams       INTEGER NOT NULL DEFAULT 0,
    created_at  INTEGER NOT NULL DEFAULT 0
, coins INTEGER NOT NULL DEFAULT 0, crystals INTEGER NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS veteran_bonus_claims (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    last_claimed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS vip (
    user_id INTEGER PRIMARY KEY, until INTEGER, level INTEGER DEFAULT 1);

CREATE TABLE IF NOT EXISTS vip_settings (
    user_id INTEGER PRIMARY KEY,
    color_theme TEXT NOT NULL DEFAULT 'default'
);

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
            );

CREATE TABLE IF NOT EXISTS vote_marks (
    vote_id INTEGER NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY (vote_id, user_id));

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, cmd TEXT,
    target_id INTEGER, by_id INTEGER, need INTEGER, ts INTEGER);

CREATE TABLE IF NOT EXISTS warns (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    admin_id INTEGER NOT NULL,
    reason  TEXT,
    ts      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS wedding_gifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rel_id INTEGER NOT NULL,
    giver_id INTEGER NOT NULL,
    giver_name TEXT NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1000,
    ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS word_filters (
    chat_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    action TEXT DEFAULT 'warn',
    PRIMARY KEY (chat_id, word));

CREATE TABLE IF NOT EXISTS yookassa_payments (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    item_key TEXT NOT NULL,
    amount_rub REAL NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ann_chat ON announcements(chat_id, created_at);

CREATE INDEX IF NOT EXISTS idx_buf ON msg_buffer(chat_id, ts);

CREATE INDEX IF NOT EXISTS idx_casino_wins_ts ON casino_big_wins(ts, win_amount);

CREATE INDEX IF NOT EXISTS idx_chat_members_active
    ON chat_members(chat_id, is_member, updated_at);

CREATE INDEX IF NOT EXISTS idx_chat_profiles ON chat_profiles(chat_id, user_id);

CREATE INDEX IF NOT EXISTS idx_chat_quotes_chat ON chat_quotes(chat_id);

CREATE INDEX IF NOT EXISTS idx_daily ON daily_stats(day, chat_id);

CREATE INDEX IF NOT EXISTS idx_friends_u1 ON friends(user1_id);

CREATE INDEX IF NOT EXISTS idx_friends_u2 ON friends(user2_id);

CREATE INDEX IF NOT EXISTS idx_liftlog ON lift_log(chat_id, ts);

CREATE INDEX IF NOT EXISTS idx_log_user ON log(user_id);

CREATE INDEX IF NOT EXISTS idx_market_seller ON market_lots(seller_id);

CREATE INDEX IF NOT EXISTS idx_modlog_chat ON mod_log(chat_id, ts);

CREATE INDEX IF NOT EXISTS idx_pun_chat ON punishments(chat_id, user_id);

CREATE INDEX IF NOT EXISTS idx_rel_u1 ON relationships(user1_id);

CREATE INDEX IF NOT EXISTS idx_rel_u2 ON relationships(user2_id);

CREATE INDEX IF NOT EXISTS idx_stats_chat ON chat_stats(chat_id);

CREATE INDEX IF NOT EXISTS idx_support_status ON support_tickets(status, created_at);

CREATE INDEX IF NOT EXISTS idx_tour_posts ON tournament_posts(tour_id);


"""

async def init() -> None:
    global _conn
    if _conn is None:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        _conn = await aiosqlite.connect(DB_PATH)
        _conn.row_factory = aiosqlite.Row
        await _conn.execute("PRAGMA journal_mode=WAL")
        await _conn.execute("PRAGMA synchronous=NORMAL")
        # Применяем полную схему базы данных
        try:
            await _conn.executescript(SCHEMA)
        except Exception as e:
            import logging
            logging.getLogger("moxxi").warning("Ошибка применения SCHEMA: %s", e)
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
            CREATE TABLE IF NOT EXISTS max_chats (
                chat_id TEXT PRIMARY KEY,
                title TEXT DEFAULT '',
                last_broadcast_ts INTEGER DEFAULT 0
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


# ═══════════════════════════════════════════════════════════════
# 🚗 АВТОСАЛОН И АВТОПАРК (USER_CARS)
# ═══════════════════════════════════════════════════════════════

async def buy_user_car(user_id: int, car_key: str) -> tuple[bool, str]:
    car = CAR_CATALOG.get(car_key)
    if not car:
        return False, "Такой автомобиль не найден в автосалоне!"
    u = await get_user(user_id) or {}
    bal = u.get("balance", 0)
    cost = car["cost"]
    if bal < cost:
        return False, f"Недостаточно средств! Нужно `{cost:,}` 🌑 (у вас `{bal:,}` 🌑)."
    now = int(time.time())
    await add_balance(user_id, -cost)
    await conn().execute(
        "INSERT INTO user_cars (user_id, car_key, bought_at, is_active) VALUES (?, ?, ?, 1)",
        (user_id, car_key, now)
    )
    await conn().commit()
    return True, f"🎉 Поздравляем с покупкой **{car['name']}** за `{cost:,}` 🌑 монет! Машина отправлена в ваш `/гараж`."

# ═══════════════════════════════════════════════════════════════
# 📈 КРИПТОВАЛЮТНАЯ БИРЖА (CHAT_CRYPTO & USER_CRYPTO)
# ═══════════════════════════════════════════════════════════════

async def get_crypto_rate() -> tuple[float, float, int]:
    now = int(time.time())
    async with conn().execute("SELECT rate, last_update FROM chat_crypto LIMIT 1") as cur:
        row = await cur.fetchone()
    if not row:
        init_rate = 150.0
        await conn().execute("INSERT INTO chat_crypto (rate, last_update) VALUES (?, ?)", (init_rate, now))
        await conn().commit()
        return init_rate, 0.0, now

    old_rate = row["rate"]
    last_up = row["last_update"]
    diff = now - last_up
    if diff >= 180:
        factor = 1.0 + random.uniform(-0.07, 0.09)
        new_rate = round(max(10.0, min(10000.0, old_rate * factor)), 2)
        await conn().execute("UPDATE chat_crypto SET rate = ?, last_update = ?", (new_rate, now))
        await conn().commit()
        change = round(((new_rate - old_rate) / old_rate) * 100, 1)
        return new_rate, change, now
    return old_rate, 0.0, last_up

async def get_user_crypto(user_id: int) -> float:
    async with conn().execute("SELECT amount FROM user_crypto WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
        return round(row["amount"], 4) if row else 0.0

async def buy_crypto(user_id: int, amount: float) -> tuple[bool, str]:
    if amount <= 0:
        return False, "Укажите количество больше 0!"
    rate, _, _ = await get_crypto_rate()
    cost = int(amount * rate)
    u = await get_user(user_id) or {}
    bal = u.get("balance", 0)
    if bal < cost:
        return False, f"Недостаточно монет! Требуется `{cost:,}` 🌑 (у вас `{bal:,}` 🌑)."
    await add_balance(user_id, -cost)
    await conn().execute(
        """INSERT INTO user_crypto (user_id, amount) VALUES (?, ?)
           ON CONFLICT(user_id) DO UPDATE SET amount = amount + excluded.amount""",
        (user_id, amount)
    )
    await conn().commit()
    return True, f"✅ Вы успешно приобрели **{amount:.4f} MOX** за `{cost:,}` 🌑 монет по курсу `{rate:,.2f}` 🌑!"

async def sell_crypto(user_id: int, amount: float) -> tuple[bool, str]:
    if amount <= 0:
        return False, "Укажите количество больше 0!"
    cur_mox = await get_user_crypto(user_id)
    if cur_mox < amount:
        return False, f"Недостаточно криптовалюты! У вас только **{cur_mox:.4f} MOX**."
    rate, _, _ = await get_crypto_rate()
    revenue = int(amount * rate)
    await conn().execute("UPDATE user_crypto SET amount = amount - ? WHERE user_id = ?", (amount, user_id))
    await add_balance(user_id, revenue)
    await conn().commit()
    return True, f"💰 Вы успешно продали **{amount:.4f} MOX** и получили `+{revenue:,}` 🌑 монет!"

# ═══════════════════════════════════════════════════════════════
# 🐾 ПИТОМЦЫ: ЭКСПЕДИЦИИ (USER_PETS)
# ═══════════════════════════════════════════════════════════════

async def send_pet_expedition(user_id: int, duration_sec: int = 1800) -> tuple[bool, str]:
    pet = await get_user_pet(user_id)
    if not pet:
        return False, "У вас ещё нет питомца! Заведите его: `/приручить`."
    now = int(time.time())
    if (pet.get("expedition_until") or 0) > now:
        left = pet["expedition_until"] - now
        return False, f"Питомец уже находится в экспедиции! Возврат через **{left // 60} мин. {left % 60} сек.**"
    if (pet.get("hunger") or 0) < 20:
        return False, "Питомец слишком голоден! Сначала покормите его: `/покормить`."
    until = now + duration_sec
    await conn().execute(
        "UPDATE user_pets SET expedition_until = ? WHERE user_id = ?",
        (until, user_id)
    )
    await conn().commit()
    return True, f"🧭 Ваш питомец **{pet['pet_name']}** отправился в опасную экспедицию за сокровищами на **30 минут**!"

async def claim_pet_expedition(user_id: int) -> tuple[bool, str]:
    pet = await get_user_pet(user_id)
    if not pet:
        return False, "У вас нет питомца!"
    now = int(time.time())
    until = pet.get("expedition_until") or 0
    if until == 0:
        return False, "Питомец сейчас дома, а не в походе. Отправьте его: `/экспедиция`!"
    if until > now:
        left = until - now
        return False, f"Питомец ещё в пути! Ждите ещё **{left // 60} мин. {left % 60} сек.**"

    lvl = pet.get("level", 1) or 1
    coins = random.randint(1800, 4200) * lvl
    xp = 60 * lvl
    new_hunger = max(10, (pet.get("hunger", 100) or 100) - 25)
    await conn().execute(
        "UPDATE user_pets SET expedition_until = 0, xp = xp + ?, hunger = ? WHERE user_id = ?",
        (xp, new_hunger, user_id)
    )
    await add_balance(user_id, coins)
    await add_user_xp(user_id, xp)
    await conn().commit()
    return True, f"🎉 Питомец вернулся из экспедиции с сокровищами! Награда: `+{coins:,}` 🌑 монет и `+{xp}` XP!"

# ═══════════════════════════════════════════════════════════════
# 📜 ЕЖЕДНЕВНЫЕ КВЕСТЫ (USER_DAILY_QUESTS)
# ═══════════════════════════════════════════════════════════════

async def get_or_create_daily_quests(user_id: int) -> list[dict]:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with conn().execute(
        "SELECT * FROM user_daily_quests WHERE user_id = ? AND day = ?",
        (user_id, today)
    ) as cur:
        rows = await cur.fetchall()
        if rows:
            return [dict(r) for r in rows]

    templates = [
        ("work", "💼 Отработать смену на работе", 1, 1500, 100),
        ("mine", "⛏ Найти ресурсы в шахте", 2, 2000, 150),
        ("feed", "🍖 Покормить своего питомца", 1, 1200, 80),
        ("slots", "🎰 Испытать удачу в играх", 2, 2500, 200),
    ]
    selected = random.sample(templates, 3)
    for q_id, title, target, r_coins, r_xp in selected:
        await conn().execute(
            """INSERT INTO user_daily_quests (user_id, day, quest_id, quest_title, target_count, current_count, reward_coins, reward_xp, completed, claimed)
               VALUES (?, ?, ?, ?, ?, 0, ?, ?, 0, 0)""",
            (user_id, today, q_id, title, target, r_coins, r_xp)
        )
    await conn().commit()

    async with conn().execute(
        "SELECT * FROM user_daily_quests WHERE user_id = ? AND day = ?",
        (user_id, today)
    ) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def claim_quest_reward(user_id: int, quest_id: str) -> tuple[bool, str]:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with conn().execute(
        "SELECT * FROM user_daily_quests WHERE user_id = ? AND day = ? AND quest_id = ?",
        (user_id, today, quest_id)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return False, "Квест не найден!"
    if not row["completed"]:
        return False, "Квест ещё не завершён!"
    if row["claimed"]:
        return False, "Вы уже забрали награду за этот квест!"

    await conn().execute(
        "UPDATE user_daily_quests SET claimed = 1 WHERE user_id = ? AND day = ? AND quest_id = ?",
        (user_id, today, quest_id)
    )
    coins = row["reward_coins"]
    xp = row["reward_xp"]
    await add_balance(user_id, coins)
    await add_user_xp(user_id, xp)
    await conn().commit()
    return True, f"🎉 Награда получена: `+{coins:,}` 🌑 монет и `+{xp}` XP!"

async def progress_daily_quest(user_id: int, quest_id: str, count: int = 1) -> None:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with conn().execute(
        "SELECT current_count, target_count, completed FROM user_daily_quests WHERE user_id = ? AND day = ? AND quest_id = ?",
        (user_id, today, quest_id)
    ) as cur:
        row = await cur.fetchone()
    if not row or row["completed"]:
        return
    new_c = min(row["target_count"], row["current_count"] + count)
    is_done = 1 if new_c >= row["target_count"] else 0
    await conn().execute(
        "UPDATE user_daily_quests SET current_count = ?, completed = ? WHERE user_id = ? AND day = ? AND quest_id = ?",
        (new_c, is_done, user_id, today, quest_id)
    )
    await conn().commit()


# ── Чаты MAX и рассылки ────────────────────────────────────────────────

async def record_chat_activity(chat_id: str | int, title: str = "") -> None:
    c_str = str(chat_id)
    await conn().execute(
        """INSERT INTO max_chats (chat_id, title)
           VALUES (?, ?)
           ON CONFLICT(chat_id) DO UPDATE SET
               title = CASE WHEN excluded.title != '' THEN excluded.title ELSE max_chats.title END""",
        (c_str, title)
    )
    await conn().commit()

async def get_all_max_chats() -> list[dict]:
    async with conn().execute("SELECT chat_id, title, last_broadcast_ts FROM max_chats") as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def update_max_chat_broadcast_ts(chat_id: str | int, ts: int) -> None:
    c_str = str(chat_id)
    await conn().execute("UPDATE max_chats SET last_broadcast_ts = ? WHERE chat_id = ?", (ts, c_str))
    await conn().commit()
