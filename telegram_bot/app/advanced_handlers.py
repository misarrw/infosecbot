### Импорты
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import DataError

### Импорты из файлов
import app.database.requests as rq
import app.keyboards as kb
from app.middlewares import PermissionMiddleware
import app.sup_func as sf
from app.deadline_handlers import Deadline


### Подключение роутеров
advanced_router = Router()
"""Роутер для функций, доступных только старостам"""


class Students(StatesGroup):
    """Класс состояния"""
    student = State()


class Absent(StatesGroup):
    """Класс состояния"""
    name_subject = State()
    username = State()
    gap_number = State()
    selection = State()
    dynamic_gap = State()


class Subjects(StatesGroup):
    """Класс состояния"""
    subject = State()
    subject_skip = State()


class Timetable(StatesGroup):
    """Класс состояния"""
    days = State()


### Подключение к Middleware
advanced_router.message.outer_middleware(PermissionMiddleware())


### Опции для старост
@advanced_router.message(F.text == 'Редактирование данных')
async def edit_data(message: Message) -> None:
    """Вывод клавиатуры с настройками для старосты

    :param message: Управление сообщениями
    :return: None
    """
    await message.answer('Настройки для старост',
                         reply_markup=kb.master_settings)

### Редактирвоание данных
@advanced_router.message(F.text == 'Назначить/редактировать дедлайн')
async def add_deadlines(message: Message, state: FSMContext) -> None:
    """Обновление состояния

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await state.set_state(Deadline.name_deadline)
    await message.answer('Напиши название дедлайна, который хочешь создать.')



@advanced_router.message(F.text == 'Изменить список группы')
async def edit_group_list(message: Message, state: State) -> None:
    """Промежуточна функция к добавлению студентов в список

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await state.set_state(Students.student)
    await message.answer('Введи студентов, которых ты хочешь добавить в список группы\nЕсли хочешь добавить несколько, вводи в разных сообщениях.\nЕсли захочешь остановиться, нажми "Закончить".\n\nОтметим, что ты можешь изменить список только своей группы.', reply_markup=kb.add_students)


@advanced_router.message(Students.student)
async def write_student_name(message: Message, state: State) -> None:
    """Функция добавления студента в общий список группы

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    if message.text == 'Закончить':
        await state.clear()
        await message.answer('Что надо?',
                             reply_markup=await kb.main(message.from_user.id))
    else:
        try:
            group = await rq.get_group(message.from_user.id)
            if await rq.check_student_in_list(message.text):
                await message.answer('Такой студент уже есть в списке вашей группы')
                await state.set_state(Students.student)
            elif not sf.check_student_name(message.text):
                await message.answer('В имени не может быть числа')
                await state.set_state(Students.student)
            else:
                await state.update_data(username = message.text)
                info = await state.get_data()
                await rq.set_group_list(username=info['username'], group = group)
                await state.clear()
                await state.set_state(Students.student)
        except DataError:
            await message.answer('Имя слишком длинное.\nМаксимальная длина вводимых данных: 40 символов')


### пропуски
@advanced_router.message(F.text == 'Отметить пропуски')
async def pick_subject(message: Message, state: FSMContext) -> None:
    """Промежуточная функция к отметке отсутствующих

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await message.answer('Выбери предмет, по которому хочешь отметить отсутствие студента.',
                         reply_markup=await kb.subjects())
    await state.set_state(Absent.name_subject)


@advanced_router.message(Absent.name_subject)
async def pick_subject2(message: Message, state: FSMContext) -> None:
    """Функция добавления предметов в базу данных или выбор способа добавления пропусков

    :param message: Управление сообщениями
    :param state: Управления состояниями
    :return: None
    """
    if message.text == 'Добавить предмет':
        await state.clear()
        await state.set_state(Subjects.subject)
        await message.answer('Напиши название предмета, по которому хочешь отметить отсутствие студента.\n '
                             'Если хочешь добавить несколько, вводи в разных сообщениях.\n'
                             'Когда захочешь остановиться, нажми "Стоп"',
                             reply_markup=kb.add_subjects)
        if message.text == 'Назад':
            await state.clear()
    else:
        await state.update_data(name_subject=message.text)
        await state.set_state(Absent.selection)
        await message.answer('Выбери способ отметить пропуск предмета студентом:', reply_markup=kb.selection)


@advanced_router.message(F.text == 'Автоматически отметить 1 пропуск')
async def mark_absent(message: Message, state: FSMContext) -> None:
    """Промежуточная функция к добавлению пропусков атоматическим способом

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await message.answer('Выбери студентов, отсутствие которых хочешь отметить.\n'
                         'Если захочешь остановиться, нажми "Стоп"',
                             reply_markup=await kb.students(message.from_user.id))
    await state.set_state(Absent.username)
    

@advanced_router.message(Absent.username)
async def student_selection(message: Message, state: FSMContext) -> None:
    """Функция добавления пропусков студентов в базу данных автоматическим способом

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    if message.text == 'Стоп':
        await state.clear()
        await message.answer('Что надо?',
                             reply_markup= kb.main)
    else:
        group = await rq.get_group(message.from_user.id)
        if not await rq.check_student(message.text, group):
            await message.answer('Кажется, такого студента нет((')
        else:
            await state.update_data(username=message.text)
            data_mark = await state.get_data()
            await rq.set_absent(username=data_mark['username'], group=int(group),
                                subject=data_mark['name_subject'], number=1)
        await state.set_state(Absent.username)


