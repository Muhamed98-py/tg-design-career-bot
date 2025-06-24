import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {
        "text": "1️⃣ Представьте, что вы в новом городе. Что вам интереснее всего?",
        "options": [
            ("Архитектура и планировка", "space"),
            ("Магазины с необычным оформлением", "branding"),
            ("Шоурумы и дизайнерские ателье", "fashion"),
            ("Арт-инсталляции и реклама", "illustration"),
            ("Музыка и звуки улиц", "sound"),
            ("Технологичные пространства", "digital")
        ]
    },
    {
        "text": "2️⃣ С чего вы начинаете проект?",
        "options": [
            ("Ищу атмосферу и вдохновение", "art_direct"),
            ("Изучаю контекст и аналитику", "info"),
            ("Строю схему, структуру", "ux"),
            ("Представляю визуальный образ", "illustration"),
            ("Общаюсь с людьми, понимаю потребности", "interior"),
            ("Делаю черновой прототип", "3d")
        ]
    },
    {
        "text": "3️⃣ Что из этого вам ближе всего?",
        "options": [
            ("Черчение и техника", "product"),
            ("История и анализ визуальной культуры", "illustration"),
            ("Создание визуальных историй", "branding"),
            ("Прототипирование и 3D", "3d"),
            ("Создание визуальных презентаций", "ux"),
            ("Композиция и эстетика дизайна", "interior")
        ]
    },
    {
        "text": "4️⃣ Какой предмет вас больше всего вдохновляет?",
        "options": [
            ("Фотокамера или визуальный медиапродукт", "photo"),
            ("Пояс или аксессуар художественной направленности", "fashion"),
            ("Музыкальные инструменты", "sound"),
            ("Скетчбук с иллюстрациями", "illustration"),
            ("3D-прототип или макет", "3d"),
            ("План или макет помещения/пространства", "space")
        ]
    },
    {
        "text": "5️⃣ Что для вас важнее всего в работе?",
        "options": [
            ("Вдохновение и эстетика", "branding"),
            ("Четкость процессов и структуры", "ux"),
            ("Материал и детали", "fashion"),
            ("Формы и пространство", "interior"),
            ("Функциональность изделия", "product"),
            ("Эмоция через звук или движение", "sound")
        ]
    },
    {
        "text": "6️⃣ Что бы вы с удовольствием освоили?",
        "options": [
            ("Работу с изображениями и нейросетями", "illustration"),
            ("3D‑редактор и VR/AR", "3d"),
            ("Графический интерфейс", "ux"),
            ("Швейное производство", "fashion"),
            ("Звукорежиссуру", "sound"),
            ("Интерьерный чертёж", "space")
        ]
    },
    {
        "text": "7️⃣ Какой из следующих проектов вам интересен?",
        "options": [
            ("Видео-инсталляция с музыкой", "sound"),
            ("Бренд и логотип для компании", "branding"),
            ("Инфографика для СМИ", "info"),
            ("3D-модель продукта", "3d"),
            ("Каталог мебели или декора", "interior"),
            ("Коллекция одежды", "fashion")
        ]
    },
    {
        "text": "8️⃣ В команде вы бы были...",
        "options": [
            ("Креативным лидером концептов", "art_direct"),
            ("Техником или инженерным специалистом", "product"),
            ("Візуализатором, автором образов", "illustration"),
            ("UX/UI аналитиком", "ux"),
            ("Организатором пространства", "space"),
            ("Музыкальным/звуковым оформителем", "sound")
        ]
    },
    {
        "text": "9️⃣ Какую атмосферу вы хотите создавать?",
        "options": [
            ("Инновационную и технологичную", "digital"),
            ("Теплую и уютную через вещи", "interior"),
            ("Эмоциональную через звук или движение", "sound"),
            ("Красочную и выразительную", "illustration"),
            ("Стильную через одежду и аксессуары", "fashion"),
            ("Информативную и понятную", "info")
        ]
    },
    {
        "text": "🔟 Если это был бы ваш первый проект, вы бы сделали...",
        "options": [
            ("Мини-фильм или анимацию", "sound"),
            ("3D-концепт продукта", "3d"),
            ("Интерьер или ландшафт пространства", "space"),
            ("Иллюстрированную историю", "illustration"),
            ("Брендбук или визуальную айдентику", "branding"),
            ("Инфографику для статьи", "info")
        ]
    },
]

RECOMMENDATIONS = {
    "branding": {"title": "Коммуникационный дизайн / Арт-дирекшн", "courses": ["Коммуникационный дизайн. Базовый курс", "Арт-дирекшн"]},
    "illustration": {"title": "Современная иллюстрация / История искусства", "courses": ["Современная иллюстрация: от графики до нейросетей", "История искусства и дизайна"]},
    "fashion": {"title": "Дизайн одежды / Конструирование", "courses": ["Дизайн одежды. Базовый курс", "Конструирование одежды", "Фэшн-индустрия: Продакт-менеджмент"]},
    "interior": {"title": "Интерьер / Ландшафт", "courses": ["Дизайн интерьера", "Ландшафтный дизайн"]},
    "product": {"title": "Промышленный дизайн", "courses": ["Современные практики промышленного дизайна"]},
    "3d": {"title": "3D-графика / Unreal / Геймдизайн", "courses": ["3D художник", "Художник в Unreal Engine", "Геймдизайн: Базовый курс"]},
    "sound": {"title": "Саунд-дизайн и анимация", "courses": ["Саунд-продакшн", "Анимация: Базовый курс"]},
    "digital": {"title": "Цифровой дизайн / UX", "courses": ["Цифровой дизайн: Базовый курс"]},
    "info": {"title": "Инфографика и визуальная аналитика", "courses": ["Основы инфографики"]},
    "ux": {"title": "UX / Продуктовый дизайн", "courses": ["Цифровой дизайн: Базовый курс", "Геймдизайн: Базовый курс"]},
    "space": {"title": "Пространственный дизайн", "courses": ["Дизайн интерьера", "Ландшафтный дизайн", "Современные практики промышленного дизайна"]}
}

user_state = {}

ASKING = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_state[uid] = {"step": 0, "scores": {}}
    await update.message.reply_text("Привет! Начнём тест. Отвечай, выбирая один вариант.")
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = user_state[uid]
    step = state["step"]
    if step >= len(QUESTIONS):
        return await show_result(update, context)

    q = QUESTIONS[step]
    buttons = [[KeyboardButton(opt[0])] for opt in q["options"]]
    reply = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(q["text"], reply_markup=reply)
    state["step"] += 1
    return ASKING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = user_state[uid]
    selected = update.message.text
    prev_step = state["step"] - 1
    q = QUESTIONS[prev_step]

    for text, tag in q["options"]:
        if text == selected:
            state["scores"][tag] = state["scores"].get(tag, 0) + 1
            break

    return await ask_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    scores = user_state[uid]["scores"]
    top = sorted(scores.items(), key=lambda x: -x[1])[:2]
    reply = "🎯 <b>Вам подходят направления:</b>\n\n"
    for tag, _ in top:
        rec = RECOMMENDATIONS[tag]
        reply += f"<b>{rec['title']}</b>\n"
        for c in rec["courses"]:
            reply += f"— {c}\n"
        reply += "\n"
    await update.message.reply_text(reply, parse_mode="HTML")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён. /start — начать заново.")
    return ConversationHandler.END

def main():
    import os
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
