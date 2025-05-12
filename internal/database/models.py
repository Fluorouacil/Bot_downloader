from sqlalchemy import Column, Integer, String, DateTime, BigInteger, func, UniqueConstraint, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
# Создаем базу для ORM
Base = declarative_base()

# Модель для пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)                                # Уникальный идентификатор записи
    user_id = Column(BigInteger, nullable=False)                                      # ID пользователя в Telegram
    username = Column(String, nullable=True)                                          # Имя пользователя
    first_name = Column(String, nullable=True)                                        # Имя пользователя
    last_name = Column(String, nullable=True)                                         # Фамилия пользователя
    language_code = Column(String, nullable=True)                                     # Язык пользователя
    created_at = Column(DateTime, server_default=func.now())                          # Время добавления пользователя

    __table_args__ = (UniqueConstraint('user_id', name='uq_user'),)  # Уникальность user_id

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, first_name={self.first_name}, last_name={self.last_name})>"
