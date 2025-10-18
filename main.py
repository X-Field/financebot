#!/usr/bin/python
import os.path

import telebot
import json

API_TOKEN = '8433567433:AAH9bDuB8tEmiQiZIJfkEN3_qI_RmvhoJEo'

bot = telebot.TeleBot(API_TOKEN)

categories = ("еда", "услуги", "игры", "электроника", "обслуживание авто")
data = {}

DATA_FILE = "expenses.json"


def clear_category(category_name: str):
    category_name = category_name.lower().strip()

    if category_name in data:
        data[category_name] = 0
        save_data()
        return True
    else:
        return False


def clear_all_categories():
    global data
    for category in data:
        data[category] = 0
    save_data()


def load_data():
    global data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def add_order(text: str):
    text_list = text.split()
    correct_symbols = "0123456789."
    amount_str: str = text_list[-1]
    current_category = " ".join(text_list[:-1]).lower()
    print(current_category)

    for symbol in amount_str:
        if symbol not in correct_symbols:
            return
    if amount_str == ".":
        return

    amount = float(amount_str)
    if amount == 0:
        return




    if current_category not in categories:
        return



    if current_category in data:
        data[current_category] += amount
    else:
        data[current_category] = amount

    save_data()

    return amount, current_category, data[current_category]


load_data()


@bot.message_handler(commands=['clear'])
def clear_categories(message):
    clear_category()
    bot.reply_to(message, "Отчистка выполнена")



@bot.message_handler(content_types=['text'])
def handle_message(message):
    try:
        text = message.text.strip()

        if text.startswith('Очистить'):
            parts = text.split()
            if len(parts) == 1:
                clear_all_categories()
                bot.reply_to(message, "Все категории очищены!")
                return
            elif len(parts) >= 2:
                category = " ".join(parts[1:])
                if clear_category(category):
                    bot.reply_to(message, f"Категория '{category}' очищена!")
                else:
                    bot.reply_to(message, f"Категория '{category}' не найдена")
                return

        result = add_order(text)

        if result is None:
            bot.reply_to(message, "Не могу найти сумму в сообщении, попробуйте еще раз")
        else:
            amount, category, total = result

            response = f" Добавлено!\n"
            response += f" Сумма: {amount} руб.\n"
            response += f" Категория: {category}\n"
            response += f" Всего в категории: {total:.2f} руб."

            bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f" Ошибка: {str(e)}")


if __name__ == "__main__":
    print("Бот запущен 👍")
    bot.infinity_polling()