import json
import os

# Определяем константы здесь, если импорт не работает
try:
    from config import DATA_FILE, DEFAULT_CATEGORIES
except ImportError:
    # Fallback значения если config не импортируется
    DATA_FILE = "expenses.json"
    DEFAULT_CATEGORIES = ["еда", "услуги", "игры", "электроника", "обслуживание авто"]

users_data = {}


def load_data():
    global users_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users_data = {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(users_data, file, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            'categories': DEFAULT_CATEGORIES.copy(),
            'expenses': {}
        }
        save_data()
    return users_data[user_id]


def clear_all(user_id):
    user_data = get_user_data(user_id)
    user_data['expenses'] = {}
    save_data()


def add_category(user_id, new_category):
    user_data = get_user_data(user_id)
    if new_category not in user_data['categories']:
        user_data['categories'].append(new_category)
        save_data()
        return True
    return False


def get_categories(user_id):
    user_data = get_user_data(user_id)
    return user_data['categories']


def add_expense(user_id, text):
    user_data = get_user_data(user_id)
    parts = text.split()
    if len(parts) < 2:
        return None

    amount_str, category = parts[-1], " ".join(parts[:-1]).lower()

    if not all(c in "0123456789." for c in amount_str) or amount_str == ".":
        return None

    try:
        amount = float(amount_str)
    except ValueError:
        return None

    if amount <= 0:
        return None

    user_data['expenses'][category] = user_data['expenses'].get(category, 0) + amount
    save_data()
    return amount, category, user_data['expenses'][category]


def get_balance(user_id):
    user_data = get_user_data(user_id)
    if not user_data['expenses']:
        return "Нет расходов"

    balance_text = "Ваши расходы:\n"
    total = 0
    for category, amount in user_data['expenses'].items():
        balance_text += f"{category}: {amount:.2f} руб.\n"
        total += amount

    balance_text += f"\nВсего: {total:.2f} руб."
    return balance_text


# Защита от прямого запуска
if __name__ == "__main__":
    print("Это модуль utils, не предназначен для прямого запуска!")
    print("Запустите bot.py вместо этого.")