import random
import sqlite3
import telebot
from telebot import types
import requests

# API сайта OpenWeatherMap, возвращающий погоду
APPID = "9cf0895e6ec56cb899be23b8577f4206"
URL_BASE = "https://api.openweathermap.org/data/2.5/"


# Функция, для определения погоды в городе, который является аргументов функции
def current_weather(q: str = "Chicago", appid: str = APPID, lang: str = 'ru', units: str = 'metric') -> dict:
    return requests.get(URL_BASE + "weather", params=locals()).json()


# Создается контакт с базой данных и создает, если её нет.
conn = sqlite3.connect('data/sql/guessing_game.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS films_photo_questions(
    id INT,
    answer_options TEXT,
    correct_answer INT,
    photo TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS films_phrase_questions(
    id INT,
    answer_options TEXT,
    correct_answer INT,
    phrase TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS line_from_songs_questions(
    id INT,
    answer_options TEXT,
    correct_answer INT,
    line TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS admins(
    id INT,
    username TEXT
    )""")
conn.commit()

# Токен телеграм бота
bot = telebot.TeleBot('5804294219:AAFIg82Ho6j2tJdiCMeDuR-QvcdPyZb2F-k')

# Создание основной клавиатуры, с выбором режимов
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
film_phrase = types.KeyboardButton('Угадать фильм по фразе')
film_photo = types.KeyboardButton('Угадать фильм по кадру')
line_from_song = types.KeyboardButton('Угадать песню строчке')
weather_key = types.KeyboardButton('Узнать погоду в моем городе')
create_level = types.KeyboardButton('Создать свой вопрос')
markup.add(film_photo, film_phrase, line_from_song, weather_key, create_level)

create_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
create_phrase = types.KeyboardButton('Фильм по фразе')
create_song = types.KeyboardButton('Песня по строчке')
create_markup.add(create_phrase, create_song)

# Списки с количеством правильных и неправильных ответов
wrong_answers_count = []
correct_answers_count = []

# Режим (Используется дальше)
mode = ['0']

# Имя пользователя (Используется дальше)
USERNAME = ['0']


# Запуск бота, который спросит у пользователя имя
@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.send_message(message.chat.id, 'Как Вас зовут?')
    bot.register_next_step_handler(sent, start_next)


# Берет данные из таблицы, открывает клавиатуру с выбором режима и здоровается с пользователем
@bot.message_handler(commands=['next'])
def start_next(message):
    USERNAME.append(message.text)
    if USERNAME[-1] == '/next' or USERNAME[-1] == 'Угадать фильм по фразе' or USERNAME[-1] == 'Угадать фильм по кадру' \
            or USERNAME[-1] == 'Угадать песню строчке' or USERNAME[-1] == 'Узнать погоду в моем городе':
        USERNAME[-1] = 'noname'
    hello_name = f'Привет, <b>{USERNAME[-1]}</b>!\nВыберите режим из предложенных. \n\n' \
                 f'Угадать фильм по фразе (Сложность: сложно) \n' \
                 f'Угадать фильм по кадру (Сложность: нормально) \n' \
                 f'Угадать песню строчке (Сложность: нормально)\n' \
                 f'Узнать погоду в вашем городе (Рекомендуется)\n\n' \
                 f'Создать свой уровень <b>(Только для администраторов!)</b>'
    start_hello = bot.send_message(message.chat.id, f'{hello_name} ', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(start_hello, mode_selection)

# Действия, которые будут совершены после выбора режима пользователем
def mode_selection(message):
    global all_with_photo, all_with_phrase, all_songs, admins

    admins_db = cur.execute("""SELECT * FROM admins""").fetchall()
    admins_db = list(admins_db)
    admins = {}
    for admins_id, admins_nick in admins_db:
        admins[admins_id] = admins_nick

    # Очищает списки ответов, для выбора другого режима
    wrong_answers_count.clear()
    correct_answers_count.clear()

    # Клавиатура для режима "Фильм по кадру"
    if message.text.lower() == 'угадать фильм по кадру':

        all_with_photo = cur.execute("""SELECT * FROM films_photo_questions""").fetchall()
        all_with_photo = list(all_with_photo)

        mode.append('photo')

        # Перемешивание списка вопросов
        random.shuffle(all_with_photo)

        # Создание Inline клавиатуры
        photo_markup = types.InlineKeyboardMarkup(row_width=1)

        add1 = types.InlineKeyboardButton(text=f"{all_with_photo[0][1].split('@')[0]}", callback_data=1)
        add2 = types.InlineKeyboardButton(text=f"{all_with_photo[0][1].split('@')[1]}", callback_data=2)
        add3 = types.InlineKeyboardButton(text=f"{all_with_photo[0][1].split('@')[2]}", callback_data=3)
        add4 = types.InlineKeyboardButton(text=f"{all_with_photo[0][1].split('@')[3]}", callback_data=4)
        back = types.InlineKeyboardButton(text="Вернуться назад", callback_data=5)

        photo_markup.add(add1, add2, add3, add4, back)

        photo_file = open(all_with_photo[0][3], 'rb')

        bot.send_photo(message.chat.id, photo_file, caption='Из какого фильма этот кадр?',
                       reply_markup=photo_markup)

    # Клавиатура для режима "Фильм по фразе"
    elif message.text.lower() == 'угадать фильм по фразе':

        all_with_phrase = cur.execute("""SELECT * FROM films_phrase_questions""").fetchall()
        all_with_phrase = list(all_with_phrase)

        mode.append('phrase')

        # Перемешивание списка вопросов
        random.shuffle(all_with_phrase)

        # Создание Inline клавиатуры
        phrase_markup = types.InlineKeyboardMarkup(row_width=1)

        add1 = types.InlineKeyboardButton(text=f"{all_with_phrase[0][1].split('@')[0]}", callback_data=1)
        add2 = types.InlineKeyboardButton(text=f"{all_with_phrase[0][1].split('@')[1]}", callback_data=2)
        add3 = types.InlineKeyboardButton(text=f"{all_with_phrase[0][1].split('@')[2]}", callback_data=3)
        add4 = types.InlineKeyboardButton(text=f"{all_with_phrase[0][1].split('@')[3]}", callback_data=4)
        back = types.InlineKeyboardButton(text="Вернуться назад", callback_data=5)

        phrase_markup.add(add1, add2, add3, add4, back)

        bot.send_message(message.chat.id, f'Из какого фильма эта фраза?\n\n<b>{all_with_phrase[0][3]}</b>',
                         parse_mode='html',
                         reply_markup=phrase_markup)

    # Клавиатура для режима "Песня по строчке"
    elif message.text.lower() == 'угадать песню строчке':

        all_songs = cur.execute("""SELECT * FROM line_from_songs_questions""").fetchall()
        all_songs = list(all_songs)

        mode.append('song')

        # Перемешивание списка вопросов
        random.shuffle(all_songs)

        # Создание Inline клавиатуры
        songs_markup = types.InlineKeyboardMarkup(row_width=1)

        add1 = types.InlineKeyboardButton(text=f"{all_songs[0][1].split('@')[0]}", callback_data=1)
        add2 = types.InlineKeyboardButton(text=f"{all_songs[0][1].split('@')[1]}", callback_data=2)
        add3 = types.InlineKeyboardButton(text=f"{all_songs[0][1].split('@')[2]}", callback_data=3)
        add4 = types.InlineKeyboardButton(text=f"{all_songs[0][1].split('@')[3]}", callback_data=4)
        back = types.InlineKeyboardButton(text="Вернуться назад", callback_data=5)

        songs_markup.add(add1, add2, add3, add4, back)

        bot.send_message(message.chat.id, f'Из какого фильма эта фраза?\n\n<b>{all_songs[0][3]}</b>',
                         parse_mode='html',
                         reply_markup=songs_markup)

    # Спрашивает пользователя о его месте проживание
    elif message.text.lower() == 'узнать погоду в моем городе':
        sent = bot.send_message(message.chat.id, 'В каком городе вы проживаете?')
        bot.register_next_step_handler(sent, check_the_weather)

    # Создание уровней (только администраторам)
    elif message.text.lower() == 'создать свой уровень':
        if message.from_user.id in admins:
            sent = bot.send_message(message.chat.id, f'<b>Здравствуйте, {admins[message.from_user.id]}.\n</b>'
                                                     f'Выберите, в каком режиме нужно создать уровень',
                                    parse_mode='html', reply_markup=create_markup)
            bot.register_next_step_handler(sent, choose_create_the_level_phrase_or_song)
        else:
            sent = bot.send_message(message.chat.id, '<b>У вас недостаточно прав.</b>', parse_mode='html',
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, mode_selection)


# Обработка выбора режима создания пользователем
def choose_create_the_level_phrase_or_song(message):
    if message.text.lower() == 'фильм по фразе':
        sent = bot.send_message(message.chat.id, 'Введите фразу из фильма:')
        bot.register_next_step_handler(sent, create_the_level_phrase)
    elif message.text.lower() == 'песня по строчке':
        sent = bot.send_message(message.chat.id, 'Введите строчку из песни:')
        bot.register_next_step_handler(sent, create_the_level_song)


# Добавляет фразу, введённую пользователем, в базу данных,
# а затем просит его ввести варианты ответа и записывает их в бд
def create_the_level_phrase(message):
    try:
        global count_id_phrase
        count_id_phrase = list(cur.execute("""SELECT COUNT(id) FROM films_phrase_questions"""))
        for i in count_id_phrase[0]:
            count_id_phrase = i
        count_id_phrase += 1
        cur.execute(f"""INSERT INTO films_phrase_questions (id, phrase) 
                        VALUES ({count_id_phrase}, '{message.text}')""").fetchall()
        conn.commit()
        sent = bot.send_message(message.chat.id, 'Хорошо. Теперь напишите варианты ответов.\nКаждый вариант записывайте '
                                                 'через знак "%"\n'
                                                 'Пример:\nМадагаскар%Форест Гамп%Зеленая миля%Майнкрафт')
        bot.register_next_step_handler(sent, create_the_level_phrase_all_answers)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)


# Показывает пользователю результат записи, а затем спрашивает правильный ответ и записывает его в бд
def create_the_level_phrase_all_answers(message):
    try:
        global count_id_phrase
        answers = message.text.split('%')
        cur.execute(f"""UPDATE films_phrase_questions 
                        SET answer_options = '1.{answers[0]}@2.{answers[1]}@3.{answers[2]}@4.{answers[3]}'
                        WHERE id = {count_id_phrase}""").fetchall()
        conn.commit()
        sent = bot.send_message(message.chat.id,
                                f'Отлично.\n'
                                f'Вот что получилось:\n\n'
                                f'1.{answers[0]}\n'
                                f'2.{answers[1]}\n'
                                f'3.{answers[2]}\n'
                                f'4.{answers[3]}\n\n'
                                f'А теперь введите номер правильного ответа')
        bot.register_next_step_handler(sent, create_the_level_phrase_ans_and_success)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)


# Сообщает пользователю об успешном создание вопроса
def create_the_level_phrase_ans_and_success(message):
    try:
        global count_id_phrase
        cur.execute(f"""UPDATE films_phrase_questions 
                        SET correct_answer = {int(message.text)}
                        WHERE id = {count_id_phrase}""")
        conn.commit()
        sent = bot.send_message(message.chat.id, 'Вопрос создан! Он появился в списке вопросов. А теперь выбирайте режим!',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)


# Добавляет строку, введённую пользователем, в базу данных,
# а затем просит его ввести варианты ответа и записывает их в бд
def create_the_level_song(message):
    try:
        global count_id_songs
        count_id_songs = list(cur.execute("""SELECT COUNT(id) FROM line_from_songs_questions"""))
        for i in count_id_songs[0]:
            count_id_songs = i
        count_id_songs += 1
        cur.execute(f"""INSERT INTO line_from_songs_questions (id, line) 
                            VALUES ({count_id_songs}, '{message.text}')""").fetchall()
        conn.commit()
        sent = bot.send_message(message.chat.id, 'Хорошо. Теперь напишите варианты ответов.\nКаждый вариант записывайте '
                                                 'через знак "%"\n'
                                                 'Пример:\nТёплый ужин%Голая%Когда-нибудь%Девочка-деньги')
        bot.register_next_step_handler(sent, create_the_level_songs_all_answers)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)


# Показывает пользователю результат записи, а затем спрашивает правильный ответ и записывает его в бд
def create_the_level_songs_all_answers(message):
    try:
        global count_id_songs
        answers = message.text.split('%')
        cur.execute(f"""UPDATE line_from_songs_questions 
                            SET answer_options = '1.{answers[0]}@2.{answers[1]}@3.{answers[2]}@4.{answers[3]}'
                            WHERE id = {count_id_songs}""").fetchall()
        conn.commit()
        sent = bot.send_message(message.chat.id,
                                f'Отлично.\n'
                                f'Вот что получилось:\n\n'
                                f'1.{answers[0]}\n'
                                f'2.{answers[1]}\n'
                                f'3.{answers[2]}\n'
                                f'4.{answers[3]}\n\n'
                                f'А теперь введите номер правильного ответа')
        bot.register_next_step_handler(sent, create_the_level_songs_ans_and_success)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)


# Сообщает пользователю об успешном создание вопроса
def create_the_level_songs_ans_and_success(message):
    try:
        global count_id_songs
        cur.execute(f"""UPDATE line_from_songs_questions 
                            SET correct_answer = {int(message.text)}
                            WHERE id = {count_id_songs}""")
        conn.commit()
        sent = bot.send_message(message.chat.id, 'Вопрос создан! Он появился в списке вопросов. А теперь выбирайте режим!',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)
    except Exception:
        sent = bot.send_message(message.chat.id, 'Что-то пошло не так. Выберите режим еще раз', reply_markup=markup)
        bot.register_next_step_handler(sent, mode_selection)
