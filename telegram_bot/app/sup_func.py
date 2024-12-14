import datetime


def check_data(day):
    dt_now = datetime.datetime.now()
    dt_dl = datetime.datetime.strptime(day, "%d.%m.%Y %H:%M")
    return dt_dl > dt_now


def convert_into_group_number(text):
    groups = [241, 242, 243, 244, 245]
    int_text = int(text)
    if int_text in groups:
        return True
    return False


def check_value(gap):
    int_gap = int(gap)
    if int_gap < 0:
        return False
    return True
