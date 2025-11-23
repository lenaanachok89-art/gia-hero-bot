import os
# gia_hero_bot.py
import asyncio
import aiosqlite
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ==========================
# 🔑 ЗАМЕНИТЕ НА СВОЙ ТОКЕН ОТ @BotFather!
BOT_TOKEN = os.getenv("8092728513:AAGkNSv9M6gqeDzyjQCc8CLSgkBXX1PBOdM")
# ==========================

DB_PATH = "gia_quest.db"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =============== ПСИХОЛОГИЧЕСКИЕ УПРАЖНЕНИЯ ===============
PSYCHO_EXERCISES = [
    {
        "name": "Дыхание квадратом",
        "steps": [
            "Вдохни через нос на 4 секунды…",
            "Задержи дыхание на 4 секунды…",
            "Выдохни через рот на 4 секунды…",
            "Подожди 4 секунды перед следующим вдохом…"
        ]
    },
    {
        "name": "Техника заземления «5-4-3-2-1»",
        "steps": [
            "Назови **5** вещей, которые ты **видишь**.",
            "Коснись **4** предметов и почувствуй их текстуру.",
            "Назови **3** звука, которые ты **слышишь**.",
            "Улови **2** запаха (или вспомни любимые).",
            "Сделай **1** глоток воды или пошевели пальцами ног."
        ]
    },
    {
        "name": "Якорь уверенности",
        "steps": [
            "Вспомни момент, когда ты почувствовал себя сильным и уверенным.",
            "Представь его как можно ярче: что ты видел, слышал, чувствовал?",
            "Положи руку на грудь и скажи себе: «Я справлюсь. Я уже справлялся».",
            "Сохрани это ощущение — оно всегда с тобой."
        ]
    },
    {
        "name": "Письмо тревоге",
        "steps": [
            "Возьми лист бумаги и напиши: «Дорогая тревога…»",
            "Расскажи ей всё, что она тебе говорит: «Ты провалишься», «У тебя не получится»…",
            "Теперь ответь ей от себя: «Спасибо, что хочешь меня защитить. Но я могу сам».",
            "Сожги письмо в воображении или аккуратно порви — тревога уходит."
        ]
    },
    {
        "name": "Мини-медитация «Безопасное место»",
        "steps": [
            "Закрой глаза и представь место, где ты чувствуешь себя в безопасности.",
            "Что ты там видишь? Какие цвета, предметы, природа?",
            "Что слышишь? Пение птиц, шум моря, тишину?",
            "Оставайся там 30 секунд. Ты всегда можешь вернуться сюда мысленно."
        ]
    },
    {
        "name": "От стресса к спокойствию",
        "steps": [
            "Сожми кулаки, плечи, челюсть на 5 секунд — почувствуй напряжение.",
            "Резко отпусти всё. Почувствуй, как напряжение уходит.",
            "Повтори 2 раза. Тело учится: «Я могу расслабиться»."
        ]
    },
    {
        "name": "3 добрых слова о себе",
        "steps": [
            "Скажи себе вслух или про себя: «Я…» и добавь 3 добрых качества.",
            "Например: «Я старательный. Я добрый. Я расту».",
            "Повторяй это каждое утро — это твой внутренний щит."
        ]
    },
    {
        "name": "Волна дыхания",
        "steps": [
            "Представь, что твоё дыхание — это волна.",
            "На вдохе волна поднимается — в груди тепло и светло.",
            "На выдохе волна уходит — забирает тревогу и напряжение.",
            "Повтори 5 раз."
        ]
    },
    {
        "name": "Сила маленьких шагов",
        "steps": [
            "Подумай: что самое маленькое, что ты можешь сделать прямо сейчас?",
            "Открыть тетрадь? Написать одну формулу? Сделать один вдох?",
            "Сделай этот шаг. Ты уже начал — это победа."
        ]
    },
    {
        "name": "Объятие себе",
        "steps": [
            "Обними себя за плечи или скрести руки на груди.",
            "Скажи: «Я с тобой. Ты не один».",
            "Держи 20 секунд. Это активирует чувство безопасности."
        ]
    },
    {
        "name": "Границы тревоги",
        "steps": [
            "Представь, что тревога — это гость без приглашения.",
            "Скажи ей: «Я вижу тебя, но сейчас мне нужно готовиться».",
            "Проводи её к двери. Ты хозяин своего пространства."
        ]
    },
    {
        "name": "Ресурс дня",
        "steps": [
            "Подумай: что сегодня тебя порадовало, даже немного?",
            "Это может быть луч солнца, смешная мемасик, поддержка друга.",
            "Сохраняй этот момент в «копилку ресурсов» — он даёт силы завтра."
        ]
    }
]

