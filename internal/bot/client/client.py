import os
import asyncio
import shutil
from telethon import TelegramClient
from internal.utils.utils import check_path, delete_file

# Получите ваши данные API: API_ID, API_HASH и имя бота (username бота с символом @)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE_NUMBER")  # Ваш номер телефона в формате +79810815128

client = TelegramClient("user_session", API_ID, API_HASH)

async def send_file_to_bot(file_path: str, bot_username: str, caption: str = ""):
    """
    Отправляет файл нашему боту через аккаунт пользователя.
    Если file_path не оканчивается на .mp4 или .mp3, ищет в папке файл с нужным расширением.
    После успешной отправки, папка, содержащая файл, удаляется.
    """
    file_path = await check_path(file_path)

    await client.start(PHONE)
    file = await client.upload_file(file_path, part_size_kb=512)
    result = await client.send_file(bot_username, file, caption=caption)
    print(f"Файл отправлен, id сообщения: {result.id}")

    # Удаляем папку с видео/аудио после отправки
    await delete_file(file_path)