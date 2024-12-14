### Импорты
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.database.requests import check_status, get_subjects, get_users


### Стартовая клавиатура
async def main(tg_id) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text='Учебное'))
    keyboard.add(KeyboardButton(text='Внеучебное'))
    if await check_status(tg_id):
        keyboard.add(KeyboardButton(text='Редактирование данных'))
        keyboard.add(KeyboardButton(text = 'Посмотреть пропуски студентов'))
    return keyboard.adjust(1).as_markup(resize_keyboard=True, 
                                        input_field_placeholder='можешь ' +
                                        'выбрать, что тебе нужно')


async def students(tg_id) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    all_name = await get_users(tg_id)
    keyboard.add(KeyboardButton(text='Стоп'))
    names_list = []
    for name in all_name:
        names_list.append(name.username)
    sorted_name_list = sorted(names_list)
    for name in sorted_name_list:
        keyboard.add(KeyboardButton(text=name))
    return keyboard.adjust(3).as_markup(resize_keyboard = True,
                            input_field_placeholder='Нажми, если нужно' + 
                            'остановить процесс')


async def subjects() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    all_subjects = await get_subjects()
    subjects_list = []
    for subject in all_subjects:
        subjects_list.append(subject.subject)
    sorted_subject_list = sorted(subjects_list)
    for subject in sorted_subject_list:
        keyboard.add(KeyboardButton(text=subject))
    keyboard.add(KeyboardButton(text='Добавить предмет'))
    keyboard.add(KeyboardButton(text='Назад'))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


selection = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Автоматически отметить 1 пропуск')],
    [KeyboardButton(text = 'Вписать количество пропущенных занятий вручную')]
], resize_keyboard=True)


### Учебное
curricular = ReplyKeyboardMarkup(keyboard = ([
    [KeyboardButton(text = 'Расписание'),
     KeyboardButton(text = 'Список группы')],
    [KeyboardButton(text = 'Посещение'),
     KeyboardButton(text = 'Мои дедлайны')],
    [KeyboardButton(text = 'Назад')]]),
                    resize_keyboard = True,
                    input_field_placeholder = 'кто любит учиться вообще???')

add_subjects = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Стоп')]
], resize_keyboard=True)

add_students = ReplyKeyboardMarkup(keyboard = ([
    [KeyboardButton(text = 'Закончить')]]), resize_keyboard=True)

### Внеучебное
extracurricular = ReplyKeyboardMarkup(keyboard=([
    [KeyboardButton(text='Инфофлуд (телеграм-каналы)')],
    [KeyboardButton(text='Если кому-то пожаловаться надо (контакты)')],
    [KeyboardButton(text='Назад')]]),
                                resize_keyboard=True,
                                input_field_placeholder='не любим учиться,' +
                                'значит...')

### Редактирование данных
master_settings = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = 'Редактировать расписание'), 
     KeyboardButton(text = 'Изменить список группы')], 
    [KeyboardButton(text = 'Отметить пропуски'), 
     KeyboardButton(text = 'Назначить/редактировать дедлайн')],
    [KeyboardButton(text = 'Назад')]
], resize_keyboard = True, input_field_placeholder = 'Только для старост')

### Выбор группы при регистрации
reg_groups = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='241'), KeyboardButton(text='242')],
    [KeyboardButton(text='243'), KeyboardButton(text='244'), KeyboardButton(text='245')]
], resize_keyboard=True)

### Назад (пропуск действия)
skip = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Скип')]
], resize_keyboard=True)

### Каналы
channels = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Официальный канал ВШЭ',
                          url='https://t.me/hse_official')],
    [InlineKeyboardButton(text='Официальный канал МИЭМ',
                          url='https://t.me/miem_hse')],
    [InlineKeyboardButton(text='Канал с вакансиями',
                          url='https://t.me/hsecareer')],
    [InlineKeyboardButton(text='Канал СНТО',
                          url='https://t.me/snto_miem')],
    [InlineKeyboardButton(text='ЭКСТРА',
                          url='https://t.me/extrahse')],
    [InlineKeyboardButton(text='Movement',
                          url='https://t.me/hse_movement')],
    [InlineKeyboardButton(text='Афиша ВШЭ',
                          url='https://t.me/HSEafisha')],
    [InlineKeyboardButton(text='Обратная сторона BHS',
                          url='https://t.me/bear_head_studio')],
    [InlineKeyboardButton(text='Команда Уймина',
                          url='https://t.me/au_team_news')],
    [InlineKeyboardButton(text='Сплетни',
                          url='https://t.me/inside_hse')]
])

### Да/нет-ка (вроде бесполезно)
choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='yes', callback_data='yes')],
    [InlineKeyboardButton(text='nо', callback_data='no')]
])

### Контакты
contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Иванов (научрук)',
                          callback_data='Иванов')],
    [InlineKeyboardButton(text='Павлова (менеджер)',
                          callback_data='Павлова')],
    [InlineKeyboardButton(text='Тестова (менеджер)',
                          callback_data='Тестова')],
    [InlineKeyboardButton(text='Справочная',
                          callback_data='справочная')],
    [InlineKeyboardButton(text='Подразделение/работник',
                          callback_data='п/р')],
    [InlineKeyboardButton(text='Приемная комиссия',
                          callback_data='прием.комиссия')]
])

### Выбор группы
groups = InlineKeyboardMarkup(inline_keyboard=
                   [[InlineKeyboardButton(text='241', 
                                          callback_data='241')],
                   [InlineKeyboardButton(text='242', 
                                         callback_data='242')],
                   [InlineKeyboardButton(text='243', 
                                         callback_data='243')],
                   [InlineKeyboardButton(text='244', 
                                         callback_data='244')],
                   [InlineKeyboardButton(text='245', 
                                         callback_data='245')]
                   ])
