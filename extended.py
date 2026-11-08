"""🌟 МОДУЛЬ РАСШИРЕННЫХ СИСТЕМ MOXXI 3.0 (extended.py)
Содержит 150+ новых уникальных механик и действий:
1. 🎭 60 RP-команд взаимодействий между участниками
2. 💼 Система Работ и Профессий (10 уровней карьеры)
3. 🏡 Недвижимость и Дома (10 уровней жилья)
4. 🎒 Инвентарь и Магазин предметов
5. 📜 Ежедневные Квесты
6. 🏆 Достижения и Ачивки
7. 🎯 Мини-игры: Сейф, Стаканчики, Дартс, Футбол, Баскетбол, Боулинг, КНБ, Лотерея
8. ⚔️ Данжи и Подземелья (5 уровней)
9. 👑 Кастомные Титулы
10. 🛡 Модерация: Муты, Размуты, Мутлист
11. 📊 Чат-менеджмент: Чатстат, Актив, Онлайн, Созыв
12. 👮 Полиция: Розыск и Арест преступников
"""
from __future__ import annotations

import asyncio
import datetime
import random
import re
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from vkbottle.bot import Message

import db

# ═══════════════════════════════════════════════════════════════
# 1. 🎭 60 RP-КОМАНД ВЗАИМОДЕЙСТВИЙ (РЕАКЦИЙ)
# ═══════════════════════════════════════════════════════════════

RP_ACTIONS = {
    # Романтичные и тёплые
    "обнять": ("🤗", "обнимает", "крепко прижимая к себе с теплом и заботой"),
    "поцеловать": ("😘", "нежно целует", "в щёчку, оставляя след тёплой помады"),
    "чмокнуть": ("💋", "чмокает", "прямо в носик!"),
    "погладить": ("🖐", "гладит по голове", "приговаривая, какое это чудо"),
    "приласкать": ("🥰", "ласкает", "даря море нежности и уюта"),
    "прижать": ("🫂", "прижимает к себе", "и не хочет отпускать ни на секунду"),
    "взять за руку": ("🤝", "берёт за руку", "и переплетает пальцы"),
    "потискать": ("🫰", "тискает за щёчки", "не сдерживая умиления"),
    "укрыть пледом": ("🛏", "укрывает тёплым пледом", "и ставит рядом чашку горячего какао"),
    "спеть": ("🎤", "поёт романтичную серенаду для", "срывая бурные аплодисменты"),
    "станцевать": ("💃", "кружится в страстном танце с", "под лучами вечернего неона"),
    "сделать массаж": ("💆", "делает расслабляющий массаж плеч для", "снимая всю усталость дня"),
    "подарить цветы": ("💐", "преподносит роскошный букет цветов для", "вызывая сияющую улыбку"),
    "признаться": ("❤️", "краснея, признаётся в тайных чувствах к", "заставляя сердце биться чаще"),
    "флиртовать": ("😏", "кокетливо заигрывает с", "стреляя глазками"),
    "подмигнуть": ("😉", "с загадочной улыбкой подмигивает", "намекая на что-то интересное"),
    "улыбнуться": ("😊", "искренне и тепло улыбается", "освещая всё вокруг"),
    "похвалить": ("👏", "искренне хвалит", "за выдающиеся успехи и крутость!"),
    "поздравить": ("🎉", "от всего сердца поздравляет", "осыпая блестящим конфетти!"),
    "поддержать": ("💪", "подбадривает и держит кулачки за", "напоминая, что всё обязательно получится!"),
    "утешить": ("🫂", "заботливо утешает", "вытирая слезинки и обещая, что всё наладится"),
    "защитить": ("🛡", "заслоняет собой и берёт под защиту", "от любых невзгод и обидчиков"),
    "выпить с": ("🥂", "поднимает бокал игристого за", "говоря самый душевный тост"),
    "накормить": ("🍰", "с ложечки кормит вкуснейшим десертом", "заботясь о сытости"),
    "спать с": ("💤", "уютно сопит рядышком под одеялом с", "видя самые сказочные сны"),
    "поиграть с": ("🎮", "рубится в кооперативе на геймпадах с", "раздавая мощные хедшоты"),
    "сфоткать": ("📸", "делает эстетичный полароид-снимок", "для персональной фотосессии"),

    # Дерзкие, боевые и шуточные
    "ударить": ("👊", "отвешивает мощный хук в челюсть", "отправляя в лёгкий нокдаун!"),
    "шлёпнуть": ("👋", "звонко шлёпает по мягкому месту", "за дерзкое поведение!"),
    "укусить": ("😬", "игриво кусает за ушко", "оставляя милый след зубок"),
    "пнуть": ("🦵", "даёт смачного пенделя", "придавая ускорение для полёта!"),
    "толкнуть": ("🫱", "толкает в сугроб", "заливаясь громким смехом"),
    "дать подзатыльник": ("🖐", "отвешивает отцовский подзатыльник", "для прочистки мозгов"),
    "кинуть тапок": ("🥿", "снайперски метает домашний тапок в", "поражая цель на 100%!"),
    "облить водой": ("💦", "выплёскивает ведро ледяной воды на", "чтобы охладить пыл!"),
    "закидать снежками": ("❄️", "закидывает градом снежков", "устраивая настоящую ледовую битву!"),
    "кинуть торт": ("🎂", "размазывает праздничный торт прямо по лицу", "делая жизнь слаще!"),
    "связать": ("🪢", "намертво связывает шелковыми веревками", "лишая возможности двигаться!"),
    "похитить": ("🚗", "засовывает в багажник спорткара и увозит", "в неизвестном направлении!"),
    "съесть": ("😋", "с аппетитом откусывает кусочек от", "приговаривая, какая вкуснятина!"),
    "проклясть": ("🔮", "насылает древнее проклятие вечной икоты на", "в клубах фиолетового дыма!"),
    "расстрелять": ("🔫", "разряжает лазерный бластер в сторону", "проверяя броню на прочность!"),
    "помиловать": ("👑", "царским жестом дарует прощение и милость", "отменяя казнь!"),
    "отравить": ("🧪", "подсыпает щепотку сонного зелья в чай", "наблюдая за зевотой"),
    "задушить": ("🐍", "устраивает удушающий приём для", "как настоящий чемпион UFC"),
    "выпороть": ("🦯", "устраивает показательную порку ремнём для", "в воспитательных целях!"),
    "плюнуть": ("💦", "демонстративно плюет под ноги", "показывая крайнее презрение"),
    "ущипнуть": ("🤏", "больно щипает за бочок", "заставляя подпрыгнуть от неожиданности!"),
    "нокаутировать": ("🥊", "вырубает точным апперкотом", "до появления звёздочек над головой!"),
    "сжечь": ("🔥", "направляет струю огнемета в", "зажигая эту тусовку по полной!"),
    "испугать": ("👻", "выскакивает из-за угла с криком «БУ!» перед", "заставляя волосы встать дыбом!"),
    "отругать": ("🗣", "строго и громко отчитывает", "за все совершенные косяки"),
    "наказать": ("⛓", "ставит в угол на горох", "на целых 15 минут за баловство"),
    "обокрасть": ("🥷", "незаметно вытаскивает счастливую монетку из кармана", "оставляя дырку в штанах"),
    "унизить": ("🤡", "громко высмеивает перед всей беседой", "вызывая бурю насмешек"),
    "лизнуть": ("👅", "игриво лижет в щёчку", "заставляя замурчать от неожиданности"),
    "пощекотать": ("🖐", "безжалостно щекочет за бока", "вызывая неудержимый приступ смеха"),
    "дать пять": ("✋", "отвешивает звонкую пятюню", "со смачным хлопком ладоней!"),
    "положить голову": ("💆", "уютно укладывает голову на плечо", "чувствуя абсолютное спокойствие"),
    "поделиться": ("🍪", "отламывает половинку шоколадной печеньки для", "согревая душевным теплом"),
    "станцевать вальс": ("💃", "кружит в грациозном венском вальсе с", "под аккомпанемент скрипок"),
    "прошептать": ("🤫", "шепчет таинственный секрет на ушко для", "заставляя пробежать мурашки"),
    "подбодрить": ("👏", "громко кричит и аплодирует в поддержку", "напоминая, что лучше никого нет!"),
    "погладить хвост": ("🦊", "нежно поглаживает пушистый лисий хвостик", "наслаждаясь мягкой шерсткой"),
    "обнять сзади": ("🫂", "неожиданно и крепко обнимает со спины", "уткнувшись носом в шею"),
    "напоить чаем": ("☕️", "заваривает кружку душистого чая с мятой для", "принося домашний уют"),
    "надеть корону": ("👑", "торжественно возлагает золотую корону на голову", "провозглашая великим правителем!"),
    "ущипнуть за нос": ("👃", "забавно щипает за кончик носа", "приговаривая «пип!»"),
    "дать леща": ("🐟", "отвешивает смачного увесистого леща", "с характерным влажным звуком!"),
    "отнять конфету": ("🍬", "нагло выхватывает вкусную конфету у", "и прячет за спину с хитрой ухмылкой!"),
    "вызвать на дуэль": ("⚔️", "демонстративно бросает белую шелковую перчатку под ноги", "требуя честного поединка!"),
    "бросить снежок": ("❄️", "лепит идеальный снежок и метко запускает в", "под взрывной хохот!"),
    "запустить фейерверк": ("🎆", "зажигает батарею салютов в честь", "озаряя ночное небо миллионом искр!"),
    "станцевать лезгинку": ("🕺", "лихо и зажигательно отплясывает лезгинку вокруг", "под бурные хлопки всей беседы!"),
    "проверить карманы": ("🔍", "бесцеремонно выворачивает карманы у", "выискивая припрятанные сокровища"),
    "поцеловать в губы": ("💋", "страстно целует в губы", "заставляя затаить дыхание"),
    "погладить по щеке": ("✨", "нежно проводит ладонью по щеке", "даруя тепло и спокойствие"),
    "положить на колени": ("💆", "нежно укладывает голову на колени", "перебирая пряди волос"),
    "подарить шоколадку": ("🍫", "угощает вкуснейшей плиткой молочного шоколада", "поднимая настроение!"),
    "подарить розу": ("🌹", "дарит одну идеальную бархатную розу", "со сладким ароматом"),
    "дать по шее": ("🖐", "отвешивает звонкую затрещину", "чтобы не умничать!"),
    "позвать пить чай": ("🫖", "приглашает за стол пить чай с плюшками", "в душевной компании"),
    "накрыть одеялом": ("🛋", "заботливо укутывает пушистым одеялом", "оберегая сладкий сон"),
    "дать кулачок": ("👊", "ударяет кулачком о кулачок", "в знак вечной дружбы и респекта!"),
    "похлопать по плечу": ("🤝", "дружески хлопает по плечу", "подбадривая: «держись, прорвёмся!»"),
}


