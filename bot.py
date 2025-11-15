import telebot
from telebot import types

try:
    from config import API_TOKEN, DATA_FILE, DEFAULT_CATEGORIES
    from utils import (
        load_data, save_data, get_user_data, clear_all,
        add_category, get_categories, add_expense, get_balance
    )
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь что все файлы в одной папке:")
    print("- config.py")
    print("- utils.py")
    print("- bot.py")
    print("- .env")
    exit(1)

# Инициализируем бота
try:
    bot = telebot.TeleBot(API_TOKEN)
    print("✅ Бот инициализирован успешно!")
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    exit(1)

user_states = {}


def create_kb(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i + 2])
    return keyboard


def main_kb():
    return create_kb([
        types.KeyboardButton('Баланс'),
        types.KeyboardButton('Категории'),
        types.KeyboardButton('Добавить категорию')
    ])


def get_help_text():
    return (
        "💰 *Бот для учета расходов*\n\n"
        "📝 *Как добавлять расходы:*\n"
        "Просто напишите: *категория сумма*\n"
        "Например: `еда 500` или `транспорт 150`\n\n"
        "⌨️ *Команды:*\n"
        "*/start* - начать работу\n"
        "*/help* - эта справка\n"
        "*/balance* - показать баланс\n"
        "*/categories* - показать категории\n"
        "*/clear* - очистить все расходы\n\n"
        "🔘 *Кнопки:*\n"
        "• *Баланс* - ваши расходы по категориям\n"
        "• *Категории* - список всех категорий\n"
        "• *Добавить категорию* - создать новую категорию\n\n"
        "💡 *Совет:* Используйте кнопки для быстрого доступа к функциям!"
    )


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    user_states[user_id] = None
    bot.send_message(
        message.chat.id,
        get_help_text(),
        parse_mode='Markdown',
        reply_markup=main_kb()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(
        message,
        get_help_text(),
        parse_mode='Markdown',
        reply_markup=main_kb()
    )


@bot.message_handler(commands=['clear'])
def clear_command(message):
    user_id = str(message.from_user.id)
    clear_all(user_id)
    bot.reply_to(message, "✅ Все расходы очищены!", reply_markup=main_kb())


@bot.message_handler(func=lambda message: message.text == 'Добавить категорию')
def add_category_handler(message):
    user_id = str(message.from_user.id)
    user_states[user_id] = 'waiting_for_category'
    bot.reply_to(message, "Введите название новой категории:")


@bot.message_handler(func=lambda message: message.text == 'Категории')
def categories_handler(message):
    user_id = str(message.from_user.id)
    categories = get_categories(user_id)
    if categories:
        text = "📂 Ваши категории:\n• " + "\n• ".join(categories)
    else:
        text = "📂 У вас пока нет категорий"
    bot.reply_to(message, text, reply_markup=main_kb())


@bot.message_handler(func=lambda message: message.text == 'Баланс')
def balance_handler(message):
    user_id = str(message.from_user.id)
    balance_text = get_balance(user_id)
    bot.reply_to(message, balance_text, reply_markup=main_kb())


@bot.message_handler(commands=['balance'])
def balance_command(message):
    user_id = str(message.from_user.id)
    balance_text = get_balance(user_id)
    bot.reply_to(message, balance_text, reply_markup=main_kb())


@bot.message_handler(commands=['categories'])
def categories_command(message):
    user_id = str(message.from_user.id)
    categories = get_categories(user_id)
    if categories:
        text = "📂 Ваши категории:\n• " + "\n• ".join(categories)
    else:
        text = "📂 У вас пока нет категорий"
    bot.reply_to(message, text, reply_markup=main_kb())


@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()

    # Обработка добавления категории
    if user_states.get(user_id) == 'waiting_for_category':
        if text and len(text) <= 50:
            if add_category(user_id, text.lower()):
                bot.reply_to(message, f"✅ Категория '{text}' добавлена!", reply_markup=main_kb())
            else:
                bot.reply_to(message, f"❌ Категория '{text}' уже существует!", reply_markup=main_kb())
        else:
            bot.reply_to(message, "❌ Название категории должно быть от 1 до 50 символов!", reply_markup=main_kb())
        user_states[user_id] = None
        return

    # Обработка добавления расхода
    result = add_expense(user_id, text)
    if result:
        amount, category, total = result
        bot.reply_to(
            message,
            f"✅ Добавлено {amount:.2f} руб. в '{category}'\n"
            f"Всего в категории: {total:.2f} руб.",
            reply_markup=main_kb()
        )
    else:
        # Игнорируем сообщения, которые не являются командами добавления расходов
        if not text.startswith('/'):
            bot.reply_to(
                message,
                "❌ Неверный формат. Используйте: 'категория сумма'\n"
                "Например: 'еда 500' или 'транспорт 150'\n\n"
                "Напишите /help для справки",
                reply_markup=main_kb()
            )


if __name__ == "__main__":
    print("Загрузка данных...")
    load_data()
    print("Запуск бота...")
    bot.infinity_polling()