# =============== ЗАДАНИЯ ОГЭ (Формат: вопрос, варианты, правильный, тип) ===============
TASKS_OGE = {
    "math": [
        ("Чему равна сумма углов треугольника?", ["90°", "180°", "270°", "360°"], "180°", "test"),
        ("Сколько процентов составляет 15 от 60?", ["20%", "25%", "30%", "35%"], "25%", "test"),
        ("Найдите значение √64 + 3²", ["15", "17", "19", "20"], "17", "test"),
        ("Решите уравнение: 2x + 7 = 15", ["3", "4", "5", "6"], "4", "test"),
        ("Чему равен sin(90°)?", ["0", "0.5", "1", "-1"], "1", "test")
    ],
    "bio": [
        ("Сколько хромосом в соматических клетках человека?", ["44", "46", "48", "50"], "46", "test"),
        ("Какой орган выделяет желчь?", ["желудок", "печень", "поджелудочная", "селезёнка"], "печень", "test"),
        ("Процесс деления соматических клеток?", ["мейоз", "митоз", "оплодотворение", "редукция"], "митоз", "test")
    ],
    "social": [
        ("Сколько ветвей власти в РФ?", ["2", "3", "4", "5"], "3", "test"),
        ("Высший закон страны?", ["Устав", "Кодекс", "Конституция", "Декларация"], "Конституция", "test"),
        ("Возраст административной ответственности?", ["14", "16", "18", "21"], "16", "test")
    ],
    "history": [
        ("Год начала Великой Отечественной войны?", ["1939", "1941", "1945", "1917"], "1941", "test"),
        ("Кто крестил Русь?", ["Олег", "Владимир", "Ярослав", "Игорь"], "Владимир", "test"),
        ("Столица РФ при Петре I?", ["Москва", "Киев", "Санкт-Петербург", "Новгород"], "Санкт-Петербург", "test")
    ],
    "physics": [
        ("Сила тяжести на тело 5 кг (g=10)?", ["5 Н", "50 Н", "500 Н", "0.5 Н"], "50 Н", "test"),
        ("Единица напряжения?", ["ампер", "вольт", "ом", "ватт"], "вольт", "test"),
        ("Скорость света (млн м/с)?", ["150", "300", "500", "1000"], "300", "test")
    ],
    "english": [
        ("She ___ to school every day.", ["go", "goes", "going", "went"], "goes", "test"),
        ("There ___ a book on the table.", ["is", "are", "am", "be"], "is", "test"),
        ("Перевод «dream»?", ["мечта", "сон", "день", "ночь"], "мечта", "test")
    ],
    "rus": [
        ("Синоним «доброта»?", ["жестокость", "человеколюбие", "злость", "холодность"], "человеколюбие", "test"),
        ("Глава государства в РФ?", ["Премьер", "Президент", "Спикер", "Генсек"], "Президент", "test")
    ]
}

# =============== ЗАДАНИЯ ЕГЭ (можно расширить) ===============
TASKS_EGE = TASKS_OGE  # Для примера — используем те же

# =============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===============
def get_level_from_points(points: int) -> int:
    if points >= 20: return 4
    if points >= 10: return 3
    if points >= 5: return 2
    return 1

def get_level_title(level: int) -> str:
    return {1: "Новичок", 2: "Искатель", 3: "Герой ГИА", 4: "Мастер уверенности"}.get(level, "Новичок")

def generate_diploma(name: str, title: str, desc: str) -> str:
    border = "🟦" * 24
    n = f"🏅 {name}".center(48)
    t = f"🎖 {title}".center(48)
    d = f"✨ {desc}".center(48)
    return f"{border}\n{n}\n{t}\n{d}\n{border}\n\nВыдано в квесте «Герой ГИА»\nДата: {datetime.now():%d.%m.%Y}"

