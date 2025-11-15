# Finance Bot
Это telegram бот для ведения личных финансовых трат

## Функции
- Добавление трат по категориям. 
```
Пример: еда 500
```
- Добавление своих категорий.
```
Пример: /add Новая_категория
```
- Очистка всей своей статистики по тратам
```
Пример: /clear
```

## Установка и запуск:

1. Скопировать репозиторий
```sh
git clone https://github.com/X-Field/financebot.git
cd financebot
```
2. Создание виртуального окружения
```sh
python -m venv my_env
```
Для виндовс:
```sh
.\my_env\Scripts\activate
```
Для linux:
```sh
source my_env/bin/activate
```
3. Установка зависимостей
```sh
pip install -r requirements.txt
```
Указать токен telegram бота
```sh
touch .env
echo 'TELEGRAM_BOT_TOKEN=(твой токен)' >> .env
```
4. Запуск
```sh
python main.py
```
