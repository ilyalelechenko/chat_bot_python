import re
import datetime


# Проверка ФИО (доработать с регулярками)
def only_letters(message):
    if re.search('[0-9,!@#$%^&*()+=]', message):
        return False
    else:
        return True


def only_numbers(message):
    if re.match('^[0-9+()-]*$', message) is not None:
        return True
    else:
        return False


# Проверка даты рождения
def numbers(message):
    try:
        datetime.datetime.strptime(message, "%d.%m.%Y")
        return True
    except:
        return False
