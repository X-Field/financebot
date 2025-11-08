import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATA_FILE = "expenses.json"
DEFAULT_CATEGORIES = ["еда", "услуги", "игры", "электроника", "обслуживание авто"]