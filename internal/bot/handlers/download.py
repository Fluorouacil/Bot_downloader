import re
import asyncio
import grpc
import logging
from aiogram import Router, F, Bot
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery, ReactionTypeEmoji, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from internal.pb.python import downloader_pb2, downloader_pb2_grpc
from internal.bot.config.config import GRPC_DOWNLOADER_ADDRESS
from internal.bot.client.client import send_file_to_bot
from internal.utils.utils import check_path, delete_file

router = Router(name=__name__)

async def get_available_qualities(link: str) -> list:
    """
    Запускает yt-dlp для получения доступных качеств видео.
    Исключает качества выше 1080p.
    Если не удаётся определить, возвращает значение по умолчанию.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            "yt-dlp", "-F", link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        qualities = set()
        for line in stdout.decode().splitlines():
            # Ищем строки с разрешением вида 360p, 480p, 720p и т.д.
            match = re.search(r"(\d{3,4}p)", line)
            if match:
                qualities.add(match.group(1))

        if qualities:
            # Преобразуем в список и фильтруем: только <= 1080p
            valid_qualities = [q for q in qualities if int(q.replace("p", "")) <= 1080]
            return sorted(valid_qualities, key=lambda x: int(x.replace("p", "")))
    except Exception as e:
        pass

    return ["720p"]  # значение по умолчанию

@router.message(F.text.startswith("http"))
async def handle_download_link(message: Message, state: FSMContext, bot: Bot):
    link = message.text.strip()
    await message.react([ReactionTypeEmoji(emoji="👀")])  # Отправляем реакцию "в ожидании"
    # Если ссылка относится к YouTube, используем логику выбора качества
    if "youtube" in link.lower():
        await state.update_data(download_link=link)
        available_qualities = await get_available_qualities(link)
        keyboard = InlineKeyboardBuilder()
        for qual in available_qualities:
            keyboard.button(
                text=f"{qual}",
                callback_data=f"download:{qual}"
            )
        keyboard.adjust(2)
        keyboard.row(
            InlineKeyboardButton(text="Mp3", callback_data="download:mp3")
        )
        await message.answer(
            "Выберите качество видео или скачивание в формате Mp3:",
            reply_markup=keyboard.as_markup()
        )
        return

    # Для всех остальных ссылок (например, Instagram, Twitch и прочих) - упрощенная логика
    async def call_download_other():
        try:
            async with grpc.aio.insecure_channel(GRPC_DOWNLOADER_ADDRESS) as channel:
                stub = downloader_pb2_grpc.DownloaderStub(channel)
                request = downloader_pb2.DownloadRequest(
                    url=link,
                    quality="",  # качество не выбирается
                    chat_id=str(message.chat.id),
                    message_id=str(message.message_id),
                    user_id=str(message.from_user.id),
                )
                response = await stub.DownloadVideo(request)
                if response.file_path:
                    if response.file_size > 50 * 1024**2:
                        bot_me = await bot.get_me()
                        full_username = "@" + bot_me.username if bot_me.username else bot_me.first_name
                        await send_file_to_bot(response.file_path, full_username, caption=f"{message.from_user.id}")
                    else:
                        file = await check_path(response.file_path)
                        if file.endswith(".mp4"):
                            await bot.send_video(message.from_user.id, FSInputFile(path=file), caption="Ваше видео готово!")
                        else:
                            await bot.send_audio(message.from_user.id, FSInputFile(path=file), caption="Ваше аудио готово!")
                        await delete_file(file)
                else:
                    await message.answer("Загрузка завершилась, но файл не найден.")
        except Exception as e:

            print(f"Ошибка при обращении к сервису загрузки: {e}")

    await message.answer("Загрузка началась...")
    asyncio.create_task(call_download_other())

@router.callback_query(F.data.startswith("download:"))
async def process_download_choice(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    link = data.get("download_link")
    if not link:
        await callback_query.message.answer("Ссылка не найдена, повторите попытку.")
        return
    
    # callback_data в формате "download:<choice>"
    _, choice = callback_query.data.split(":", maxsplit=1)
    quality = choice if choice != "mp3" else ""
    message_id = str(callback_query.message.message_id)
    user_id = str(callback_query.from_user.id)

    async def call_download():
        try:
            async with grpc.aio.insecure_channel(GRPC_DOWNLOADER_ADDRESS) as channel:
                stub = downloader_pb2_grpc.DownloaderStub(channel)
                if choice == "mp3":
                    request = downloader_pb2.DownloadRequest(
                        url=link,
                        quality="",
                        chat_id=user_id,
                        message_id=message_id,
                        user_id=user_id,
                    )
                    response = await stub.DownloadAudio(request)
                else:
                    request = downloader_pb2.DownloadRequest(
                        url=link,
                        quality=quality,
                        chat_id=user_id,
                        message_id=message_id,
                        user_id=user_id,
                    )
                    response = await stub.DownloadVideo(request)
            if response.file_path:
                if response.file_size > 50 * 1024**2:
                    bot_me = await bot.get_me()
                    full_username = "@" + bot_me.username if bot_me.username else bot_me.first_name
                    await send_file_to_bot(response.file_path, full_username, caption=f"{callback_query.from_user.id}")
                else:
                    file = await check_path(response.file_path)
                    if file.endswith(".mp4"):
                        await bot.send_video(callback_query.from_user.id, FSInputFile(path=file), caption="Ваше видео готово!")
                    else:
                        await bot.send_audio(callback_query.from_user.id, FSInputFile(path=file), caption="Ваше аудио готово!")
            else:
                await callback_query.message.answer("Загрузка завершилась, но файл не найден.")
        except Exception as e:
            print(f"Ошибка при обращении к сервису загрузки: {e}")

    await callback_query.message.edit_text("Загрузка началась...")
    asyncio.create_task(call_download())
    await state.clear()

