import re
import datetime


# Проверка ФИО (доработать с регулярками)
def only_letters(message):
    return bool(re.search("[0-9,!@#$%^&*()+=]", message))


# Проверка номера телефона
def only_numbers(message):
    return bool(re.match('^[0-9+()-]*$', message) is not None)


# Проверка даты рождения
def numbers(message):
    try:
        datetime.datetime.strptime(message, "%d.%m.%Y")
        return True
    except ValueError:
        return False
