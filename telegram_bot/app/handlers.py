### Импорты
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import DataError

### Импорты из файлов
import app.database.requests as rq
import app.keyboards as kb
import app.sup_func as sf


### Инициализация логера модуля
logger = logging.getLogger(__name__)


### Классы состояния
class Reg(StatesGroup):
    """Класс состояния"""
    group = State()
    status = State()
    password = State()
    name = State()


### Подключение роутеров
router = Router()
"""Основной роутер"""


### Ввод переменных
itr_password = 0
"""Попытки введения пароля"""


### стартовая команда
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Команда старт, регистрация

    :param message: Управления сообщениями
    :param state: Управления состояниями
    :return: None
    """
    logger.debug('ЭТАП РЕГИСТРАЦИИ: ВЫБОР ГРУППЫ')
    await message.answer('Меня зовут БИБика, и я твой учебный помощник. Ты можешь найти во мне много полезного')
    if not await rq.get_user_id(message.from_user.id):
        await message.answer('Но мы с тобой не знакомы пока,\nтак что ' + 
                             'расскажи мне, кто ты')
        await state.set_state(Reg.group)
        await message.answer('Выбери свою группу',
                         reply_markup=kb.reg_groups)
    else:
        await message.answer('Что надо?', reply_markup=await kb.main(message.from_user.id))


### регистрация
@router.message(Reg.group)
async def reg_gr(message: Message, state: FSMContext) -> None:
    """Добавление группы студента в состояние

    :param message: Управления сообщениями
    :param state: Управления состояниями
    :return: None
    """
    try:
        if sf.convert_into_group_number(message.text):
            await state.update_data(group=int(message.text))
            await state.set_state(Reg.password)
            await message.answer('Окей, если ты (зам)староста, введи пароль:',
                                    reply_markup=kb.skip)
            logger.debug('ЭТАП РЕГИСТРАЦИИ: ВВОД ПАРОЛЯ')
        else:
            await message.answer('Такой группы нет. Попробуй нажать на одну из кнопок на клавиатуре.')
            await state.set_state(Reg.group)
    except ValueError:
        await message.answer('Номер группы состоит из цифр')
        await state.set_state(Reg.group)


@router.message(Reg.password)
async def check_password(message: Message, state: FSMContext) -> None:
    """Регистрация статуса студента и проверка пароля

       :param message: Управления сообщениями
       :param state: Управления состояниями
       :return: None
    """
    logger.debug('')
    global itr_password
    intermediate_data = await state.get_data()
    if message.text == 'Скип':
        await state.update_data(password=message.text)
        await reg_st(message, state)
        logger.debug('ЭТАП РЕГИСТРАЦИИ: ВВОД ФИО')
    else:
        check = await rq.check_password(intermediate_data['group'], message.text)
        if check:
            await state.update_data(password=message.text)
            await message.answer('Верю')
            await reg_st(message, state)
            logger.debug('ЭТАП РЕГИСТРАЦИИ: ВВОД ФИО')
        elif not check and itr_password < 3:
            itr_password += 1
            await state.update_data(password=message.text)
            await state.set_state(Reg.password)
            await message.answer(f'Пароль не такой!. Еще {3 - itr_password} попытки/а')
        elif itr_password == 2:
            await message.answer('Не верю')
            await reg_st(message, state)
            logger.debug('ЭТАП РЕГИСТРАЦИИ: ВВОД ФИО')


@router.message(Reg.status)
async def reg_st(message: Message, state: FSMContext) -> None:
    """Добавление статуса в состояние

        :param message: Управления сообщениями
        :param state: Управления состояниями
        :return: None
    """
    intermediate_data = await state.get_data()
    check = await rq.check_password(intermediate_data['group'], intermediate_data['password'])
    if not check:
        await state.update_data(status=False)
    else:
        await state.update_data(status=True)
    await state.set_state(Reg.name)
    await message.answer('Давай знакомиться. Введи свои имя и фамилию')


@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext) -> None:
    """Регистрация имени пользователя и добавление данных в базу данных

        :param message: Управления сообщениями
        :param state: Управления состояниями
        :return: None
    """
    try:
        if not sf.check_student_name(message.text):
            await message.answer('В имени не может быть числа')
            await state.set_state(Reg.name)
        else:
            await state.update_data(name=message.text)
            data_reg = await state.get_data()
            await rq.set_user(data_reg['name'], message.from_user.id, data_reg['group'],
                              data_reg['status'])
            await state.clear()
            logger.debug('РЕГИСТРАЦИЯ ЗАВЕРШЕНА')
            await message.answer('Вроде зарегистрировались.\nЧто надо?',
                                 reply_markup=await kb.main(message.from_user.id))
    except DataError:
        await message.answer('Имя слишком длинное.\nМаксимальная длина вводимых данных: 40 символов')
        await state.set_state(Reg.name)


### Учебное
@router.message(F.text == 'Учебное')
async def curricular(message: Message) -> None:
    """Вывод клавиатуры

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Всё для тебя', reply_markup=kb.curricular)


