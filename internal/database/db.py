from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from internal.bot.config.config import DATABASE_URL
from .models import Base

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=False)
# Создание сессии
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_db_session() -> AsyncSession:
    """
    Возвращает контекстный менеджер для работы с сессией базы данных.
    """
    return async_session()

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создание всех таблиц, если они не существуют
