#!/usr/bin/python

import telebot
import json
from telebot import types

API_TOKEN = '8433567433:AAH9bDuB8tEmiQiZIJfkEN3_qI_RmvhoJEo'
bot = telebot.TeleBot(API_TOKEN)

default_categories = ["еда", "услуги", "игры", "электроника", "обслуживание авто"]
DATA_FILE = "expenses.json"
users_data = {}


def load_data():
    global users_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            users_data = json.load(file)
    except:
        users_data = {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(users_data, file, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            'categories': default_categories.copy(),
            'expenses': {}
        }
        save_data()
    return users_data[user_id]


def clear_all(user_id):
    user_data = get_user_data(user_id)
    for category in user_data['expenses']:
        user_data['expenses'][category] = 0
    save_data()

def add_category(user_id, new_category):
    user_data = get_user_data(user_id)
    if new_category not in user_data["expenses"]:
        user_data["expenses"].append(new_category)
    save_data()

def add_expense(user_id, text):
    user_data = get_user_data(user_id)
    parts = text.split()
    if len(parts) < 2: return
    amount_str, category = parts[-1], " ".join(parts[:-1]).lower()

    if not all(c in "0123456789." for c in amount_str) or amount_str == ".": return
    amount = float(amount_str)
    if amount == 0: return

    user_data['expenses'][category] = user_data['expenses'].get(category, 0) + amount
    save_data()
    return amount, category, user_data['expenses'][category]


def create_kb(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i + 2])
    return keyboard


def main_kb():
    return create_kb([
        types.KeyboardButton('/Баланс'),
        types.KeyboardButton("/Категории",),
    ])

def get_categories(user_id: int) ->list[str]:
    user_data = get_user_data(user_id)
    return users_data["expenses"]


user_states = {}
clear_states = {}

load_data()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from.id)
    user_states[user_id] = None
    bot.send_message(message.chat.id, "Бот для учета расходов", reply_markup=main_kb())

@bot.message_handler(commands=['clear'])
def clear(message):
    user_id = str(message.from.id)
    clear_all(user_id)
    bot.reply_to(message, "Все категории очищены!", reply_markup=main_kb())

@bot.message_handler(commands=['add',"добавить","Add","Добавить"])
def add_user_category(message):
    user_id = str(message.chat.from.id)
    start = message.text.rstript().find(" ")
    if start != -1:
        new_category = message.text[start + 1:]
        add_category(user_id, new_category)
        bot.reply_to(message, f"Новая категория: {new_category} добавлена", reply_markup=main_kb())


@bot.message_handler(commands=["categories", "категории", "Categories", "Категории"])
def categories(message):
    user_id = str(message.chat.user.id)
    categories = get_categories(user_id)
    text = "\n".join(categories)
    bot.reply_to(message, "Все категории:\n" + text, reply_markup=main_kb())


@bot.message_handler(content_types=['text'])
def handle_message(message):
    try:
        text, user_id = message.text.strip().lower(), str(message.from.user.id)
        result = add_expense(user_id, text)
        if result:
            amount, category, total = result
            bot.reply_to(message, f"Добавлено {amount} руб. в {category}\nВсего: {total:.2f} руб.",
                         reply_markup=main_kb())
        else:
            bot.reply_to(message, "Не могу найти сумму", reply_markup=main_kb())

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}", reply_markup=main_kb())


if __name__ == "__main__":
    print("Бот запущен")
    bot.infinity_polling()