@advanced_router.message(F.text == 'Вписать количество пропущенных занятий вручную')
async def set_gap_number(message: Message, state: FSMContext) -> None:
    """Промежуточная функция к добавлению пропусков ручным способом

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await message.answer('Выбери студентов, отсутствие которых хочешь отметить.',
                             reply_markup=await kb.students(message.from_user.id))
    await state.set_state(Absent.gap_number)
    

@advanced_router.message(Absent.gap_number)
async def set_dynamic_gap1(message: Message, state: FSMContext) -> None:
    """Выбор студента для отметки отсутствия в базу данных ручным способом

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    if message.text == 'Стоп':
        await state.clear()
        await message.answer('Что надо?',
                             reply_markup= await kb.main(message.from_user.id))
    else:
        group = await rq.get_group(message.from_user.id)
        if not await rq.check_student(message.text, group):
            await message.answer('Кажется, такого студента нет((')
            await state.set_state(Absent.gap_number)
        else:
            await state.update_data(username=message.text)
            await message.answer('Введи количество пропусков студентом вручную')
            await state.set_state(Absent.dynamic_gap)

    
@advanced_router.message(Absent.dynamic_gap)
async def set_dynamic_gap2(message: Message, state: FSMContext) -> None:
    """Функция добавления пропусков студентов в базу данных автоматическим способом

    :param message: Управление сообщениями
    :param state: Управление состояниями
    :return: None
    """
    try:
        group = await rq.get_group(message.from_user.id)
        if sf.check_value(message.text):
            data_mark = await state.get_data()
            await rq.set_absent(username=data_mark['username'], group=int(group),
                                subject=data_mark['name_subject'], number=int(message.text))
            await state.set_state(Absent.gap_number)
        else:
            await message.answer('Число не может быть меньше 0')
            await state.set_state(Absent.dynamic_gap)
    except ValueError:
        await message.answer('Введи число')
        await state.set_state(Absent.dynamic_gap)


@advanced_router.message(Subjects.subject)
async def add_subject(message: Message, state: FSMContext) -> None:
    """Функция добавления предмета в базу данных

    :param message: Управление сообщениями
    :param state: Управления состояниями
    :return: None
    """
    try:
        if message.text == 'Стоп':
            await message.answer('Выбери предмет, по которому хочешь отметить отсустствие студента.',
                                reply_markup=await kb.subjects())
            await state.clear()
            await state.set_state(Absent.name_subject)
        elif not await rq.add_subject(message.text):
            await message.answer('Такой предмет уже записан.')
            await state.set_state(Subjects.subject)
    except DataError:
        await message.answer('Предмет слишком длинный.\nДопустимая длина вводимых данных: 120 символов')
        await state.set_state(Subjects.subject)

@advanced_router.message(F.text == 'Посмотреть пропуски студентов')
async def pick_subject_skip(message: Message, state: FSMContext) -> None:
    """Выбор предмета для отметки пропуска

    :param message: Управление сообщениями
    :param state: Управление
    :return: None
    """
    await message.answer('Выбери предмет',
                         reply_markup=await kb.subjects())
    await state.set_state(Subjects.subject_skip)


@advanced_router.message(Subjects.subject_skip)
async def print_table_skips(message: Message, state: FSMContext) -> None:
    """Вывод пропуска студентов

    :param message: Управление сообщениями
    :param state: Управление
    :return: None
    """
    if rq.check_subject_in_absent(message.text):
        absents_list = await rq.get_absents(message.from_user.id, message.text)
        ending_str = f'Пропуски предмета "{message.text}":\n' + ''.join(absents_list)
        await message.answer(ending_str)
    else:
        await message.answer('Такого предмета или пропусков по этому предмету нет')
        await state.set_state(Subjects.subject_skip)


@advanced_router.message(F.text == 'Редактировать расписание')
async def edit_timetable(message: Message, state: FSMContext) -> None:
    """Промежуточная функция к добавлению расписания

    :param message: Управления сообщениями
    :param state: Управления состояниями
    :return: None
    """
    await message.answer('Введите расписание. Например:\n1.Аип 3.Матан 4.Алгем\n5.История\nЗанятий нет...')
    await state.set_state(Timetable.days)


@advanced_router.message(Timetable.days)
async def set_timetable(message: Message, state: FSMContext) -> None:
    """Добавление расписания в базу данных

    :param message: Управления сообщениями
    :param state: Управления состояниями
    :return: None
    """
    try:
        if sf.check_format_timetable(message.text):
            group = await rq.get_group(message.from_user.id)
            timetable = message.text.split('\n')
            await rq.set_timetable(int(group), timetable[0], timetable[1], timetable[2], timetable[3], timetable[4],
                                   timetable[5])
            await message.answer('Расписание добавлено')
            await state.clear()
            await message.answer('Что надо?',
                                 reply_markup=await kb.main(message.from_user.id))
        else:
            await message.answer('Пожалуйста введите расписание в соответствие с шаблоном')
            await state.set_state(Timetable.days)
    except ValueError:
        await message.answer('Пожалуйста, введите номер пары')
        await state.set_state(Timetable.days)