def get_post_answer_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Продолжить")],
            [KeyboardButton(text="🔄 Выбрать предмет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# =============== БАЗА ДАННЫХ ===============
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                exam_level TEXT DEFAULT 'oge',
                last_subject TEXT,
                confidence_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                anxiety_shield_active BOOLEAN DEFAULT 0,
                shield_activated_at TEXT,
                parents_joined BOOLEAN DEFAULT 0,
                friends_joined BOOLEAN DEFAULT 0,
                teachers_joined BOOLEAN DEFAULT 0,
                awarded_5pts BOOLEAN DEFAULT 0,
                awarded_level3 BOOLEAN DEFAULT 0,
                awarded_team_diploma BOOLEAN DEFAULT 0
            )
        """)
        await db.execute("CREATE TABLE IF NOT EXISTS pending_tests (user_id INTEGER PRIMARY KEY, correct TEXT)")
        try:
            await db.execute("ALTER TABLE users ADD COLUMN last_subject TEXT")
        except aiosqlite.OperationalError:
            pass
        await db.commit()

# =============== ФУНКЦИИ РАБОТЫ С ПОЛЬЗОВАТЕЛЕМ ===============
async def get_user(user_id: int, username: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            await db.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username or "anonymous"))
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
        return row

async def add_confidence_point(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT confidence_points, level FROM users WHERE user_id = ?", (user_id,))
        old_points, old_level = await cursor.fetchone()
        new_points = old_points + 1
        new_level = get_level_from_points(new_points)
        await db.execute("UPDATE users SET confidence_points = ?, level = ? WHERE user_id = ?", (new_points, new_level, user_id))
        await db.commit()

        username = (await get_user(user_id))[1] or "Герой"
        user_name = username.replace("_", " ").title()

        if old_points < 5 and new_points >= 5:
            await db.execute("UPDATE users SET awarded_5pts = 1 WHERE user_id = ?", (user_id,))
            await bot.send_message(user_id, f"🎉 *Поздравляем!*\n\n{generate_diploma(user_name, 'Победитель тревоги', 'За смелость и уверенность!')}", parse_mode="Markdown")

        if old_level < 3 and new_level >= 3:
            await db.execute("UPDATE users SET awarded_level3 = 1 WHERE user_id = ?", (user_id,))
            await bot.send_message(user_id, f"🌟 *Ты — Герой ГИА!*\n\n{generate_diploma(user_name, 'Герой ГИА', 'За упорство и веру в себя!')}", parse_mode="Markdown")

async def check_team_diploma(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT parents_joined, friends_joined, teachers_joined, awarded_team_diploma, username FROM users WHERE user_id = ?", (user_id,))
        p, f, t, awarded, username = await cursor.fetchone()
        if p and f and t and not awarded:
            await db.execute("UPDATE users SET awarded_team_diploma = 1 WHERE user_id = ?", (user_id,))
            name = (username or "Герой").replace("_", " ").title()
            await bot.send_message(user_id, f"👥 *Твоя команда собрана!*\n\n{generate_diploma(name, 'Капитан поддержки', 'За умение объединять близких!')}", parse_mode="Markdown")

async def activate_shield(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT shield_activated_at FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        last_time = row[0] if row and row[0] else None
        if last_time:
            last_dt = datetime.fromisoformat(last_time)
            if datetime.now() - last_dt < timedelta(hours=24):
                return False, last_dt + timedelta(hours=24)
        now = datetime.now().isoformat()
        await db.execute("UPDATE users SET anxiety_shield_active = 1, shield_activated_at = ? WHERE user_id = ?", (now, user_id))
        return True, None

async def join_support_as_ally(owner_id: int, role: str):
    col = {"parent": "parents_joined", "friend": "friends_joined", "teacher": "teachers_joined"}.get(role)
    if not col:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {col} = 1 WHERE user_id = ?", (owner_id,))
    await check_team_diploma(owner_id)

async def get_status(user_id: int):
    user = await get_user(user_id)
    _, _, level_exam, last_sub, conf, level, _, shield_time, p, f, t = user[:10]
    title = get_level_title(level)
    avatar = {1: "🧑‍🎓", 2: "🧭", 3: "🦸", 4: "👑"}.get(level, "🧑‍🎓")
    can = conf >= 5
    if shield_time:
        last = datetime.fromisoformat(shield_time)
        shield = "🛡 Активен до " + (last + timedelta(hours=24)).strftime('%d.%m в %H:%M') if datetime.now() - last < timedelta(hours=24) else "✅ Готов!" if can else f"🔒 +{5 - conf}"
    else:
        shield = "✅ Готов!" if can else f"🔒 +{5 - conf}"
    team = ("👨‍👩‍👧" if p else "") + ("🧑‍🤝‍🧑" if f else "") + ("👩‍🏫" if t else "") or "—"
    return f"{avatar} *{title}*\nОчки: {conf}\n🛡 Щит: {shield}\n👥 Команда: {team}\n\nТы на правильном пути! 💫"

# =============== ОТПРАВКА ТЕСТОВОГО ЗАДАНИЯ ===============
async def send_test_task(user_id: int, question: str, options: list, correct: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO pending_tests (user_id, correct) VALUES (?, ?)", (user_id, correct))
        await db.commit()

    shuffled = options[:]
    random.shuffle(shuffled)
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in shuffled]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(user_id, f"❓ {question}", reply_markup=keyboard)

# =============== ОСНОВНЫЕ ОБРАБОТЧИКИ ===============
@dp.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject = None):
    user_id = message.from_user.id
    username = message.from_user.username

    if command and command.args:
        parts = command.args.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            role, owner_id = parts[0], int(parts[1])
            if role in ["parent", "friend", "teacher"]:
                await join_support_as_ally(owner_id, role)
                await message.answer("✅ Спасибо! Вы в команде поддержки!")
                return

    await get_user(user_id, username)
    await message.answer(
        "🎓 Вы готовитесь к экзаменам!\n\nВыберите ваш уровень:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="9 класс (ОГЭ)")], [KeyboardButton(text="11 класс (ЕГЭ)")]],
            resize_keyboard=True
        )
    )

@dp.message(lambda m: m.text in ["9 класс (ОГЭ)", "11 класс (ЕГЭ)"])
async def select_exam_level(message: Message):
    level = "oge" if "9" in message.text else "ege"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET exam_level = ? WHERE user_id = ?", (level, message.from_user.id))
        await db.commit()
    await show_main_menu(message)

async def show_main_menu(message: Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📚 Задание по предмету"), KeyboardButton(text="🧘 Психоупражнение")],
                [KeyboardButton(text="🛡 Активировать Щит тревоги"), KeyboardButton(text="💬 Настроение")],
                [KeyboardButton(text="👥 Пригласить поддержку"), KeyboardButton(text="📊 Мой статус")],
                [KeyboardButton(text="🆘 Психопомощь")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(lambda m: m.text == "🆘 Психопомощь")
async def btn_help(message: Message):
    support_text = (
        "💙 Ты не один. Всегда можно попросить о помощи.\n\n"
        "📞 **Телефон доверия для детей и подростков (бесплатно, анонимно, 24/7):**\n"
        "🔹 **8-800-2000-122**\n\n"
        "📍 **В твоей школе:**\n"
        "🔹 Школьный психолог — **Елена** — всегда готова помочь очно.\n"
        "🔹 Запись: через классного руководителя или личным сообщением.\n\n"
        "💬 Помни: просить о помощи — это признак силы.\n"
        "Ты важен. Твоя жизнь важна."
    )
    await message.answer(support_text, parse_mode="Markdown")

# =============== ОСТАЛЬНЫЕ КНОПКИ ===============
@dp.message(lambda m: m.text == "📊 Мой статус")
async def btn_status(message: Message):
    await message.answer(await get_status(message.from_user.id), parse_mode="Markdown")

@dp.message(lambda m: m.text == "🛡 Активировать Щит тревоги")
async def btn_shield(message: Message):
    user = await get_user(message.from_user.id)
    if user[4] < 5:
        await message.answer(f"🛡 Нужно 5 очков. У тебя: {user[4]}. Выполни задания!")
        return
    ok, next_time = await activate_shield(message.from_user.id)
    if ok:
        await message.answer("🛡✨ Щит тревоги активирован на 24 часа! Ты в безопасности. 🌿")
    else:
        await message.answer(f"⏳ Следующая активация: {next_time.strftime('%d.%m в %H:%M')}")

@dp.message(lambda m: m.text == "👥 Пригласить поддержку")
async def btn_invite(message: Message):
    uid = message.from_user.id
    base = f"https://t.me/GIAgeroyBot?start="
    await message.answer(
        f"Отправь ссылку тем, кто тебя поддерживает:\n\n"
        f"👨‍👩‍👧 Родители: {base}parent_{uid}\n"
        f"🧑‍🤝‍🧑 Друзья: {base}friend_{uid}\n"
        f"👩‍🏫 Учителя: {base}teacher_{uid}"
    )

@dp.message(lambda m: m.text == "🧘 Психоупражнение")
async def btn_psycho(message: Message):
    exercise = random.choice(PSYCHO_EXERCISES)
    steps = "\n".join(f"**Шаг {i+1}**: {step}" for i, step in enumerate(exercise["steps"]))
    await message.answer(f"🧘 *{exercise['name']}*\n\n{steps}\n\n✅ После выполнения — +1 очко уверенности!", parse_mode="Markdown")
    await add_confidence_point(message.from_user.id)

@dp.message(lambda m: m.text == "💬 Настроение")
async def btn_mood(message: Message):
    await bot.send_poll(
        chat_id=message.chat.id,
        question="🧠 Как ты себя чувствуешь перед ГИА?",
        options=["Спокоен — я готов!", "Немного волнуюсь", "Тревожно, но ищу поддержку", "Тяжело, но не сдаюсь"],
        is_anonymous=False,
        allows_multiple_answers=False
    )
    await message.answer("💬 Спасибо, что поделился настроением!")

@dp.message(lambda m: m.text == "📚 Задание по предмету")
async def btn_subject_task(message: Message):
    subjects = ["Математика", "Русский", "Обществознание", "Биология", "История", "Физика", "Английский"]
    builder = ReplyKeyboardBuilder()
    for s in subjects:
        builder.button(text=s)
    builder.button(text="🔙 Назад")
    builder.adjust(2)
    await message.answer("Выберите предмет:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda m: m.text in ["Математика", "Русский", "Обществознание", "Биология", "История", "Физика", "Английский"])
async def subject_selected(message: Message):
    subject_map = {
        "Математика": "math",
        "Русский": "rus",
        "Обществознание": "social",
        "Биология": "bio",
        "История": "history",
        "Физика": "physics",
        "Английский": "english"
    }
    key = subject_map[message.text]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET last_subject = ? WHERE user_id = ?", (key, message.from_user.id))
        await db.commit()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT exam_level FROM users WHERE user_id = ?", (message.from_user.id,))
        level = (await cursor.fetchone())[0] or "oge"

    tasks = TASKS_EGE.get(key, []) if level == "ege" else TASKS_OGE.get(key, [])
    if not tasks:
        await message.answer("Задания по этому предмету пока не добавлены.", reply_markup=get_post_answer_keyboard())
        return

    question, options, correct, task_type = random.choice(tasks)
    await send_test_task(message.from_user.id, question, options, correct)

# =============== INLINE-КНОПКИ И ОТВЕТЫ ===============
@dp.callback_query(F.data.startswith("ans_"))
async def handle_test_answer(callback: F.callback_query):
    selected = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT correct FROM pending_tests WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            await callback.answer("Задание устарело", show_alert=True)
            return
        correct = row[0]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM pending_tests WHERE user_id = ?", (user_id,))
        await db.commit()

    if selected == correct:
        await add_confidence_point(user_id)
        result_msg = "✅ Верно! +1 очко уверенности! 💯"
    else:
        result_msg = f"🤔 Почти! Правильный ответ: **{correct}**"

    await callback.message.edit_text(result_msg, parse_mode="Markdown")
    await bot.send_message(user_id, "Что дальше?", reply_markup=get_post_answer_keyboard())
    await callback.answer()

# =============== КНОПКИ ПОСЛЕ ОТВЕТА ===============
@dp.message()
async def handle_post_answer_buttons(message: Message):
    text = message.text.strip() if message.text else ""
    
    if text == "✅ Продолжить":
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT last_subject FROM users WHERE user_id = ?", (message.from_user.id,))
            row = await cursor.fetchone()
            if row and row[0]:
                fake_msg = type('obj', (object,), {
                    'from_user': message.from_user,
                    'chat': message.chat,
                    'text': [k for k, v in {"Математика": "math", "Русский": "rus", "Обществознание": "social", "Биология": "bio", "История": "history", "Физика": "physics", "Английский": "english"}.items() if v == row[0]][0]
                })
                await subject_selected(fake_msg)
            else:
                await show_main_menu(message)
        return

    if text == "🔄 Выбрать предмет":
        await btn_subject_task(message)
        return

    if any(kw in text.lower() for kw in ["боюсь", "страшно", "стресс", "не получится", "тревога"]):
        memes = [
            "😅 *'Когда понимаешь, что всё получится... просто чуть позже'*",
            "🥲 *'Когда боишься, но всё равно идёшь вперёд'*",
            "🦸 *'Я — герой своего пути'*"
        ]
        await message.answer(random.choice(memes), parse_mode="Markdown")

# =============== ЗАПУСК ===============
async def main():
    await init_db()
    print("🚀 @GIAgeroyBot запущен! Все функции активны.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())