### Расписание
@router.message(F.text == 'Расписание')
async def get_schedule(message: Message) -> None:
    """Вывод расписание группы

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Держи расписание своей группы')
    schedule = await rq.get_schedule(message.from_user.id)
    for i in schedule:
        await message.answer(f'Понедельник:\n{i.monday}\n\nВторник:\n' +
                             f'{i.tuesday}\n\n' +
                             f'Среда:\n{i.wednesday}\n\nЧетверг:\n' +
                             f'{i.thursday}\n\n' +
                             f'Пятница:\n{i.friday}\n\nСуббота:\n{i.saturday}\n')


@router.message(F.text == 'Посещение')
async def user_pass(message: Message) -> None:
    """Вывод пропусков

    :param message: Управления сообщениями
    :return: None
    """
    try:
        await message.answer('Твои пропуски:')
        skips = await rq.get_user_skips(message.from_user.id)
        my_skips = ''
        for skip in skips:
            my_skips += skip
        await message.answer(my_skips)
    except DataError:
        await message.answer('Пропусков пока что не было')


@router.message(F.text == 'Мои дедлайны')
async def begin_deadlines(message: Message) -> None:
    """Вывод дедлайнов группы

    :param message: Управления сообщениями
    :return: None
    """
    try:
        deadlines = await rq.get_deadlines(message.from_user.id)
        sorted_deadlines_list = []
        b_message = ''
        for deadline in deadlines:
            sorted_deadlines_list.append(deadline)
        for deadline in sorted_deadlines_list:
            b_message += (f'{deadline.name_deadline}\n' + f'{deadline.day}.{deadline.month}.{deadline.hour} ' +
                        f'{deadline.hour}:{deadline.minute}\n\n')
        await message.answer(b_message)
    except TelegramBadRequest:
        await message.answer('Активных дедлайнов нет! (happy happy haaappyyy)')


@router.message(F.text == 'Список группы')
async def group_list(message: Message) -> None:
    """Вывод списка группы

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Вот список твоей группы')
    students = await rq.get_group_list(message.from_user.id)
    group_students_list = ''
    for student in students:
        group_students_list += f'{student.username}\n'
    await message.answer(group_students_list)


### Команда /help (она бесполезная)
@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    """Ну есть и есть

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('S O S please some-one-help-me(barca>real)')


### Назад
@router.message(F.text == 'Назад')
async def back_cmd(message: Message, state: FSMContext) -> None:
    """Вспомогательная кнопка назад

    :param message: Управления сообщениями
    :param state: Управление состояниями
    :return: None
    """
    await message.answer('Ну и пожалуйста', reply_markup=await kb.main(message.from_user.id))
    await state.clear()


### Внеучебное
@router.message(F.text == 'Внеучебное')
async def extracurricular(message: Message) -> None:
    """Вывод клавиатуры

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Все для тебя', reply_markup=kb.extracurricular)


### Телеграм-каналы
@router.message(F.text == 'Инфофлуд (телеграм-каналы)')
async def channels(message: Message) -> None:
    """Вывод полезных тг-каналов

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Полезное из каналов', reply_markup=kb.channels)


### Контакты
@router.message(F.text == 'Если кому-то пожаловаться надо (контакты)')
async def contacts_cmd(message: Message) -> None:
    """Вывод клавиатуры с контактами

    :param message: Управления сообщениями
    :return: None
    """
    await message.answer('Полезное из контактов', reply_markup=kb.contacts)


### Контакты (конкретно)
@router.callback_query(F.data == 'Иванов')
async def contact1(callback: CallbackQuery):
    await callback.message.answer('Иванов Федор Ильич\nТелефон: +7 (985) 471-86-23; 15194\n Почта: fivanov@hse.ru')

@router.callback_query(F.data == 'Павлова')
async def contact2(callback: CallbackQuery):
    await callback.message.answer('Павлова Татьяна Александровна\nТелефон: +7 (495) 772-95-90; 11093\n '
                                  'Почта: miem-office@hse.ru')

@router.callback_query(F.data == 'Тестова')
async def contact3(callback: CallbackQuery):
    await callback.message.answer('Тестова Екатерина Алексеевна\nТелефон: +7 (495) 772-95-90; 15179\n '
                                  'Почта: miem-office@hse.ru')

@router.callback_query(F.data == 'Справочная')
async def contact4(callback: CallbackQuery):
    await callback.message.answer('справочная\nТелефон: +7 (495) 771-32-32')

@router.callback_query(F.data == 'П/р')
async def contact5(callback: CallbackQuery):
    await callback.message.answer('для соединения с подразделением/работником\nТелефон: +7 (495) 531-00-00')

@router.callback_query(F.data == 'Прием.комиссия')
async def contact6(callback: CallbackQuery):
    await callback.message.answer('приемная комиссия\nТелефон: (495) 771-32-42; (495) 916-88-44')
