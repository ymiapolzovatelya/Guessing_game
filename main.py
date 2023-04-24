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
