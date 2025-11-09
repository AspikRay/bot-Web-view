import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'ВАШ-ТОКЕН')
ADMIN_IDS = [123456789]  # Замените на ваш Telegram ID
WEBAPP_URL = 'https://subtle-tapioca-286934.netlify.app/'  # URL где будет хоститься Mini App
