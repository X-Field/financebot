import telebot
from telebot import types
from config import API_TOKEN
from utils import (
    load_data, save_data, get_user_data, clear_all,
    add_category, get_categories, add_expense, get_balance
)

bot = telebot.TeleBot(API_TOKEN)
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
        types.KeyboardButton('Добавить категорию'),
        types.KeyboardButton('Очистить все')
    ])


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    user_states[user_id] = None
    bot.send_message(
        message.chat.id,
        "💰 Бот для учета расходов\n\n"
        "Как использовать:\n"
        "• Для добавления расхода напишите: 'категория сумма'\n"
        "• Например: 'еда 500' или 'транспорт 150'\n\n"
        "Используйте кнопки для управления:",
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda message: message.text == 'Очистить все')
def clear_handler(message):
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
        bot.reply_to(
            message,
            "❌ Неверный формат. Используйте: 'категория сумма'\n"
            "Например: 'еда 500' или 'транспорт 150'",
            reply_markup=main_kb()
        )


if __name__ == "__main__":
    load_data()
    print("Бот запущен...")
    bot.infinity_polling()