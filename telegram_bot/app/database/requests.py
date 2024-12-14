from app.database.models import async_session
from app.database.models import User, Password, Schedule, Subject, Deadline, Absent, Students
from sqlalchemy import select
import hashlib


async def add_subject(subject: str) -> bool:
    """Функция добавления предмета в базу данных

    :param subject: Предмет, который добавляем в базу данных
    :type subject: str
    :return: Возвращает усешность процесса
    :rtype: bool
    """
    async with async_session() as session:
        if await session.scalar(select(Subject).where(Subject.subject == subject)):
            return False
        else:
            session.add(Subject(subject=subject))
            await session.commit()
            return True


async def check_password(group: int, password: str) -> bool:
    """Функция проверки пароля

    :param  group: Номер группы пользователя
    :type group: int
    :param password: Введеный пароль
    :type password: str
    :return: Правильность пароля
    :rtype: bool
    """
    async with async_session() as session:
        hash_password = hashlib.md5(password.encode())
        return await session.scalar(select(Password).where(Password.group == group).
                                    where(Password.password == hash_password.hexdigest()))


async def check_subject_in_absent(subject: str) -> bool:
    async with async_session() as session:
        return session.scalar(select(Absent).where(Absent.subject == subject))

async def check_status(tg_id: int) -> bool:
    """Проверка статуса пользователя

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Статус пользователя
    :rtype: bool
    """
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id).where(User.status))


async def check_student(username: str, group: int) -> bool:
    """Проверка наличия студента в группе

    :param username: Имя студента
    :type username: str
    :param group: Группа пользователя
    :type group: int
    :return: Наличие студента в группе
    :rtype: bool
    """
    async with async_session() as session:
        return await session.scalar(select(User).where(User.username == username)
                                       .where(User.group == group))
    

async def check_student_in_list(username: str) -> bool:
    """Проверка на наличие студента в базе данных

    :param username: Имя студента
    :return: Наличие студента в базе данных
    """
    async with async_session() as session:
        return await session.scalar(select(Students).where(Students.username == username))


async def get_absents(tg_id: int, subject: str) -> list:
    """Получение списка с пропусками студентов определенного предмета

    :param tg_id: id пользователя
    :type tg_id: int
    :param subject: Предмет
    :return: Список пропусков
    :rtype: list
    """
    async with async_session() as session:
        group = await get_group(tg_id)
        all_absents = await session.scalars(select(Absent).where(Absent.group == group).where(Absent.subject == subject))
        absents_list = []
        for absent in all_absents:
            absents_list.append(f'{absent.username}: {str(absent.cnt_gap)}\n')
        return sorted(absents_list)


async def get_cnt_gap(username: str) -> int:
    """Получение пропусков студента

    :param username: Имя студента
    :type username: str
    :return: Пропуски студента
    :rtype: int
    """
    async with async_session() as session:
        str_user = await session.scalars(select(Absent).where(Absent.username == username))
        cnt_gap = [i.cnt_gap for i in str_user]
        return cnt_gap[0]


async def get_deadlines(tg_id: int):
    """Получение списка дедлайнов

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Список дедлайнов
    :rtype:
    """
    async with async_session() as session:
        group = await get_group(tg_id)
        return await session.scalars(select(Deadline).where(Deadline.group == group))
    

async def get_group_list(tg_id: int):
    """Полученье списка группы

    :param tg_id: id пользователя
    :return: Список группы
    """
    group = await get_group(tg_id)
    async with async_session() as session:
        return await session.scalars(select(Students).where(Students.group == group))


async def get_group(tg_id: int) -> str:
    """Получение группы пользователя

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Группу пользователя
    :rtype: str
    """
    async with async_session() as session:
        str_user = await session.scalars(select(User).where(User.tg_id == tg_id))
        group = [i.group for i in str_user]
        return group[0]


async def get_schedule(tg_id):
    """Получение расписания

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Расписание
    :rtype:
    """
    async with async_session() as session:
        group_schedule = await get_group(tg_id)
        return await session.scalars(
            select(Schedule).where(Schedule.group == group_schedule))


