from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url = 'mysql+aiomysql://root:Kk4866336@localhost:3306/bot')

async_session = async_sessionmaker(engine) # подключение к БД

class Base(AsyncAttrs, DeclarativeBase):
    """Родительский класс для таблиц в базе данных"""
    pass


class Absent(Base):
    """Класс создания таблицы пропусков"""
    __tablename__ = 'absents'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(35))
    group: Mapped[int] = mapped_column()
    subject: Mapped[str] = mapped_column(String(120))
    cnt_gap: Mapped[int] = mapped_column()


class Deadline(Base):
    """Класс создания таблицы дедлайнов"""
    __tablename__ = 'deadlines'
    id: Mapped[int] = mapped_column(primary_key=True)
    name_deadline: Mapped[str] = mapped_column(String(120))
    group: Mapped[int] = mapped_column()
    day: Mapped[str] = mapped_column(String(2))
    month: Mapped[str] = mapped_column(String(2))
    year: Mapped[str] = mapped_column(String(4))
    hour: Mapped[str] = mapped_column(String(2))
    minute: Mapped[str] = mapped_column(String(2))


class Subject(Base):
    """Класс создания таблицы предметов"""
    __tablename__ = 'subjects'
    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(120))


class Password(Base):
    """Класс создания таблицы паролей"""
    __tablename__ = 'passwords'
    id: Mapped[int] = mapped_column(primary_key = True)
    group: Mapped[str] = mapped_column(String(6))
    password: Mapped[str] = mapped_column(String(50))



class Schedule(Base):
    """Класс создания таблицы с расписанием"""
    __tablename__ = 'schedules'
    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[int] = mapped_column()
    monday: Mapped[str] = mapped_column(String(1000))
    tuesday: Mapped[str] = mapped_column(String(1000))
    wednesday: Mapped[str] = mapped_column(String(1000))
    thursday: Mapped[str] = mapped_column(String(1000))
    friday: Mapped[str] = mapped_column(String(1000))
    saturday: Mapped[str] = mapped_column(String(1000))
    '''category: Mapped[int] = mapped_column(ForeignKey('categories.id'))'''


class User(Base):
    """Класс создания таблицы со студентами"""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(35))
    tg_id = mapped_column(BigInteger)
    group: Mapped[int] = mapped_column()
    status: Mapped[bool] = mapped_column()


class Students(Base):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40))
    group: Mapped[int] = mapped_column()


async def async_main() -> None:
    """Коннект с базой данных

    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)