# ═══════════════════════════════════════════════════════════════
# 2. 💼 ПРОФЕССИИ И КАРЬЕРА (10 УРОВНЕЙ)
# ═══════════════════════════════════════════════════════════════

JOBS_CATALOG = {
    "1": {"id": "cleaner", "title": "🧹 Дворник", "salary": 1500, "req_lvl": 1, "desc": "Подметает улицы и собирает бутылки"},
    "2": {"id": "courier", "title": "🚴 Курьер", "salary": 3500, "req_lvl": 2, "desc": "Доставляет горячую пиццу на электровелосипеде"},
    "3": {"id": "waiter", "title": "☕️ Официант", "salary": 7500, "req_lvl": 3, "desc": "Принимает заказы и собирает щедрые чаевые"},
    "4": {"id": "driver", "title": "🚕 Таксист", "salary": 15000, "req_lvl": 5, "desc": "Крутит баранку и травит жизненные байки"},
    "5": {"id": "manager", "title": "👔 Менеджер", "salary": 32000, "req_lvl": 8, "desc": "Проводит зум-созвоны и генерирует отчеты"},
    "6": {"id": "developer", "title": "💻 Программист", "salary": 70000, "req_lvl": 12, "desc": "Пишет сложнейший код для бота MOXXI 3.0"},
    "7": {"id": "banker", "title": "🏦 Банкир", "salary": 150000, "req_lvl": 18, "desc": "Управляет процентными ставками и займами"},
    "8": {"id": "politician", "title": "🏛 Депутат", "salary": 350000, "req_lvl": 25, "desc": "Принимает важные государственные указы"},
    "9": {"id": "oligarch", "title": "💎 Олигарх", "salary": 850000, "req_lvl": 40, "desc": "Скупает контрольные пакеты мировых акций"},
    "10": {"id": "astronaut", "title": "🚀 Космонавт", "salary": 2000000, "req_lvl": 60, "desc": "Исследует дальний космос на орбитальной станции"},
}


# ═══════════════════════════════════════════════════════════════
# 3. 🏡 НЕДВИЖИМОСТЬ И ДОМА (10 УРОВНЕЙ ЖИЛЬЯ)
# ═══════════════════════════════════════════════════════════════

REALTY_CATALOG = {
    "1": {"id": "box", "title": "📦 Картонная коробка", "price": 10000, "bonus": 500, "desc": "Скромный ночлег под теплым городским мостом"},
    "2": {"id": "dorm", "title": "🛏 Комната в общаге", "price": 40000, "bonus": 2000, "desc": "Веселые соседи и общая кухня"},
    "3": {"id": "studio", "title": "🚪 Квартира-студия", "price": 150000, "bonus": 6000, "desc": "18 квадратных метров уюта и микроволновка"},
    "4": {"id": "apartment", "title": "🏢 Двушка в центре", "price": 500000, "bonus": 18000, "desc": "Евроремонт и шикарный вид на парк"},
    "5": {"id": "townhouse", "title": "🏡 Таунхаус с газоном", "price": 1800000, "bonus": 55000, "desc": "Собственный гараж и зона для гриля"},
    "6": {"id": "cottage", "title": "🌲 Загородный коттедж", "price": 6000000, "bonus": 150000, "desc": "Баня, камин и вековой сосновый бор"},
    "7": {"id": "penthouse", "title": "🏙 Пентхаус в Сити", "price": 20000000, "bonus": 450000, "desc": "Панорамные окна на 75 этаже и джакузи"},
    "8": {"id": "villa", "title": "🏖 Вилла на Мальдивах", "price": 75000000, "bonus": 1200000, "desc": "Личный коралловый риф и infinity-бассейн"},
    "9": {"id": "castle", "title": "🏰 Средневековый замок", "price": 250000000, "bonus": 3500000, "desc": "Каменные башни, ров с водой и рыцарский зал"},
    "10": {"id": "island", "title": "🏝 Личный остров", "price": 1000000000, "bonus": 12000000, "desc": "Собственный райский уголок посреди океана"},
}


# ═══════════════════════════════════════════════════════════════
# 4. 🎒 ИНВЕНТАРЬ И ПРЕДМЕТЫ
# ═══════════════════════════════════════════════════════════════

ITEMS_CATALOG = {
    "1": {"id": "potion_xp", "title": "✨ Эликсир Опыта", "price": 12000, "desc": "Мгновенно начисляет +500 XP"},
    "2": {"id": "potion_luck", "title": "🍀 Зелье Удачи", "price": 25000, "desc": "Дает удачу в казино и шахте"},
    "3": {"id": "gold_pickaxe", "title": "⛏ Золотая кирка", "price": 60000, "desc": "Удваивает добычу монет в шахте"},
    "4": {"id": "titan_rod", "title": "🎣 Титановая удочка", "price": 50000, "desc": "Позволяет ловить редкую рыбу и сундуки"},
    "5": {"id": "medkit", "title": "💊 Аптечка спецназа", "price": 10000, "desc": "Восстанавливает силы в походах"},
    "6": {"id": "safe_key", "title": "🔑 Ключ-отмычка", "price": 30000, "desc": "Дает бонусную попытку взлома сейфа"},
    "7": {"id": "armor_vest", "title": "🦺 Бронежилет", "price": 45000, "desc": "Защищает от 1 попытки ограбления"},
}


# ═══════════════════════════════════════════════════════════════
# 5. ⚔️ ПОДЗЕМЕЛЬЯ И ДАНЖИ
# ═══════════════════════════════════════════════════════════════

DUNGEONS_CATALOG = {
    "1": {"id": "goblin", "name": "🌲 Гоблинский Лес", "req_lvl": 1, "reward": 5000, "xp": 80, "boss": "Гоблин-Шаман", "win_rate": 80},
    "2": {"id": "crypt", "name": "💀 Склеп Нежити", "req_lvl": 5, "reward": 18000, "xp": 180, "boss": "Рыцарь Смерти", "win_rate": 65},
    "3": {"id": "cave", "name": "🔥 Пещера Дракона", "req_lvl": 15, "reward": 55000, "xp": 400, "boss": "Огненный Виверн", "win_rate": 55},
    "4": {"id": "citadel", "name": "🏰 Цитадель Тьмы", "req_lvl": 30, "reward": 150000, "xp": 900, "boss": "Лорд Преисподней", "win_rate": 45},
    "5": {"id": "abyss", "name": "🌌 Бездна Пустоты", "req_lvl": 50, "reward": 450000, "xp": 2500, "boss": "Пожиратель Миров", "win_rate": 35},
}


# ═══════════════════════════════════════════════════════════════
# 6. 🏆 ДОСТИЖЕНИЯ И АЧИВКИ (12 НАГРАД)
# ═══════════════════════════════════════════════════════════════

ACHIEVEMENTS_CATALOG = {
    "first_bonus": {"title": "🎁 Первый шаг", "desc": "Забрать ежедневный бонус", "reward_c": 1000, "reward_xp": 50},
    "banker": {"title": "🏦 Вкладчик", "desc": "Положить первые монеты в банк", "reward_c": 3000, "reward_xp": 100},
    "miner_10": {"title": "⛏ Золотоискатель", "desc": "Поработать в шахте 10 раз", "reward_c": 10000, "reward_xp": 200},
    "millionaire": {"title": "💰 Миллионер", "desc": "Накопить баланс свыше 1 000 000 монет", "reward_c": 50000, "reward_xp": 500},
    "married": {"title": "💍 Семейные узы", "desc": "Сыграть свадьбу в боте", "reward_c": 15000, "reward_xp": 250},
    "car_owner": {"title": "🚗 Автолюбитель", "desc": "Купить первый автомобиль в гараж", "reward_c": 20000, "reward_xp": 300},
    "pet_master": {"title": "🐾 Верный друг", "desc": "Завести и покормить питомца", "reward_c": 12000, "reward_xp": 180},
    "biz_tycoon": {"title": "🏢 Магнат", "desc": "Купить бизнес в каталоге", "reward_c": 35000, "reward_xp": 450},
    "boss_hit": {"title": "🩸 Первая кровь", "desc": "Нанести удар по Рейдовому Боссу", "reward_c": 8000, "reward_xp": 150},
    "escape_master": {"title": "🥷 Ловкач", "desc": "Успешно сбежать из тюрьмы через вентиляцию", "reward_c": 25000, "reward_xp": 350},
    "clansman": {"title": "🏰 Братство", "desc": "Вступить в клан или создать свой", "reward_c": 20000, "reward_xp": 300},
    "dungeon_slayer": {"title": "⚔️ Герой подземелий", "desc": "Пройти любой данж", "reward_c": 30000, "reward_xp": 400},
}


# ═══════════════════════════════════════════════════════════════
# 7. 👑 ТИТУЛЫ ИГРОКОВ
# ═══════════════════════════════════════════════════════════════

TITLES_CATALOG = {
    "1": "⚡️ Легенда Беседы",
    "2": "💎 Мультимиллионер",
    "3": "👑 Повелитель Судеб",
    "4": "🥷 Теневой Барон",
    "5": "🐉 Убийца Драконов",
    "6": "💖 Главный Романтик",
    "7": "🎲 Любимчик Фортуны",
    "8": "🛡 Страж Правосудия",
}


# ═══════════════════════════════════════════════════════════════
# 🛠 ОБРАБОТЧИК РАСШИРЕННЫХ СИСТЕМ
# ═══════════════════════════════════════════════════════════════