async def get_subjects():
    """Получение списка предметов

    :return: Список предметов
    :rtype:
    """
    async with async_session() as session:
        return await session.scalars(select(Subject))


async def get_users(tg_id: int):
    """Получение списка студентов в группе

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Список студентов
    :rtype:
    """
    async with async_session() as session:
        group = await get_group(tg_id)
        return await session.scalars(select(User).where(User.group == group))


async def set_timetable(group: int, monday: str, tuesday: str, wednesday: str, thursday: str, friday: str,
                        saturday: str) -> None:
    """Добавление информации о расписание в базу данных

    :param group: Группа пользователя
    :param monday: Расписание на понедельник
    :param tuesday: Расписание на вторник
    :param wednesday: Расписание на среду
    :param thursday: Расписание на четверг
    :param friday: Расписание на пятницу
    :param saturday: Расписание на субботу
    :return: None
    """
    async with async_session() as session:
        session.add(Schedule(group=group, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday,
                             friday=friday, saturday=saturday))
        await session.commit()


async def get_username(tg_id: int) -> str:
    """Получение имени пользователя

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Имя пользователя
    :rtype: str
    """
    async with async_session() as session:
        str_user = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = [i.username for i in str_user]
        return user[0]


async def get_user_id(tg_id: int) -> bool:
    """Проверка наличия пользователя в базе данных

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Наличие пользователя в базе данных
    :rtype: bool
    """
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_skips(tg_id: int) -> list:
    """Получение пропусков пользователя

    :param tg_id: id пользователя
    :type tg_id: int
    :return: Пропуски пользователя
    :rtype: list
    """
    async with async_session() as session:
        user_name = await get_username(tg_id)
        skips = await session.scalars(select(Absent).where(Absent.username == user_name))
        skips_list = []
        for skip in skips:
            skips_list.append(f'{skip.subject}: {str(skip.cnt_gap)}\n')
        return sorted(skips_list)


async def set_absent(username: str, group: int, subject: str, number: int) -> None:
    """Заполнение в базе данных информацию о пропусках студентов

    :param username: Имя студента
    :type username: str
    :param group: Группа студента
    :type group: int
    :param subject: Предмет
    :type subject: str
    :param number: Количество пропусков
    :type number: int
    :rtype: None
    """
    async with async_session() as session:
        if await session.scalar(select(Absent).where(Absent.subject == subject).where(Absent.username
                                                                                              == username)):
            str_absent = await session.scalars(select(Absent).where(Absent.subject == subject)
                                               .where(Absent.username == username))
            if number == 1:
                for i in str_absent:
                    i.cnt_gap += 1
                await session.commit()
            else:
                for i in str_absent:
                    i.cnt_gap = number
                await session.commit()
        else:
            session.add(Absent(username=username, group=group, subject=subject, cnt_gap=number))
            await session.commit()


async def set_deadline(name_deadline: str, group: int, day: str, month: str, year: str, hour: str, minute: str) -> None:
    """Заполнение в базу данных информацию о дедлайнах группы

    :param name_deadline: Название дедлайна
    :type name_deadline: str
    :param group: Номер группы
    :type group: int
    :param day: День дедлайна
    :type day: str
    :param month: Месяц дедлайна
    :type month: str
    :param year: Год дедлайна
    :type year: str
    :param hour: Час дедлайна
    :type hour: str
    :param minute: Минута дедлайна
    :type minute: str
    :rtype: None
    """
    async with async_session() as session:
        session.add(Deadline(name_deadline=name_deadline, group=group, day=day, month = month, year = year, hour = hour,
                             minute = minute))
        await session.commit()


async def set_group_list(username: str, group: int):
    async with async_session() as session:
        session.add(Students(username=username, group=group))
        await session.commit()


async def set_user(name: str, tg_id: int, group: int, status: bool) -> None:
    """Заполнение информации о пользователе в базу данных

    :param name: Имя пользователя
    :type name: str
    :param tg_id: id пользователя
    :type tg_id: int
    :param group: Номер группы пользователя
    :type group: int
    :param status: Статус пользователя
    :type status: bool
    :rtype: None
    """
    async with async_session() as session:
        session.add(User(username=name, tg_id=tg_id, group=group, status=status))
        await session.commit()
