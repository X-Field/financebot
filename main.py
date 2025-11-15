import telebot
from telebot import types
from config import API_TOKEN, DATA_FILE, DEFAULT_CATEGORIES
from utils import (
    load_data, save_data, get_user_data, clear_all,
    add_category, get_categories, add_expense, get_balance
)

print("Загрузка данных...")
users_data = load_data()

bot = telebot.TeleBot(API_TOKEN)
print(" Бот инициализирован успешно!")


def create_kb(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i + 2])
    return keyboard


def main_kb():
    return create_kb([
        types.KeyboardButton('/balance'),
        types.KeyboardButton('/categories')
    ])


def get_help_text():
    return (
        " *Бот для учета расходов*\n\n"
        " *Как добавлять расходы:*\n"
        "Просто напишите: *категория сумма*\n"
        "Например: `еда 500` или `транспорт 150`\n\n"
        "⌨ *Команды:*\n"
        "*/start* - начать работу\n"
        "*/help* - эта справка\n"
        "*/balance* - показать баланс\n"
        "*/categories* - показать категории\n"
        "*/clear* - очистить все расходы\n\n"
        " *Кнопки:*\n"
        "• *Баланс* - ваши расходы по категориям\n"
        "• *Категории* - список всех категорий\n"
        "• *Добавить категорию* - создать новую категорию\n\n"
        " *Совет:* Используйте кнопки для быстрого доступа к функциям!"
    )


@bot.message_handler(commands=['start'])
def start(message):
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
    user_id = message.from_user.id
    clear_all(user_id, users_data)
    bot.reply_to(message, "✅ Все расходы очищены!", reply_markup=main_kb())


@bot.message_handler(commands=['balance'])
def balance_command(message):
    user_id = message.from_user.id
    balance_text = get_balance(user_id, users_data)
    bot.reply_to(message, balance_text, reply_markup=main_kb())


@bot.message_handler(commands=['categories'])
def categories_command(message):
    user_id = message.from_user.id
    categories = get_categories(user_id, users_data)
    if categories:
        text = "📂 Ваши категории:\n• " + "\n• ".join(categories)
    else:
        text = "📂 У вас пока нет категорий"
    bot.reply_to(message, text, reply_markup=main_kb())

@bot.message_handler(commands=["add"])
def add_category_command(message):
    user_id = message.from_user.id
    text = message.text.removeprefix("/add").lstrip()
    if users_data.get(user_id):
        if text and len(text) <= 50:
            if add_category(user_id, text.lower(),users_data):
                bot.reply_to(message, f"✅ Категория '{text}' добавлена!", reply_markup=main_kb())
            else:
                bot.reply_to(message, f"❌ Категория '{text}' уже существует!", reply_markup=main_kb())
        else:
            bot.reply_to(message, "❌ Название категории должно быть от 1 до 50 символов!", reply_markup=main_kb())
        return



@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Обработка добавления расхода
    result = add_expense(user_id, text, users_data)
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
        if text.startswith('/'):
            bot.reply_to(
                message,
                "❌ Неверный формат. Используйте: 'категория сумма'\n"
                "Например: 'еда 500' или 'транспорт 150'\n\n"
                "Напишите /help для справки",
                reply_markup=main_kb()
            )


if __name__ == "__main__":
    print("Запуск бота...")
    bot.infinity_polling()