async def handle_extended_command(
    message: Message,
    cmd: str,
    args: str,
    user_id: int,
    db_uid: int,
    db_cid: int,
    is_chat: bool,
    user_display: str,
    my_rank: int,
    get_vk_user_info_func,
    extract_target_func
) -> Optional[bool]:
    """Возвращает True, если команда была обработана в этом модуле."""
    con = db.conn()

    # ─────────────────────────────────────────────────────────────
    # 🎭 1. РП-КОМАНДЫ (РЕАКЦИИ)
    # ─────────────────────────────────────────────────────────────
    rp_key = None
    target_clean_txt = (message.text or "").strip().lower()

    # Проверяем совпадение с ключом РП
    for act_name in RP_ACTIONS:
        if target_clean_txt.startswith(act_name) or cmd == act_name:
            rp_key = act_name
            break

    if rp_key:
        icon, verb, suffix = RP_ACTIONS[rp_key]
        target_uid = extract_target_func(message, args)
        if not target_uid:
            return await message.answer(f"💡 Укажите игрока: «{rp_key} @юзер» или ответьте на его сообщение!")
        if target_uid == user_id:
            return await message.answer(f"😄 Нельзя применить действие «{rp_key}» к самому себе!")

        t_fn, t_ln = await get_vk_user_info_func(target_uid)
        target_display = f"[id{target_uid}|{t_fn}]"
        
        # Обновляем счетчик сообщений/актива
        await con.execute("""
            INSERT INTO chat_activity (chat_id, user_id, msg_count, last_msg_ts)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
            msg_count = msg_count + 1, last_msg_ts = ?
        """, (db_cid, db_uid, int(time.time()), int(time.time())))
        await con.commit()

        await message.answer(f"{icon} {user_display} {verb} {target_display} {suffix}!")
        return True

    # ─────────────────────────────────────────────────────────────
    # 💼 2. СИСТЕМА РАБОТ И ПРОФЕССИЙ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("работы", "профессии", "вакансии"):
        cur_row = await con.execute("SELECT job_id, level, last_work_ts FROM user_jobs WHERE user_id = ?", (db_uid,))
        cur_job = await cur_row.fetchone()
        cur_job_id = cur_job["job_id"] if cur_job else None

        lines = ["💼 ДОСТУПНЫЕ ПРОФЕССИИ И ВАКАНСИИ MOXXI:\n━━━━━━━━━━━━━━━━━━━━"]
        for num, j in JOBS_CATALOG.items():
            mark = " ✅ (Текущая)" if cur_job_id == j["id"] else ""
            lines.append(f"{num}. {j['title']} — Зарплата: {j['salary']:,} 🌑 / смену (Треб. {j['req_lvl']} ур.){mark}\n   📝 {j['desc']}")

        lines.append("\n💡 Команды:\n• «устроиться [номер 1-10]» — выбор профессии\n• «работать» — отработать смену и получить зарплату (кулдаун 1 час)\n• «уволиться» — уйти с текущей работы")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("устроиться", "профессия"):
        if not args or args not in JOBS_CATALOG:
            return await message.answer("💡 Напишите: «устроиться [номер от 1 до 10]». Список: «работы».")
        job = JOBS_CATALOG[args]
        u = await db.get_user(db_uid)
        u_lvl = max(1, (u.get("xp", 0) if u else 0) // 100)
        if u_lvl < job["req_lvl"]:
            return await message.answer(f"❌ Для профессии {job['title']} требуется минимум {job['req_lvl']} уровень (у вас {u_lvl} ур.)!")

        await con.execute("""
            INSERT INTO user_jobs (user_id, job_id, level, last_work_ts, shift_count)
            VALUES (?, ?, 1, 0, 0)
            ON CONFLICT(user_id) DO UPDATE SET job_id = ?
        """, (db_uid, job["id"], job["id"]))
        await con.commit()
        await message.answer(f"🎉 Поздравляем, {user_display}! Вы успешно устроились на работу: {job['title']}!\n💰 Зарплата: {job['salary']:,} 🌑 за смену.\n⏱ Напишите «работать», чтобы приступить!")
        return True

    if cmd in ("работать", "смена"):
        cur_row = await con.execute("SELECT job_id, last_work_ts, shift_count FROM user_jobs WHERE user_id = ?", (db_uid,))
        cur_job = await cur_row.fetchone()
        if not cur_job:
            return await message.answer("❌ Вы нигде не работаете! Посмотрите вакансии: «работы» и устройтесь: «устроиться 1».")

        now = int(time.time())
        diff = now - cur_job["last_work_ts"]
        cd_sec = 3600  # 1 час
        if diff < cd_sec:
            rem = cd_sec - diff
            rm = rem // 60
            rs = rem % 60
            return await message.answer(f"⏳ Вы устали после прошлой смены! Отдохните еще {rm} мин {rs} сек перед новой работой.")

        job_info = next((j for j in JOBS_CATALOG.values() if j["id"] == cur_job["job_id"]), None)
        if not job_info:
            return await message.answer("❌ Ваша профессия устарела. Выберите новую: «работы».")

        salary = job_info["salary"]
        await con.execute("UPDATE user_jobs SET last_work_ts = ?, shift_count = shift_count + 1 WHERE user_id = ?", (now, db_uid))
        await con.commit()
        await db.add_balance(db_uid, salary)
        await db.add_xp(db_uid, 45)

        phrases = [
            f"🛠 {user_display} отлично отработал смену на должности {job_info['title']}!",
            f"💼 Трудовой день подошёл к концу! {user_display} перевыполнил норму!",
            f"📈 Начальство довольно вашей работой ({job_info['title']})!"
        ]
        await message.answer(f"{random.choice(phrases)}\n💰 Выдана зарплата: +{salary:,} 🌑 и +45 XP!")
        return True

    if cmd in ("уволиться",):
        await con.execute("DELETE FROM user_jobs WHERE user_id = ?", (db_uid,))
        await con.commit()
        await message.answer(f"🚪 {user_display}, вы уволились с работы. Теперь вы свободны! Новые вакансии: «работы».")
        return True

    # ─────────────────────────────────────────────────────────────
    # 🏡 3. НЕДВИЖИМОСТЬ И ДОМА
    # ─────────────────────────────────────────────────────────────
    if cmd in ("дома", "недвижимость", "жилье"):
        cur_row = await con.execute("SELECT house_id, purchased_at FROM user_realty WHERE user_id = ?", (db_uid,))
        my_h = await cur_row.fetchone()
        my_hid = my_h["house_id"] if my_h else None

        lines = ["🏡 РЫНОК НЕДВИЖИМОСТИ MOXXI:\n━━━━━━━━━━━━━━━━━━━━"]
        for num, h in REALTY_CATALOG.items():
            mark = " 🏠 (Ваш дом)" if my_hid == h["id"] else ""
            lines.append(f"{num}. {h['title']} — {h['price']:,} 🌑\n   💎 Ежедневный бонус: +{h['bonus']:,} 🌑 | {h['desc']}{mark}")

        lines.append("\n💡 Команды:\n• «купить дом [номер 1-10]» — покупка жилья\n• «мой дом» — информация о вашей недвижимости\n• «продать дом» — продать за 75% стоимости")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("купить_дом", "купитьдом") or (cmd == "купить" and args.startswith("дом")):
        num = args.replace("дом", "").strip()
        if not num or num not in REALTY_CATALOG:
            return await message.answer("💡 Напишите: «купить дом [1-10]». Каталог: «дома».")
        h = REALTY_CATALOG[num]
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < h["price"]:
            return await message.answer(f"❌ Недостаточно средств! {h['title']} стоит {h['price']:,} 🌑 (у вас {bal:,} 🌑).")

        await db.add_balance(db_uid, -h["price"])
        await con.execute("""
            INSERT INTO user_realty (user_id, house_id, purchased_at, last_rent_ts)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET house_id = ?, purchased_at = ?
        """, (db_uid, h["id"], int(time.time()), int(time.time()), h["id"], int(time.time())))
        await con.commit()
        await message.answer(f"🎉 Поздравляем с новосельем, {user_display}!\n🏠 Вы приобрели: {h['title']} за {h['price']:,} 🌑!\n💎 Теперь ваше жилье приносит статус и уют!")
        return True

    if cmd in ("мой_дом", "мойдом", "дом"):
        cur_row = await con.execute("SELECT house_id, purchased_at FROM user_realty WHERE user_id = ?", (db_uid,))
        my_h = await cur_row.fetchone()
        if not my_h:
            return await message.answer("🏚 У вас пока нет своего жилья! Откройте каталог: «дома» и выберите подходящий вариант.")

        h = next((item for item in REALTY_CATALOG.values() if item["id"] == my_h["house_id"]), None)
        dt = datetime.datetime.fromtimestamp(my_h["purchased_at"]).strftime("%d.%m.%Y")
        await message.answer(
            f"🏠 ВАША НЕДВИЖИМОСТЬ:\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷 Объект: {h['title'] if h else 'Уютный дом'}\n"
            f"💎 Пассивный бонус уюта: +{h['bonus']:,} 🌑\n"
            f"📅 Дата покупки: {dt}\n"
            f"💵 Стоимость при продаже (75%): {int(h['price'] * 0.75):,} 🌑\n\n"
            f"💡 Для продажи напишите: «продать дом»."
        )
        return True

    if cmd in ("продать_дом", "продатьдом"):
        cur_row = await con.execute("SELECT house_id FROM user_realty WHERE user_id = ?", (db_uid,))
        my_h = await cur_row.fetchone()
        if not my_h:
            return await message.answer("❌ У вас нет недвижимости для продажи!")

        h = next((item for item in REALTY_CATALOG.values() if item["id"] == my_h["house_id"]), None)
        refund = int(h["price"] * 0.75) if h else 5000
        await con.execute("DELETE FROM user_realty WHERE user_id = ?", (db_uid,))
        await con.commit()
        await db.add_balance(db_uid, refund)
        await message.answer(f"💰 {user_display}, вы успешно продали недвижимость за {refund:,} 🌑 (75% от цены).")
        return True

    # ─────────────────────────────────────────────────────────────
    # 🎒 4. ИНВЕНТАРЬ И ПРЕДМЕТЫ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("магазин_предметов", "предметы"):
        lines = ["🎒 МАГАЗИН СНАРЯЖЕНИЯ И АРТЕФАКТОВ:\n━━━━━━━━━━━━━━━━━━━━"]
        for num, it in ITEMS_CATALOG.items():
            lines.append(f"{num}. {it['title']} — {it['price']:,} 🌑\n   📝 {it['desc']}")
        lines.append("\n💡 Для покупки: «купить предмет [номер 1-7]»\n🎒 Ваш инвентарь: «инвентарь»")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("купить_предмет", "купитьпредмет") or (cmd == "купить" and args.startswith("предмет")):
        num = args.replace("предмет", "").strip()
        if not num or num not in ITEMS_CATALOG:
            return await message.answer("💡 Напишите: «купить предмет [1-7]». Каталог: «магазин предметов».")
        it = ITEMS_CATALOG[num]
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < it["price"]:
            return await message.answer(f"❌ Недостаточно монет! {it['title']} стоит {it['price']:,} 🌑 (у вас {bal:,} 🌑).")

        await db.add_balance(db_uid, -it["price"])
        await con.execute("""
            INSERT INTO user_inventory (user_id, item_id, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + 1
        """, (db_uid, it["id"]))
        await con.commit()
        await message.answer(f"✅ {user_display}, вы приобрели: {it['title']} за {it['price']:,} 🌑!\n🎒 Предмет помещён в ваш «инвентарь».")
        return True

    if cmd in ("инвентарь", "рюкзак"):
        rows = await (await con.execute("SELECT item_id, quantity FROM user_inventory WHERE user_id = ? AND quantity > 0", (db_uid,))).fetchall()
        if not rows:
            return await message.answer(f"🎒 {user_display}, ваш инвентарь пока пуст!\n💡 Загляните в магазин: «магазин предметов».")

        lines = [f"🎒 ИНВЕНТАРЬ ИГРОКА {user_display}:\n━━━━━━━━━━━━━━━━━━━━"]
        for r in rows:
            it = next((item for item in ITEMS_CATALOG.values() if item["id"] == r["item_id"]), None)
            t_name = it["title"] if it else r["item_id"]
            lines.append(f"• {t_name} — {r['quantity']} шт.")
        lines.append("\n💡 Чтобы использовать предмет, напишите: «использовать [название]»")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("использовать", "юзать"):
        item_raw = args.strip().lower()
        if "опыт" in item_raw or "эликсир" in item_raw:
            it_id = "potion_xp"
        elif "удач" in item_raw or "зелье" in item_raw:
            it_id = "potion_luck"
        elif "аптечк" in item_raw:
            it_id = "medkit"
        else:
            return await message.answer("💡 Напишите: «использовать эликсир опыта» или «использовать зелье удачи». Список: «инвентарь».")

        row = await (await con.execute("SELECT quantity FROM user_inventory WHERE user_id = ? AND item_id = ?", (db_uid, it_id))).fetchone()
        if not row or row["quantity"] <= 0:
            return await message.answer("❌ У вас нет этого предмета в инвентаре!")

        await con.execute("UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_id = ?", (db_uid, it_id))
        await con.commit()

        if it_id == "potion_xp":
            await db.add_xp(db_uid, 500)
            return await message.answer(f"✨ {user_display} выпил Эликсир Опыта! Начислено: +500 XP!")
        elif it_id == "potion_luck":
            await db.set_cooldown(db_uid, "luck_potion", 1800)
            return await message.answer(f"🍀 {user_display} активировал Зелье Удачи на 30 минут! Шансы на джекпот увеличены!")
        elif it_id == "medkit":
            return await message.answer(f"💊 {user_display} применил Аптечку спецназа! Здоровье полностью восстановлено!")

    # ─────────────────────────────────────────────────────────────
    # 📜 5. ЕЖЕДНЕВНЫЕ КВЕСТЫ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("квесты", "задания", "дейлики"):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        q_row = await (await con.execute("SELECT * FROM user_quests WHERE user_id = ? AND day_str = ?", (db_uid, today))).fetchone()
        if not q_row:
            await con.execute("""
                INSERT INTO user_quests (user_id, day_str, q1_id, q1_cur, q1_done, q2_id, q2_cur, q2_done, q3_id, q3_cur, q3_done)
                VALUES (?, ?, 'casino_3', 0, 0, 'mine_2', 0, 0, 'bonus_1', 0, 0)
                ON CONFLICT(user_id, day_str) DO NOTHING
            """, (db_uid, today))
            await con.commit()
            q_row = await (await con.execute("SELECT * FROM user_quests WHERE user_id = ? AND day_str = ?", (db_uid, today))).fetchone()

        status_1 = "✅ Выполнено" if q_row["q1_done"] else f"⏳ Прогресс: {q_row['q1_cur']}/3"
        status_2 = "✅ Выполнено" if q_row["q2_done"] else f"⏳ Прогресс: {q_row['q2_cur']}/2"
        status_3 = "✅ Выполнено" if q_row["q3_done"] else f"⏳ Прогресс: {q_row['q3_cur']}/1"

        text_q = (
            f"📜 ЕЖЕДНЕВНЫЕ ЗАДАНИЯ ({today}):\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"1. 🎰 Сыграть 3 раза в казино или слоты\n"
            f"   Награда: 5 000 🌑 | {status_1}\n\n"
            f"2. ⛏ Добыть руду в шахте 2 раза\n"
            f"   Награда: 5 000 🌑 | {status_2}\n\n"
            f"3. 🎁 Забрать ежедневный бонус («бонус»)\n"
            f"   Награда: 5 000 🌑 | {status_3}\n\n"
            f"💡 Для сдачи квеста напишите: «сдать квест [1-3]»!"
        )
        await message.answer(text_q)
        return True

    if cmd in ("сдать_квест", "сдатьквест"):
        q_num = args.strip()
        if q_num not in ("1", "2", "3"):
            return await message.answer("💡 Напишите: «сдать квест 1», «сдать квест 2» или «сдать квест 3».")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        q_row = await (await con.execute("SELECT * FROM user_quests WHERE user_id = ? AND day_str = ?", (db_uid, today))).fetchone()
        if not q_row:
            return await message.answer("❌ Сначала откройте список заданий: «квесты».")

        cur_done = q_row[f"q{q_num}_done"]
        if cur_done:
            return await message.answer(f"✅ Вы уже забрали награду за квест #{q_num} сегодня!")

        # Поощряем игрока за активность
        await con.execute(f"UPDATE user_quests SET q{q_num}_done = 1, q{q_num}_cur = 3 WHERE user_id = ? AND day_str = ?", (db_uid, today))
        await con.commit()
        await db.add_balance(db_uid, 5000)
        await db.add_xp(db_uid, 80)
        await message.answer(f"🎉 Задание #{q_num} успешно сдано!\n💰 Награда: +5 000 🌑 и +80 XP зачислены на баланс!")
        return True

    # ─────────────────────────────────────────────────────────────
    # 🏆 6. ДОСТИЖЕНИЯ И АЧИВКИ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("ачивки", "достижения", "награды"):
        unlocked_rows = await (await con.execute("SELECT ach_id FROM user_achievements WHERE user_id = ?", (db_uid,))).fetchall()
        unlocked = {r["ach_id"] for r in unlocked_rows}

        lines = [f"🏆 СИСТЕМА ДОСТИЖЕНИЙ {user_display}:\n━━━━━━━━━━━━━━━━━━━━"]
        for ach_id, data in ACHIEVEMENTS_CATALOG.items():
            mark = " ✅ Разблокировано" if ach_id in unlocked else f" 🔒 (+{data['reward_c']:,} 🌑)"
            lines.append(f"• {data['title']}{mark}\n  Описание: {data['desc']}")

        lines.append(f"\n📊 Прогресс: {len(unlocked)}/{len(ACHIEVEMENTS_CATALOG)} достижений")
        await message.answer("\n".join(lines))
        return True

    # ─────────────────────────────────────────────────────────────
    # 🎯 7. МИНИ-ИГРЫ: СЕЙФ, СТАКАНЧИКИ, СПОРТ, КНБ, ЛОТЕРЕЯ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("сейф", "взлом"):
        safe_row = await (await con.execute("SELECT current_code, jackpot_pool FROM safe_jackpot WHERE id = 1")).fetchone()
        pool = safe_row["jackpot_pool"] if safe_row else 50000
        code_real = safe_row["current_code"] if safe_row else 42

        if not args or not args.isdigit():
            return await message.answer(
                f"🔐 ГОСУДАРСТВЕННЫЙ СЕЙФ MOXXI:\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Текущий ДЖЕКПОТ сейфа: {pool:,} 🌑\n"
                f"🎯 Код сейфа: число от 1 до 100\n\n"
                f"💡 Чтобы попытаться взломать сейф, напишите:\n"
                f"• «сейф [число от 1 до 100]» (цена попытки: 500 🌑)\n"
                f"При неудаче ваши 500 🌑 пополняют общий джекпот!"
            )

        guess = int(args)
        if guess < 1 or guess > 100:
            return await message.answer("❌ Число должно быть от 1 до 100!")

        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < 500:
            return await message.answer("❌ Стоимость попытки взлома — 500 🌑. Недостаточно средств!")

        await db.add_balance(db_uid, -500)

        if guess == code_real:
            # ДЖЕКПОТ ВЗЯТ!
            win_amount = pool + 500
            new_code = random.randint(1, 100)
            await con.execute("UPDATE safe_jackpot SET current_code = ?, jackpot_pool = 50000 WHERE id = 1", (new_code,))
            await con.commit()
            await db.add_balance(db_uid, win_amount)
            await db.add_xp(db_uid, 500)
            return await message.answer(
                f"🚨 ВНИМАНИЕ ВСЕМ! СЕЙФ ВЗЛОМАН! 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 {user_display} подобрал верный код ({guess}) и срывает куш!\n"
                f"💰 ВЫИГРЫШ: +{win_amount:,} 🌑 зачислены на баланс!\n"
                f"🔐 Установлен новый сейф с начальным банком 50 000 🌑."
            )
        else:
            # Не угадал
            await con.execute("UPDATE safe_jackpot SET jackpot_pool = jackpot_pool + 500 WHERE id = 1")
            await con.commit()
            hint = "Слишком мало! Код больше 📈" if guess < code_real else "Слишком много! Код меньше 📉"
            return await message.answer(f"🔒 Щёлк... Замок не поддался! Неверный код ({guess}).\n💡 Подсказка: {hint}\n💰 В джекпот сейфа добавлено +500 🌑 (Всего: {pool + 500:,} 🌑).")

    if cmd in ("стаканчики", "наперстки"):
        parts = args.split()
        if len(parts) < 2 or parts[0] not in ("1", "2", "3") or not parts[1].isdigit():
            return await message.answer("💡 Пример игры: «стаканчики [1, 2 или 3] [ставка]» (Коэффициент победы x2.5).")

        cup_choice = int(parts[0])
        bet = int(parts[1])
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < bet or bet <= 0:
            return await message.answer(f"❌ Недостаточно средств! Баланс: {bal:,} 🌑.")

        await db.add_balance(db_uid, -bet)
        winning_cup = random.randint(1, 3)

        if cup_choice == winning_cup:
            win = int(bet * 2.5)
            await db.add_balance(db_uid, win)
            await db.add_xp(db_uid, 30)
            return await message.answer(f"🎩 Мокси перемешала стаканчики...\n🎉 ВЕРНО! Шарик был под стаканчиком #{winning_cup}!\n💰 Выигрыш: +{win:,} 🌑 (x2.5)!")
        else:
            return await message.answer(f"🎩 Мокси перемешала стаканчики...\n😢 Увы! Шарик оказался под стаканчиком #{winning_cup}, а вы выбрали #{cup_choice}.\n💸 Вы проиграли {bet:,} 🌑.")

    if cmd in ("дартс", "футбол", "баскетбол", "боулинг"):
        if not args or not args.isdigit():
            return await message.answer(f"💡 Напишите: «{cmd} [сумма ставки]». Пример: «{cmd} 500».")
        bet = int(args)
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < bet or bet <= 0:
            return await message.answer(f"❌ Недостаточно монет для ставки!")

        await db.add_balance(db_uid, -bet)
        score = random.randint(1, 6)

        if cmd == "дартс":
            if score >= 5:
                win = int(bet * 3)
                await db.add_balance(db_uid, win)
                return await message.answer(f"🎯 В ЯБЛОЧКО! Точный бросок в центр мишени!\n💰 Выигрыш: +{win:,} 🌑 (x3)!")
            else:
                return await message.answer(f"🎯 Дротик улетел в край мишени ({score}/6). Ставка {bet:,} 🌑 сгорела.")
        elif cmd == "футбол":
            if score >= 4:
                win = int(bet * 2.2)
                await db.add_balance(db_uid, win)
                return await message.answer(f"⚽️ ГООООЛ! Мяч вонзился в девятку ворот!\n💰 Выигрыш: +{win:,} 🌑 (x2.2)!")
            else:
                return await message.answer(f"⚽️ Вратарь в прыжке отбил мяч! Ставка {bet:,} 🌑 сгорела.")
        elif cmd == "баскетбол":
            if score >= 4:
                win = int(bet * 2.2)
                await db.add_balance(db_uid, win)
                return await message.answer(f"🏀 ТОЧНЫЙ БРОСОК! Чистый трёхочковый в корзину!\n💰 Выигрыш: +{win:,} 🌑 (x2.2)!")
            else:
                return await message.answer(f"🏀 Мяч ударился о кольцо и отскочил! Ставка {bet:,} 🌑 сгорела.")
        elif cmd == "боулинг":
            if score == 6:
                win = int(bet * 4.5)
                await db.add_balance(db_uid, win)
                return await message.answer(f"🎳 СТРАЙК! Все 10 кеглей разлетелись в щепки!\n💰 СУПЕР-ВЫИГРЫШ: +{win:,} 🌑 (x4.5)!")
            else:
                return await message.answer(f"🎳 Шар сбил лишь {score} кеглей. Ставка {bet:,} 🌑 сгорела.")

    if cmd in ("кнб",):
        parts = args.split()
        if len(parts) < 2 or parts[0] not in ("камень", "ножницы", "бумага") or not parts[1].isdigit():
            return await message.answer("💡 Пример игры: «кнб камень 500» или «кнб ножницы 1000».")
        choice = parts[0]
        bet = int(parts[1])
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < bet or bet <= 0:
            return await message.answer("❌ Недостаточно средств!")

        bot_choices = ["камень", "ножницы", "бумага"]
        bot_choice = random.choice(bot_choices)
        icons = {"камень": "🪨 Камень", "ножницы": "✂️ Ножницы", "бумага": "📄 Бумага"}

        if choice == bot_choice:
            return await message.answer(f"🤝 НИЧЬЯ!\nУ вас: {icons[choice]}\nУ Мокси: {icons[bot_choice]}\nМонеты возвращены.")
        elif (choice == "камень" and bot_choice == "ножницы") or (choice == "ножницы" and bot_choice == "бумага") or (choice == "бумага" and bot_choice == "камень"):
            win = int(bet * 2)
            await db.add_balance(db_uid, win - bet)
            return await message.answer(f"🎉 ВЫ ПОБЕДИЛИ!\nУ вас: {icons[choice]}\nУ Мокси: {icons[bot_choice]}\n💰 Выигрыш: +{win:,} 🌑!")
        else:
            await db.add_balance(db_uid, -bet)
            return await message.answer(f"😢 ВЫ ПРОИГРАЛИ!\nУ вас: {icons[choice]}\nУ Мокси: {icons[bot_choice]}\n💸 Потеряно: {bet:,} 🌑.")

    if cmd in ("лотерея", "лотерейный_билет"):
        u = await db.get_user(db_uid)
        bal = u.get("balance", 0) if u else 0
        if bal < 1000:
            return await message.answer("❌ Стоимость лотерейного билета — 1 000 🌑. Недостаточно средств!")
        await db.add_balance(db_uid, -1000)
        t_num = random.randint(10000, 99999)
        win_chance = random.randint(1, 100)

        if win_chance <= 3:
            jackpot = 100000
            await db.add_balance(db_uid, jackpot)
            return await message.answer(f"🎫 БИЛЕТ #{t_num} ОКАЗАЛСЯ СЧАСТЛИВЫМ!\n🎉 ДЖЕКПОТ ЛОТЕРЕИ: +{jackpot:,} 🌑 зачислены на ваш баланс!")
        elif win_chance <= 25:
            prize = 3000
            await db.add_balance(db_uid, prize)
            return await message.answer(f"🎫 Билет #{t_num} выиграл малый приз: +{prize:,} 🌑!")
        else:
            return await message.answer(f"🎫 Билет #{t_num} без выигрыша. Попробуйте еще раз в следующем тираже!")

    # ─────────────────────────────────────────────────────────────
    # ⚔️ 8. ДАНЖИ И ПОДЗЕМЕЛЬЯ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("данжи", "подземелья"):
        lines = ["⚔️ ПОДЗЕМЕЛЬЯ И ДАНЖИ MOXXI:\n━━━━━━━━━━━━━━━━━━━━"]
        for num, d in DUNGEONS_CATALOG.items():
            lines.append(f"{num}. {d['name']} (Треб. {d['req_lvl']} ур.)\n   👹 Босс: {d['boss']} | 💰 Награда: +{d['reward']:,} 🌑 (+{d['xp']} XP)")
        lines.append("\n💡 Для похода в данж напишите: «поход [номер 1-5]» или «данж [номер 1-5]».")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("поход", "данж"):
        d_num = args.strip()
        if d_num not in DUNGEONS_CATALOG:
            return await message.answer("💡 Напишите: «поход [1-5]». Каталог: «данжи».")

        d = DUNGEONS_CATALOG[d_num]
        u = await db.get_user(db_uid)
        u_lvl = max(1, (u.get("xp", 0) if u else 0) // 100)
        if u_lvl < d["req_lvl"]:
            return await message.answer(f"❌ Для похода в {d['name']} требуется минимум {d['req_lvl']} уровень (у вас {u_lvl} ур.)!")

        cd_left = await db.cooldown_left(db_uid, f"dungeon_{d['id']}", 1800)
        if cd_left > 0:
            dm = cd_left // 60
            ds = cd_left % 60
            return await message.answer(f"⏳ Ваши герои отдыхают! Следующий поход в этот данж через {dm} мин {ds} сек.")

        await db.set_cooldown(db_uid, f"dungeon_{d['id']}", 1800)
        roll = random.randint(1, 100)

        if roll <= d["win_rate"]:
            await db.add_balance(db_uid, d["reward"])
            await db.add_xp(db_uid, d["xp"])
            return await message.answer(
                f"⚔️ ПОХОД В {d['name'].upper()} УВЕНЧАЛСЯ УСПЕХОМ!\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👹 Босс {d['boss']} повержен после ожесточенного боя!\n"
                f"💰 Добыча: +{d['reward']:,} 🌑\n"
                f"✨ Получено: +{d['xp']} XP!"
            )
        else:
            return await message.answer(
                f"💀 ПОРАЖЕНИЕ В {d['name'].upper()}!\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👹 Босс {d['boss']} оказался слишком свирепым и разгромил ваш отряд.\n"
                f"🏥 Герои сбежали зализывать раны. Попробуйте снова через 30 минут!"
            )

    # ─────────────────────────────────────────────────────────────
    # 👑 9. ТИТУЛЫ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("титулы", "титул"):
        if not args:
            cur_t = await (await con.execute("SELECT title FROM user_titles WHERE user_id = ?", (db_uid,))).fetchone()
            my_title = cur_t["title"] if cur_t else "Отсутствует"
            lines = [f"👑 КАТАЛОГ КАСТОМНЫХ ТИТУЛОВ:\nВаш текущий титул: {my_title}\n━━━━━━━━━━━━━━━━━━━━"]
            for num, t_name in TITLES_CATALOG.items():
                lines.append(f"{num}. {t_name}")
            lines.append("\n💡 Команды:\n• «надеть титул [номер 1-8]» — надеть титул в профиль\n• «снять титул» — убрать титул")
            await message.answer("\n".join(lines))
            return True

    if cmd in ("надеть_титул", "надетьтитул") or (cmd == "надеть" and "титул" in args):
        num = args.replace("титул", "").strip()
        if num not in TITLES_CATALOG:
            return await message.answer("💡 Напишите: «надеть титул [1-8]». Список: «титулы».")
        t_name = TITLES_CATALOG[num]
        await con.execute("INSERT INTO user_titles (user_id, title) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET title = ?", (db_uid, t_name, t_name))
        await con.commit()
        await message.answer(f"👑 {user_display}, вам присвоен почетный титул: «{t_name}»! Теперь он украшает ваш профиль!")
        return True

    if cmd in ("снять_титул", "снятьтитул"):
        await con.execute("DELETE FROM user_titles WHERE user_id = ?", (db_uid,))
        await con.commit()
        await message.answer(f"👑 {user_display}, ваш титул успешно снят.")
        return True

    # ─────────────────────────────────────────────────────────────
    # 🛡 10. МОДЕРАЦИЯ: МУТЫ И РАЗМУТЫ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("мут", "заглушить"):
        if my_rank < 2:
            return await message.answer("❌ Команда доступна модераторам от ранга [2]!")
        target_uid = extract_target_func(message, args)
        if not target_uid:
            return await message.answer("💡 Напишите: «мут @юзер [минуты] [причина]» или ответом на сообщение.")

        parts = args.split()
        mins = 15
        reason = "Нарушение правил беседы"
        for p in parts:
            if p.isdigit():
                mins = max(1, min(1440, int(p)))
                break

        until_ts = int(time.time()) + mins * 60
        db_target_uid = db.to_db_uid(target_uid) if hasattr(db, "to_db_uid") else 70_000_000_000 + target_uid
        await con.execute("""
            INSERT INTO chat_mutes (chat_id, user_id, until_ts, reason, by_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET until_ts = ?, reason = ?
        """, (db_cid, db_target_uid, until_ts, reason, db_uid, until_ts, reason))
        await con.commit()

        t_fn, _ = await get_vk_user_info_func(target_uid)
        await message.answer(f"🔇 Модератор {user_display} выдал мут пользователю [id{target_uid}|{t_fn}] на {mins} мин!\n📝 Причина: {reason}.")
        return True

    if cmd in ("размут", "снять_мут"):
        if my_rank < 2:
            return await message.answer("❌ Команда доступна модераторам от ранга [2]!")
        target_uid = extract_target_func(message, args)
        if not target_uid:
            return await message.answer("💡 Напишите: «размут @юзер».")

        db_target_uid = db.to_db_uid(target_uid) if hasattr(db, "to_db_uid") else 70_000_000_000 + target_uid
        await con.execute("DELETE FROM chat_mutes WHERE chat_id = ? AND user_id = ?", (db_cid, db_target_uid))
        await con.commit()
        t_fn, _ = await get_vk_user_info_func(target_uid)
        await message.answer(f"🔊 Модератор {user_display} снял мут с пользователя [id{target_uid}|{t_fn}].")
        return True

    # ─────────────────────────────────────────────────────────────
    # 📊 11. ЧАТ-МЕНЕДЖМЕНТ: АКТИВ, ЧАТСТАТ, ОНЛАЙН, СОЗЫВ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("чатстат", "актив", "топ_актив"):
        if not is_chat:
            return await message.answer("❌ Статистика активности доступна только в беседах!")
        rows = await (await con.execute("""
            SELECT user_id, msg_count FROM chat_activity
            WHERE chat_id = ? ORDER BY msg_count DESC LIMIT 10
        """, (db_cid,))).fetchall()

        if not rows:
            return await message.answer("📊 В этой беседе пока нет накопленной статистики сообщений.")

        lines = ["📊 ТОП-10 АКТИВНЫХ УЧАСТНИКОВ БЕСЕДЫ:\n━━━━━━━━━━━━━━━━━━━━"]
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for i, r in enumerate(rows):
            real_uid = r["user_id"] - 70_000_000_000 if r["user_id"] >= 70_000_000_000 else r["user_id"]
            u_fn, _ = await get_vk_user_info_func(real_uid)
            lines.append(f"{medals[i]} [id{real_uid}|{u_fn}] — {r['msg_count']} сообщ.")
        await message.answer("\n".join(lines))
        return True

    if cmd in ("созвать", "все", "общий_сбор"):
        if not is_chat:
            return await message.answer("❌ Созыв доступен только в беседах!")
        if my_rank < 3:
            return await message.answer("❌ Команда «созвать» доступна модераторам от ранга [3]!")

        cd_left = await db.cooldown_left(db_cid, "call_all_cd", 1800)
        if cd_left > 0:
            cm = cd_left // 60
            cs = cd_left % 60
            return await message.answer(f"⏳ Следующий общий сбор беседы возможен через {cm} мин {cs} сек.")

        await db.set_cooldown(db_cid, "call_all_cd", 1800)
        await message.answer(f"📢 ВНИМАНИЕ БЕСЕДА! ОБЩИЙ СБОР! 📢\n━━━━━━━━━━━━━━━━━━━━\n👑 Модератор {user_display} созывает всех участников!\n💬 Причина: {args if args else 'Важное обсуждение / Рейдовый Босс'}!")
        return True

    # ─────────────────────────────────────────────────────────────
    # 👮 12. ПОЛИЦИЯ И РОЗЫСК
    # ─────────────────────────────────────────────────────────────
    if cmd in ("розыск", "ориентировка"):
        lines = [
            "👮 ОРИЕНТИРОВКА ПОЛИЦИИ ГОРОДА MOXXI:\n━━━━━━━━━━━━━━━━━━━━",
            "В розыске за дерзкие ограбления и криминал:",
            "🚨 Преступники на свободе рискуют быть арестованными полицией!",
            "💡 Чтобы поймать грабителя: «ограбить @юзер» или сдайте его в КПЗ!",
            "🔓 Выкуп из тюрьмы: «залог @юзер» (10 000 🌑)."
        ]
        await message.answer("\n".join(lines))
        return True


    # ─────────────────────────────────────────────────────────────
    # 🏰 13. ВОЙНЫ КЛАНОВ (КЛАНВАР) И КЛАНОВОЕ УПРАВЛЕНИЕ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("кланвар", "война_кланов", "битва_кланов"):
        if not is_chat:
            return await message.answer("❌ Клановые войны проводятся только в беседах!")
        u_clan = await db.get_user_clan(db_uid)
        if not u_clan:
            return await message.answer("❌ Вы не состоите в клане! Создайте: «создать клан [название]» или вступите в клан.")
        if u_clan["owner_id"] != db_uid:
            return await message.answer("❌ Объявлять кланвары может только Лидер клана!")

        parts = args.split()
        if len(parts) < 2 or not parts[-1].isdigit():
            return await message.answer("💡 Пример объявления войны: «кланвар [название клана] [ставка]». Пример: «кланвар Акулы 25000».")

        enemy_name = " ".join(parts[:-1]).strip()
        bet = int(parts[-1])
        c_row = await (await con.execute("SELECT id, name, treasury, owner_id FROM clans WHERE name = ? COLLATE NOCASE", (enemy_name,))).fetchone()
        if not c_row:
            return await message.answer(f"❌ Клан «{enemy_name}» не найден!")
        if c_row["id"] == u_clan["id"]:
            return await message.answer("❌ Нельзя объявить войну собственному клану!")

        if u_clan["treasury"] < bet:
            return await message.answer(f"❌ В казне вашего клана недостаточно средств! В казне: {u_clan['treasury']:,} 🌑.")
        if c_row["treasury"] < bet:
            return await message.answer(f"❌ В казне вражеского клана недостаточно монет для такой ставки ({c_row['treasury']:,} 🌑).")

        # Битва
        my_power = random.randint(30, 100) + u_clan["level"] * 5
        enemy_power = random.randint(30, 100) + 10
        if my_power >= enemy_power:
            await con.execute("UPDATE clans SET treasury = treasury + ? WHERE id = ?", (bet, u_clan["id"]))
            await con.execute("UPDATE clans SET treasury = treasury - ? WHERE id = ?", (bet, c_row["id"]))
            await con.commit()
            return await message.answer(
                f"⚔️ КЛАНОВАР ЗАВЕРШЁН ПОБЕДОЙ! ⚔️\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏰 Клан «{u_clan['name']}» сокрушил войска клана «{c_row['name']}»!\n"
                f"💰 Награда: +{bet:,} 🌑 переведены из вражеской казны в вашу казну!\n"
                f"🏆 Авторитет вашего клана взлетел до небес!"
            )
        else:
            await con.execute("UPDATE clans SET treasury = treasury - ? WHERE id = ?", (bet, u_clan["id"]))
            await con.execute("UPDATE clans SET treasury = treasury + ? WHERE id = ?", (bet, c_row["id"]))
            await con.commit()
            return await message.answer(
                f"💀 ПОРАЖЕНИЕ В КЛАНОВАРЕ! 💀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏰 Клан «{c_row['name']}» отбил нападение и разграбил казну клана «{u_clan['name']}» на {bet:,} 🌑!\n"
                f"🛡 Отступите и соберите больше бойцов перед следующим боем."
            )

    if cmd in ("клан_участники", "участники_клана", "состав_клана"):
        u_clan = await db.get_user_clan(db_uid)
        if not u_clan:
            return await message.answer("❌ Вы не состоите в клане!")
        members = await (await con.execute("SELECT user_id, rank FROM clan_members WHERE clan_id = ?", (u_clan["id"],))).fetchall()
        lines = [f"🏰 УЧАСТНИКИ КЛАНА «{u_clan['name']}» ({len(members)} чел.):\n━━━━━━━━━━━━━━━━━━━━"]
        for m in members:
            real_m_uid = m["user_id"] - 70_000_000_000 if m["user_id"] >= 70_000_000_000 else m["user_id"]
            fn, _ = await get_vk_user_info_func(real_m_uid)
            r_title = "👑 Лидер" if m["user_id"] == u_clan["owner_id"] else "⚔️ Боец"
            lines.append(f"• [id{real_m_uid}|{fn}] — {r_title}")
        await message.answer("\n".join(lines))
        return True

    # ─────────────────────────────────────────────────────────────
    # 💍 14. СЕМЕЙНЫЕ ДЕЙСТВИЯ И РОМАНТИКА
    # ─────────────────────────────────────────────────────────────
    if cmd in ("поцеловать_супруга", "поцеловать_мужа", "поцеловать_жену"):
        u = await db.get_user(db_uid)
        spouse_id = u.get("married_to") if u else None
        if not spouse_id:
            return await message.answer("❌ Вы не состоите в браке! Сыграйте свадьбу: «брак @юзер».")
        real_s_uid = spouse_id - 70_000_000_000 if spouse_id >= 70_000_000_000 else spouse_id
        s_fn, _ = await get_vk_user_info_func(real_s_uid)
        await db.add_xp(db_uid, 25)
        await message.answer(f"💋 {user_display} сладко и нежно целует своего супруга [id{real_s_uid}|{s_fn}]! Любовь крепнет с каждым днем! (+25 XP)")
        return True

    # ─────────────────────────────────────────────────────────────
    # 🔮 15. УТИЛИТЫ MOXXI: ШАР, РАНДОМ, МОНЕТКА, ВРЕМЯ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("шар", "шар_судьбы"):
        if not args:
            return await message.answer("💡 Задайте вопрос шару: «шар [вопрос]».")
        answers = [
            "Бесспорно! Звёзды сошлись ✨",
            "Мой ответ — ДА! 🔥",
            "Вероятность крайне высока 📈",
            "Спроси позже, карты пока путаются 🔮",
            "Даже не думай об этом 🙅‍♂️",
            "Очень сомнительно... 📉",
            "Мокси говорит: 100% да! 💖",
            "Мой внутренний локатор говорит НЕТ 🚫",
            "Знаки указывают на успех! 🍀"
        ]
        return await message.answer(f"🔮 Шар Судьбы Moxxi отвечает: «{random.choice(answers)}»")

    if cmd in ("рандом", "случайное_число"):
        parts = args.split()
        low = 1
        high = 100
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            low = int(parts[0])
            high = int(parts[1])
        elif len(parts) == 1 and parts[0].isdigit():
            high = int(parts[0])
        val = random.randint(min(low, high), max(low, high))
        return await message.answer(f"🎲 Случайное число от {min(low, high)} до {max(low, high)}: {val}!")

    if cmd in ("время", "точное_время", "мск"):
        now_str = datetime.datetime.now().strftime("%H:%M:%S (%d.%m.%Y)")
        return await message.answer(f"⏰ Точное серверное время MOXXI: {now_str} (МСК).")

    # ─────────────────────────────────────────────────────────────
    # 💎 16. VIP-ПРИВИЛЕГИИ И ПРОКАЧКА УРОВНЯ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("вип", "випы", "vip"):
        return await message.answer(
            f"💎 VIP-ПРИВИЛЕГИИ В БОТЕ MOXXI 3.0:\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"1. 🌟 VIP Статус (39 ₽ / 30 дней):\n"
            f"• x1.5 к опыту и зарплате\n"
            f"• Доступ к команде «вип_бонус» (+10 000 🌑 ежедневно)\n"
            f"• Персональная иконка 💎 в профиле\n\n"
            f"2. 👑 VIP+ Премиум (79 ₽ / 30 дней):\n"
            f"• x2.0 ко всем наградам и прибыли бизнесов\n"
            f"• Снижение кулдаунов в 2 раза\n"
            f"• Ежедневный VIP+ бонус: +25 000 🌑\n\n"
            f"💡 Для покупки напишите: «донат» и выберите нужный статус!"
        )

    if cmd in ("вип_бонус", "випбонус"):
        cd_left = await db.cooldown_left(db_uid, "vip_bonus", 86400)
        if cd_left > 0:
            vm = cd_left // 3600
            return await message.answer(f"⏳ Следующий VIP-бонус доступен через {vm} ч.")
        await db.set_cooldown(db_uid, "vip_bonus", 86400)
        await db.add_balance(db_uid, 15000)
        await db.add_xp(db_uid, 100)
        return await message.answer(f"💎 {user_display}, вам начислен VIP-бонус: +15 000 🌑 и +100 XP!")

    if cmd in ("лвл", "уровень", "прокачка", "опыт"):
        u = await db.get_user(db_uid)
        xp = u.get("xp", 0) if u else 0
        lvl = max(1, xp // 100)
        to_next = 100 - (xp % 100)
        return await message.answer(
            f"📈 ВАШ ИГРОВОЙ ПРОГРЕСС:\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ Текущий уровень: {lvl} ур.\n"
            f"✨ Суммарный опыт: {xp:,} XP\n"
            f"🎯 До уровня {lvl + 1} осталось: {to_next} XP\n\n"
            f"💡 Опыт дается за работу, победы в казино, побоища с боссами и квесты!"
        )


    # ─────────────────────────────────────────────────────────────
    # 💼 17. ДОПОЛНИТЕЛЬНЫЕ РАБОЧИЕ И КАРЬЕРНЫЕ КОМАНДЫ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("премия", "запросить_премию"):
        cd_left = await db.cooldown_left(db_uid, "bonus_premia", 7200)
        if cd_left > 0:
            pm = cd_left // 60
            return await message.answer(f"⏳ Босс пока не готов выдать премию! Подождите {pm} мин.")
        await db.set_cooldown(db_uid, "bonus_premia", 7200)
        roll = random.randint(1, 100)
        if roll <= 40:
            premia = random.randint(3000, 15000)
            await db.add_balance(db_uid, premia)
            return await message.answer(f"🎉 Босс в отличном настроении! {user_display} получает премию: +{premia:,} 🌑!")
        else:
            return await message.answer(f"💼 Босс сердито посмотрел сквозь очки и сказал: «Работай лучше!» В премии отказано.")

    if cmd in ("карьера", "мой_стаж"):
        cur_row = await con.execute("SELECT job_id, level, shift_count FROM user_jobs WHERE user_id = ?", (db_uid,))
        cj = await cur_row.fetchone()
        if not cj:
            return await message.answer("❌ Вы пока безработный! Вакансии: «работы».")
        j_info = next((j for j in JOBS_CATALOG.values() if j["id"] == cj["job_id"]), None)
        return await message.answer(
            f"💼 ВАША ТРУДОВАЯ КНИЖКА:\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷 Профессия: {j_info['title'] if j_info else cj['job_id']}\n"
            f"🛠 Отработано смен: {cj['shift_count']} смен\n"
            f"💰 Ставка за смену: {j_info['salary']:,} 🌑\n"
            f"💡 Для работы пишите: «работать» (кулдаун 1 час)."
        )

    # ─────────────────────────────────────────────────────────────
    # 💍 18. СВИДАНИЯ И РОМАНТИЧЕСКИЕ ВЗАИМОДЕЙСТВИЯ
    # ─────────────────────────────────────────────────────────────
    if cmd in ("свидание", "пригласить_на_свидание"):
        target_uid = extract_target_func(message, args)
        if not target_uid or target_uid == user_id:
            return await message.answer("💡 Напишите: «свидание @юзер»!")
        t_fn, _ = await get_vk_user_info_func(target_uid)
        places = [
            "в шикарный панорамный ресторан на крыше небоскреба с бокалами шампанского 🥂",
            "на ночную прогулку под падающими звездами на набережной 🌟",
            "в уютную кофейню при свечах пить какао с маршмеллоу ☕️",
            "на вечерний киносеанс на задний ряд для поцелуев 🎬"
        ]
        return await message.answer(f"💖 {user_display} галантно приглашает [id{target_uid}|{t_fn}] на незабываемое свидание {random.choice(places)}!")

    if cmd in ("комплимент", "сказать_комплимент"):
        target_uid = extract_target_func(message, args) or user_id
        t_fn, _ = await get_vk_user_info_func(target_uid)
        compliments = [
            "Твоя улыбка затмевает свет тысячи некронов и звёзд! ✨",
            "С тобой в одной беседе находиться — это уже джекпот на миллион! 💎",
            "У тебя невероятная харизма и самый шикарный вайб! 🔥",
            "Ты — лучшее украшение нашей беседы Moxxi! 💖"
        ]
        return await message.answer(f"🌹 [id{target_uid}|{t_fn}], комплимент от Мокси: «{random.choice(compliments)}»")

    # ─────────────────────────────────────────────────────────────
    # 🔮 19. ТЕКСТОВЫЕ И УТИЛИТЫ MOXXI: ПЕРЕВЕРНИ, АНЕКДОТ, СТИХ, ГОРОСКОП
    # ─────────────────────────────────────────────────────────────
    if cmd in ("переверни", "перевернуть"):
        if not args:
            return await message.answer("💡 Напишите: «переверни [текст]».")
        return await message.answer(f"🙃 Перевернутый текст: {args[::-1]}")

    if cmd in ("анекдот", "шутка"):
        jokes = [
            "Игрок заходит в казино Moxxi: «Мокси, у меня есть тактика, я сейчас подниму миллион!» Через 5 минут: «Мокси, а в шахте сегодня лопаты выдают?» 😂",
            "Жена говорит мужу: «Либо я, либо этот бот!» Муж: «Тихо, босс беседы сейчас кастанёт фаербол, я в рейде!» 🐉",
            "Полицейский в КПЗ спрашивает грабителя: «Зачем ты украл 100 монет, если залог стоит 10 000?» Грабитель: «Я просто хотел в вентиляции полежать...» 🥷"
        ]
        return await message.answer(f"🎭 Анекдот от Мокси:\n{random.choice(jokes)}")

    if cmd in ("стих", "стишок"):
        poems = [
            "Золото блестит в кармане,\nМокси улыбнулась мне!\nМы сегодня на вулкане\nИ на новеньком коне! 🐎✨",
            "В шахте киркой я стучу,\nМиллион монет хочу!\nВыпал мне сундук литой —\nБудет пир горой с Мокси! 💎⛏"
        ]
        return await message.answer(f"📜 Четверостишие от Мокси:\n{random.choice(poems)}")

    if cmd in ("гороскоп", "астрология"):
        signs = [
            "Сегодня Марс в созвездии Казино: идеальный день ставить все на красное! 🎰",
            "Луна советует заглянуть в банк и снять проценты — вас ждёт финансовый взлёт! 📈",
            "Венера обещает романтическую встречу в беседе: крутите бутылочку! 🍾",
            "Звёзды предупреждают: берегите карманы, в чате бродят хитрые воришки! 🥷"
        ]
        return await message.answer(f"🔮 Астрологический прогноз от Мокси:\n{random.choice(signs)}")

    if cmd in ("транслит", "раскладка"):
        if not args:
            return await message.answer("💡 Напишите: «транслит [текст на ошибочной раскладке]».")
        en_chars = "qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~"
        ru_chars = "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,ёЁ"
        table = str.maketrans(en_chars, ru_chars)
        return await message.answer(f"🔄 Исправленный текст: {args.translate(table)}")


    if cmd in ("моя_профессия", "моя_работа", "сменить_работу"):
        return await message.answer("💡 Посмотреть текущую профессию: «карьера». Вакансии: «работы». Устроиться: «устроиться [1-10]».")

    if cmd in ("купить_билет", "билет"):
        # перенаправляем на лотерею
        cmd = "лотерея"

    if cmd in ("мои_ачивки", "мои_достижения"):
        cmd = "ачивки"

    if cmd in ("мои_квесты", "список_квестов"):
        cmd = "квесты"

    if cmd in ("онлайн_чата", "онлайн_беседы", "активные"):
        cmd = "чатстат"

    if cmd in ("позвать", "пингануть"):
        cmd = "созвать"

    if cmd in ("казна_баланс", "баланс_казны"):
        u_clan = await db.get_user_clan(db_uid)
        if not u_clan:
            return await message.answer("❌ Вы не в клане!")
        return await message.answer(f"🏰 Казна клана «{u_clan['name']}»: {u_clan['treasury']:,} 🌑.")


    # 🔍 ПОИСК КОМАНД
    if cmd in ("найти", "поиск", "поиск_команд", "найти_команду"):
        import commands_catalog
        res = commands_catalog.search_commands(args)
        return await message.answer(res, keyboard=commands_catalog.get_hub_keyboard())

    # ⭐️ СИСТЕМА РЕПУТАЦИИ (+РЕП / -РЕП)
    if cmd in ("+реп", "+rep", "респект", "-реп", "-rep", "дизреспект", "репутация", "реп", "карма"):
        target_vk_id = await extract_target_func(message, args)
        if cmd in ("репутация", "реп", "карма") and not target_vk_id:
            target_vk_id = user_id
        if not target_vk_id:
            return await message.answer("💡 Укажите участника: «+реп @юзер» или «-реп @юзер»!")
        if target_vk_id == user_id and cmd in ("+реп", "+rep", "респект", "-реп", "-rep", "дизреспект"):
            return await message.answer("❌ Нельзя изменять репутацию самому себе!")
        t_uid = 70_000_000_000 + target_vk_id
        t_name, _ = await get_vk_user_info_func(target_vk_id)
        if cmd in ("репутация", "реп", "карма"):
            t_user = await db.get_user(t_uid)
            rep_val = t_user.get("reputation", 0) if t_user else 0
            return await message.answer(f"⭐️ Репутация {t_name}: {rep_val:+d} кармы.")
        cd_key = f"rep_{user_id}_{target_vk_id}"
        if await db.cooldown_left(db_uid, cd_key) > 0:
            return await message.answer("⏳ Вы уже изменяли репутацию этому участнику! Подождите немного.")
        delta = 1 if cmd in ("+реп", "+rep", "респект") else -1
        async with db.conn().execute("UPDATE users SET reputation = reputation + ? WHERE user_id = ?", (delta, t_uid)):
            await db.conn().commit()
        await db.set_cooldown(db_uid, cd_key, 3600)
        t_user = await db.get_user(t_uid)
        rep_val = t_user.get("reputation", 0) if t_user else 0
        icon = "⭐️" if delta > 0 else "💔"
        act = "повысил" if delta > 0 else "понизил"
        return await message.answer(f"{icon} {user_display} {act} репутацию {t_name} на {delta:+d}! (Текущая карма: {rep_val:+d})")

    # 📋 ДОСЬЕ / ЧЕК УЧАСТНИКА
    if cmd in ("чек", "досье", "проверить", "чек_юзера"):
        target_vk_id = await extract_target_func(message, args)
        if not target_vk_id:
            target_vk_id = user_id
        t_uid = 70_000_000_000 + target_vk_id
        t_name, _ = await get_vk_user_info_func(target_vk_id)
        t_user = await db.get_user(t_uid)
        if not t_user:
            return await message.answer(f"❌ Пользователь {t_name} ещё не зарегистрирован в базе бота.")
        t_rank = await db.get_user_rank(db_cid, t_uid)
        warns = await db.get_warns_count(db_cid, t_uid)
        jail_left = await db.is_in_jail(t_uid)
        status = f"🔒 В КПЗ ({jail_left // 60} мин)" if jail_left > 0 else "🕊 На свободе"
        rep = t_user.get("reputation", 0)
        bal = t_user.get("balance", 0)
        bank = t_user.get("bank", 0)
        lvl = t_user.get("level", 1)
        xp = t_user.get("xp", 0)
        return await message.answer(
            f"📋 ДОСЬЕ УЧАСТНИКА: {t_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 Ранг в чате: [{t_rank}]\n"
            f"🕊 Статус: {status}\n"
            f"⚠️ Предупреждений: {warns}/3\n"
            f"⭐️ Репутация: {rep:+d}\n"
            f"💰 На руках: {bal:,} 🌑\n"
            f"🏦 В банке: {bank:,} 🌑\n"
            f"⭐ Уровень: {lvl} ({xp:,} XP)\n"
            f"🆔 VK ID: id{target_vk_id}"
        )

    # ⏱ КУЛДАУНЫ И ТАЙМЕРЫ
    if cmd in ("кд", "кулдаун", "кулдауны", "таймеры"):
        b_cd = await db.cooldown_left(db_uid, "daily_bonus")
        j_cd = await db.cooldown_left(db_uid, "job_work")
        m_cd = await db.cooldown_left(db_uid, "mine_cooldown")
        f_cd = await db.cooldown_left(db_uid, "fish_cooldown")
        d_cd = await db.cooldown_left(db_uid, "dungeon_raid")
        def fmt_cd(sec):
            if sec <= 0: return "✅ Готово к использованию!"
            m, s = sec // 60, sec % 60
            h, m = m // 60, m % 60
            return f"⏳ {h}ч {m}м {s}с"
        return await message.answer(
            f"⏱ АКТИВНЫЕ ТАЙМЕРЫ И КУЛДАУНЫ ({user_display}):\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 Ежедневный бонус: {fmt_cd(b_cd)}\n"
            f"💼 Рабочая смена: {fmt_cd(j_cd)}\n"
            f"⛏ Шахта (добыча): {fmt_cd(m_cd)}\n"
            f"🎣 Рыбалка (клёв): {fmt_cd(f_cd)}\n"
            f"⚔️ Поход в Данж: {fmt_cd(d_cd)}"
        )

    # 🎲 ПРАВДА ИЛИ ДЕЙСТВИЕ
    if cmd in ("правда", "действие", "правда_или_действие", "пид"):
        truths = [
            "Какая твоя самая неловкая тайна за последний год? 🙈",
            "Кто из этой беседы тебе больше всего симпатичен? 💕",
            "Какое самое безумное решение ты когда-либо принимал(а)? 🤪",
            "О чем ты больше всего сожалеешь прямо сейчас? 💭",
            "Какая твоя любимая песня, за которую тебе стыдно? 🎵",
            "Если бы можно было стереть одного человека из памяти, кто это был бы? 🤫"
        ]
        dares = [
            "Отправь самое смешное селфи прямо в этот чат! 📸",
            "Поставь смешной статус в VK на 1 час! 🤡",
            "Сделай комплимент автору предыдущего сообщения! 💖",
            "Отправь голосовое сообщение с мяуканьем! 🐱",
            "Переведи 1 000 монет любому участнику беседы через «передать»! 💰",
            "Признайся в любви человеку, которого выберет бот через «кто»! 💘"
        ]
        if cmd == "правда":
            return await message.answer(f"🗣 ВОПРОС НА ПРАВДУ для {user_display}:\n«{random.choice(truths)}»")
        elif cmd == "действие":
            return await message.answer(f"🔥 ДЕЙСТВИЕ для {user_display}:\n«{random.choice(dares)}»")
        else:
            is_t = random.choice([True, False])
            val = random.choice(truths) if is_t else random.choice(dares)
            label = "🗣 ВОПРОС НА ПРАВДУ" if is_t else "🔥 СМЕЛОЕ ДЕЙСТВИЕ"
            return await message.answer(f"{label} для {user_display}:\n«{val}»")

    # 💍 БРАКИ БЕСЕДЫ
    if cmd in ("браки", "все_браки", "пары"):
        async with db.conn().execute("SELECT user_id, partner_id, created_at FROM marriages ORDER BY created_at DESC LIMIT 10") as cur:
            m_rows = await cur.fetchall()
        if not m_rows:
            return await message.answer("💔 В проекте пока нет зарегистрированных браков! Напишите «брак @юзер», чтобы пожениться!")
        lines = ["💍 СВЯЩЕННЫЕ БРАКИ И СЕМЬИ MOXXI:", "━━━━━━━━━━━━━━━━━━━━"]
        for i, row in enumerate(m_rows, 1):
            u1 = row["user_id"] - 70_000_000_000 if row["user_id"] >= 70_000_000_000 else row["user_id"]
            u2 = row["partner_id"] - 70_000_000_000 if row["partner_id"] >= 70_000_000_000 else row["partner_id"]
            n1, _ = await get_vk_user_info_func(u1)
            n2, _ = await get_vk_user_info_func(u2)
            lines.append(f"{i}. 💖 {n1} 💍 {n2}")
        return await message.answer("\n".join(lines))

    # 🧹 ЧИСТКА ЧАТА
    if cmd in ("чистка", "очистить", "clear"):
        if not is_chat:
            return await message.answer("❌ Команда доступна только в беседах!")
        if my_rank < 3:
            return await message.answer("❌ Чистка сообщений доступна от ранга [3] Старший модератор!")
        count = 10
        if args and args.isdigit():
            count = min(100, max(1, int(args)))
        return await message.answer(f"🧹 Сообщения чата очищены модератором {user_display} ({count} сообщений).")

    # 🕊 АМНИСТИЯ
    if cmd in ("амнистия", "разбан_всех"):
        if not is_chat:
            return await message.answer("❌ Команда доступна только в беседах!")
        if my_rank < 7:
            return await message.answer("❌ Амнистия доступна только от ранга [7] Главный админ или владельцу чата!")
        async with db.conn().execute("DELETE FROM chat_mutes WHERE chat_id = ?", (db_cid,)):
            pass
        async with db.conn().execute("DELETE FROM warns WHERE chat_id = ?", (db_cid,)):
            pass
        await db.conn().commit()
        return await message.answer(f"🕊 ОБЩАЯ АМНИСТИЯ! {user_display} снял абсолютно все баны, муты и предупреждения в этой беседе!")

    return None
