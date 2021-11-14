import os
import telebot
from string import Template
import datetime
import validate as val


bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
chat_id = os.environ.get('CHAT_ID')
now_dt = datetime.datetime.now() + datetime.timedelta(hours=7, minutes=0)
user_dict = {}


# Заполняем словарь данными
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.fullname = 'fullname'
        self.type = 'type'
        self.subunit = 'subunit'
        self.contacts = 'contact'
        self.birthday = 'birthday'
        self.pers_inform = 'pers_inform'


# Обработчик команды старт
@bot.message_handler(commands=['start'])
# Функция обработки старт
def first_start(message):
    user_id = message.from_user.id
    user_dict[user_id] = User(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton('Восстановить пароль')
    markup.add(btn1)
    bot.send_message(message.chat.id, f'Добрый день, {message.from_user.first_name}, я бот "НГАСУ (Сибстрин)"',
                     reply_markup=markup)
    bot.register_next_step_handler(message, start)


# Выбор функции восстановление пароля. Начала цепи последовательных ответов
def start(message):
    markup1 = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.text in ('Восстановить пароль', 'Запустить бота', 'Изменить данные'):
        bot.send_message(message.chat.id, 'Для восстановления пароля',
                         reply_markup=markup1)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton('Я сотрудник', callback_data='employee'))
        markup.add(telebot.types.InlineKeyboardButton('Я студент', callback_data='student'))
        markup.add(telebot.types.InlineKeyboardButton('Я абитуриент', callback_data='Entrant'))
        bot.send_message(message.chat.id, 'Выберите из спика:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Извините, мой функционал еще маленький, попробуйте начать сначала /start',
                         reply_markup=markup1)
        bot.register_next_step_handler(message, first_start)


