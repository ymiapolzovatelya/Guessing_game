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
