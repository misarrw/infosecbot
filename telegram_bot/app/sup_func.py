import datetime


def check_date(day) -> bool:
    """Проверяет актуальность даты дедлайна
    
    :param day: Вводимая пользователем дата дедлайна
    :type day: string 
    :return: Актуальность даты
    :raises ValueError: если пользователь вводит дату неверного формата 
    """
    current_date = datetime.datetime.now()
    deadline_date = datetime.datetime.strptime(day, "%d.%m.%Y %H:%M")
    return deadline_date > current_date

def convert_into_group_number(text) -> bool:
    """Конвертирует вводимые пользователем данные в интовое значение номера группы и проверяет существования номера группы
    
    :param text: Вводимое пользователем сообщение 
    :return: Результат проверки возможности конвертирования
    :raises ValueError: если пользователь вводит не число
    """
    groups = [241, 242, 243, 244, 245]
    int_text = int(text)
    if int_text in groups:
        return True
    return False


def check_value(gap) -> bool:
    """Конвертирует вводимые пользователем данные в интовое значение количества пропусков и проверяет вводимое значение
    на неотрицательность
    
    :param gap: Вводимое пользователем сообщение
    :return: Результат проверки на неотрицательность
    :raises ValueError: если пользователь вводит не число
    """
    int_gap = int(gap)
    if int_gap < 0:
        return False
    return True


def check_student_name(name: str) -> bool:
    """Проверка наличия цифр в имени студента

    :param name: Имя студента
    :return: Если нет цифр, то True, иначе False
    """
    digits = '0123456789'
    for digit in digits:
        if digit in name:
            return False
    return True


def check_format_timetable(timetable):
    """Проверка формата расписания

    :param timetable: Расписание
    :return: Правильность формата расписания
    """
    weekly_timetable = timetable.split('\n')
    if len(weekly_timetable) != 6:
        return False
    for day in weekly_timetable:
        if day == 'Занятий нет':
            continue
        daily_timetable = day.split(' ')
        for couple in range(len(daily_timetable)-1):
            if int(daily_timetable[couple][0]) > int(daily_timetable[couple+1][0]):
                return False
    return True
