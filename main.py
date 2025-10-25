#!/usr/bin/python

import telebot
import json
from telebot import types

API_TOKEN = '8433567433:AAH9bDuB8tEmiQiZIJfkEN3_qI_RmvhoJEo'
bot = telebot.TeleBot(API_TOKEN)

categories = ("еда", "услуги", "игры", "электроника", "обслуживание авто")
data = {}
DATA_FILE = "expenses.json"


def load_data():
    global data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except:
        data = {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def clear_all():
    for category in data: data[category] = 0
    save_data()


def add_expense(text):
    parts = text.split()
    if len(parts) < 2: return
    amount_str, category = parts[-1], " ".join(parts[:-1]).lower()

    if not all(c in "0123456789." for c in amount_str) or amount_str == ".": return
    amount = float(amount_str)
    if amount == 0 or category not in categories: return

    data[category] = data.get(category, 0) + amount
    save_data()
    return amount, category, data[category]


def create_kb(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i + 2])
    return keyboard


def main_kb():
    return create_kb(
        [types.KeyboardButton('Баланс'), types.KeyboardButton('Категории'), types.KeyboardButton('Очистить все')])


def categories_kb():
    buttons = [types.KeyboardButton(cat) for cat in categories] + [types.KeyboardButton('Назад')]
    return create_kb(buttons)


def confirm_kb():
    return create_kb([types.KeyboardButton('Да, очистить все'), types.KeyboardButton('Нет, отменить')])


def final_confirm_kb():
    return create_kb([types.KeyboardButton('Точно очистить!'), types.KeyboardButton('Нет, я не буду чистить')])


user_states = {}
clear_states = {}

load_data()


@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.chat.id] = None
    bot.send_message(message.chat.id, "Бот для учета расходов", reply_markup=main_kb())


@bot.message_handler(commands=['clear'])
def clear_cmd(message):
    clear_all()
    bot.reply_to(message, "Все категории очищены!", reply_markup=main_kb())


@bot.message_handler(content_types=['text'])
def handle_message(message):
    try:
        text, chat_id = message.text.strip().lower(), message.chat.id

        if user_states.get(chat_id):
            amount = float(text)
            category = user_states[chat_id]
            data[category] = data.get(category, 0) + amount
            save_data()
            user_states[chat_id] = None
            bot.reply_to(message, f"Добавлено {amount} руб. в {category}\nВсего: {data[category]:.2f} руб.",
                         reply_markup=main_kb())
            return

        if text == 'баланс':
            response = "Расходы еще не добавлены" if not data else "Общий баланс:\n" + "\n".join(
                [f"• {cat}: {amt:.2f} руб." for cat, amt in data.items()]) + f"\n\nИтого: {sum(data.values()):.2f} руб."
            bot.reply_to(message, response, reply_markup=main_kb())
        elif text == 'категории':
            bot.reply_to(message, "Выберите категорию:", reply_markup=categories_kb())
        elif text == 'очистить все':
            total = sum(data.values())
            if total > 0:
                clear_states[chat_id] = 'first'
                bot.reply_to(message, f"Вы уверены? Будет очищено: {total:.2f} руб.", reply_markup=confirm_kb())
            else:
                bot.reply_to(message, "Нет данных для очистки.", reply_markup=main_kb())
        elif text == 'да, очистить все':
            clear_states[chat_id] = 'second'
            bot.reply_to(message, "Вы тооооочно уверенны????", reply_markup=final_confirm_kb())
        elif text == 'точно очистить!':
            clear_all()
            clear_states[chat_id] = None
            bot.reply_to(message, "Все категории очищены!", reply_markup=main_kb())
        elif text in ['нет, отменить', 'нет, я не буду чистить']:
            clear_states[chat_id] = None
            bot.reply_to(message, "Очистка отменена.", reply_markup=main_kb())
        elif text == 'назад':
            user_states[chat_id] = None
            bot.reply_to(message, "Главное меню:", reply_markup=main_kb())
        elif text in categories:
            user_states[chat_id] = text
            bot.reply_to(message, f"Категория: {text}\nВведите сумму:")
        else:
            result = add_expense(text)
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