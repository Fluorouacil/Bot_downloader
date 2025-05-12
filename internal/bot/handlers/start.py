from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from internal.database.db import get_db_session
from internal.database.models import User
from internal.bot.config.config import DATABASE
from sqlalchemy.future import select

router = Router(name=__name__)

@router.message(CommandStart())
async def start(message: Message):
    if DATABASE:
        async with get_db_session() as session:
            result = await session.execute(
                select(User).filter(User.user_id == message.from_user.id)
            )
            user = result.scalars().first()
            if not user:
                user = User(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language_code=message.from_user.language_code,
                )
                session.add(user)
                await session.commit()
    
    # Отправка приветственного сообщения, адаптированного для скачивания видео с разных платформ
    await message.answer(
        text=(
            "🚀 *Добро пожаловать в Video Downloader Bot!*\n\n"
            "С помощью этого бота вы можете скачивать видео и аудио с множества платформ, включая YouTube, Twitch, Instagram и другие.\n\n"
            "Просто отправьте ссылку на видео – и бот мгновенно начнёт загрузку!"
        ),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
async def help(message: Message):
    await message.answer(
        text = ("Для того чтобы скачать видео просто *отправьте ссылку* на него\n\n"
                "Полный список поддерживаемых сайтов можно найти по ссылке ниже\n"
                "https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md")
    )
