from dotenv import load_dotenv
import os
from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from collections import defaultdict

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE = bool(os.getenv("DATABASE"))

admins = list(map(int, os.getenv("ADMINS", "").split(",")))

GRPC_DOWNLOADER_ADDRESS = os.getenv("DOWNLOADER_SERVICE")

# Инициализация бота и диспетчера с использованием памяти для хранения состояний
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
# Инициализация роутера
routers = []

media_groups = defaultdict(lambda: {'messages': [], 'caption': None})
media_group_tasks = {}