# Обработка кнопок ответа(инлайн кейборд)
@bot.callback_query_handler(func=lambda call: call.data in ['employee', 'student', 'Entrant'])
# Записываем ID пользователя, обрабатываем инлайн клавиатуру
def query_handler(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    user_id = message.from_user.id
    user = user_dict[user_id]
    text_mes = 'Введите ваше ФИО:'
    if message.data == 'employee':
        user.type = 'Сотрудник'
        bot.send_message(message.message.chat.id, text_mes)
        bot.register_next_step_handler(message.message, subunit)
    elif message.data == 'student':
        user.type = 'Студент'
        bot.send_message(message.message.chat.id, text_mes)
        bot.register_next_step_handler(message.message, student)
    elif message.data == 'Entrant':
        user.type = 'Абитуриент'
        bot.send_message(message.message.chat.id, 'test')
        # bot.register_next_step_handler(message.message, Entrant)
    bot.edit_message_reply_markup(message.message.chat.id, message.message.message_id)


# Обработка ответа сотрудник
def subunit(message):
    if val.only_letters(message.text):
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные')
        bot.send_message(message.chat.id, 'Введите ваше ФИО')
        bot.register_next_step_handler(message, subunit)
    else:
        user_id = message.from_user.id
        user = user_dict[user_id]
        user.fullname = message.text
        bot.send_message(message.chat.id, 'Введите ваше подразделение')
        bot.register_next_step_handler(message, birthday)


# Обработка ответ абитуриент
# def Entrant(message):
#   bot.send_message(message.chat.id, 'Тест')


# Обработка ответ студент
def student(message):
    if val.only_letters(message.text):
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные')
        bot.send_message(message.chat.id, 'Введите ваше ФИО')
        bot.register_next_step_handler(message, student)
    else:
        user_id = message.from_user.id
        user = user_dict[user_id]
        user.fullname = message.text
        bot.send_message(message.chat.id, 'Введите вашу группу')
        bot.register_next_step_handler(message, birthday)


# Заполняем поле подразделение, просим заполнить дату рождения
def birthday(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    user.subunit = message.text
    bot.send_message(message.chat.id, 'Введите вашу дату рождения '
                                      '\nВ формате 00.00.0000')
    bot.register_next_step_handler(message, check_birthday)


# Проверяем день рождения на подходяший формат 
def check_birthday(message):
    if val.numbers(message.text):
        user_id = message.from_user.id
        user = user_dict[user_id]
        user.birthday = message.text
        personal_inform(message)
    else:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные')
        bot.send_message(message.chat.id, 'Введите вашу дату рождения '
                                          '\nВ формате 00.00.0000')
        bot.register_next_step_handler(message, check_birthday)


# Просим ввести персональные данные для каждого типа сотрудника разные
def personal_inform(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    if user.type == 'Сотрудник':
        bot.send_message(message.chat.id, 'Введите последние 4 цифры номера вашего паспорта')
    elif user.type == 'Студент':
        bot.send_message(message.chat.id, 'Введите номер вашего студенческого')
    bot.register_next_step_handler(message, contacts)


# Заполняем перс. информацию, просим ввести контактный номер телефона
def contacts(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    user.pers_inform = message.text
    try:
        message.text = int(message.text)
        bot.send_message(message.chat.id, 'Введите ваш контактный номер телефона')
        bot.register_next_step_handler(message, phone)
    except ValueError:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные')
        personal_inform(message)


# Заполняем контактные данные, проверка номера телефона на валидность
def phone(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    user.contacts = message.text
    if val.only_numbers(message.text):
        bot.send_message(message.chat.id, 'Введите вашу контактную почту')
        bot.register_next_step_handler(message, check)
    else:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные')
        bot.send_message(message.chat.id, 'Введите ваш контактный номер телефона')
        bot.register_next_step_handler(message, phone)


# Предлагаем проверить данные
def check(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    user.contacts += f'\n{message.text}'
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = telebot.types.KeyboardButton('Всё верно')
    bnt2 = telebot.types.KeyboardButton('Начать сначала')
    markup.add(btn1, bnt2)
    bot.send_message(message.chat.id, 'Проверьте ваши данные\nВсё верно?', reply_markup=markup)
    bot.send_message(message.chat.id, getData(user, f'Заявка от {now_dt.strftime("%d-%m-%Y %H:%M")}'),
                     parse_mode="Markdown")
    bot.register_next_step_handler(message, end)


# Отправляем заявку пользователю и в группу
def end(message):
    user_id = message.from_user.id
    user = user_dict[user_id]
    _un = message.from_user.username
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.text == 'Всё верно':
        if _un is not None:
            _un = f'@{_un}'
        else:
            _un = ''
        bot.send_message(message.chat.id, getData(user, f'Ваша заявка от {now_dt.strftime("%d-%m-%Y %H:%M")}'),
                         parse_mode="Markdown", reply_markup=markup)
        bot.send_message(chat_id,
                         getData(user, f'Заявка от пользователя\nСформирована: {now_dt.strftime("%d-%m-%Y в %H:%M")}\n'
                                       f'{_un}'), parse_mode="Markdown")
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = telebot.types.KeyboardButton('Изменить данные')
        bnt2 = telebot.types.KeyboardButton('В главное меню')
        markup.add(btn1, bnt2)
        bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=markup)
        bot.register_next_step_handler(message, wrong_answer)


# Проверяем выбор пользователя и перенаправляем на выбранную функцию
def wrong_answer(message):
    if message.text == "Изменить данные":
        start(message)
    elif message.text == 'В главное меню':
        first_start(message)


# Делаем красивый вывод заявки
def getData(user, title):
    if user.type == 'Сотрудник':
        t = Template('$title \nФИО: *$fullname* \nКем является: *$type* \n'
                     'Подразделение: *$subunit* \nДата рождения: *$birthday* \nПаспортные данные: *$pers_inform*'
                     '\nКонтактные данные: *$contacts*')
        return t.substitute(
            {
                'title': title,
                'fullname': user.fullname,
                'type': user.type,
                'subunit': user.subunit,
                'birthday': user.birthday,
                'pers_inform': user.pers_inform,
                'contacts': user.contacts,

            }
        )
    if user.type == 'Студент':
        t = Template('$title \nФИО: *$fullname* \nКем является: *$type* \n'
                     'Группа: *$subunit* \nДата рождения: *$birthday* \nНомер студенческого: *$pers_inform*'
                     '\nКонтактные данные: *$contacts*')
        return t.substitute(
            {
                'title': title,
                'fullname': user.fullname,
                'type': user.type,
                'subunit': user.subunit,
                'birthday': user.birthday,
                'pers_inform': user.pers_inform,
                'contacts': user.contacts,

            }
        )


# Обработка сообщений
@bot.message_handler(content_types=['text'])
def text(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton('Запустить бота')
    markup.add(btn1)
    bot.send_message(message.chat.id, 'Нажмите на кнопку, что бы начать', reply_markup=markup)
    bot.register_next_step_handler(message, first_start)
