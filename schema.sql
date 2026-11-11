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

