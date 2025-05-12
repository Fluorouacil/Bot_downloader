from aiogram import Router, Bot, F
from aiogram.types import Message

router = Router(name=__name__)

@router.message(F.video)
async def forward_client_video(message: Message, bot: Bot):
    """
    Обрабатывает видео, присланное клиентом.
    Предполагается, что в caption содержится chat_id, куда должно быть перенаправлено видео.
    Видео отправляется в указанный чат с подписью "Ваше видео готово!".
    """
    if not message.caption:
        await message.answer("Ошибка: в подписи отсутствует chat_id для пересылки видео!")
        return

    target_chat_id = message.caption.strip()  # caption содержит chat_id
    try:
        await bot.send_video(
            chat_id=target_chat_id,
            video=message.video.file_id,
            caption="Ваше видео готово!"
        )
        await message.answer("Видео успешно отправлено!")
    except Exception as e:
        await message.answer(f"Ошибка при отправке видео: {e}")

@router.message(F.audio)
async def forward_client_audio(message: Message, bot: Bot):
    """
    Обрабатывает аудио, присланное клиентом.
    Предполагается, что в caption содержится chat_id, куда должно быть перенаправлено аудио.
    Аудио отправляется в указанный чат с подписью "Ваше аудио готово!".
    """
    if not message.caption:
        await message.answer("Ошибка: в подписи отсутствует chat_id для пересылки аудио!")
        return

    target_chat_id = message.caption.strip()
    try:
        await bot.send_audio(
            chat_id=target_chat_id,
            audio=message.audio.file_id,
            caption="Ваше аудио готово!"
        )
        await message.answer("Аудио успешно отправлено!")
    except Exception as e:
        await message.answer(f"Ошибка при отправке аудио: {e}")