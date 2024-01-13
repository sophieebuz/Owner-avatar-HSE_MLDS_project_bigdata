import telebot
from telebot import types
import sqlite3
import datetime
import pandas as pd
from TOKEN import token, chat_id
from notifiers import get_notifier
import json


# подключаем базу данных
conn = sqlite3.connect('bolshoi_theater.db')
cursor = conn.cursor()
# cursor.execute("DROP TABLE users")
# cursor.execute("DROP TABLE performances")


try:
    query1 = """CREATE TABLE \"users\" (
               \"chat_id\" INTEGER UNIQUE,
               \"fisrt_name\" TEXT NOT NULL,
               \"nickname\" TEXT,
               \"birthday\" DATE NOT NULL,
               PRIMARY KEY (\"chat_id\"))"""
    cursor.execute(query1)

    df = pd.read_csv('data/dftest.csv')
    df.to_sql(name='performances', con=conn)
    conn.commit()

    query2 = """CREATE TABLE \"subscribes\" (
               \"chat_id\" INTEGER NOT NULL,
               \"perf_name\" TEXT,
               \"day_of_week\" TEXT,
               \"day\" TEXT,
               CONSTRAINT name_unique UNIQUE (\"chat_id\", \"perf_name\"),
               CONSTRAINT day_unique UNIQUE (\"chat_id\", \"day_of_week\"))"""
    cursor.execute(query2)


    # query2 = """CREATE TABLE \"performances\" (
    #            \"date\" TEXT NOT NULL,
    #            \"day_of_week\" TEXT NOT NULL,
    #            \"type\" TEXT NOT NULL,
    #            \"name\" TEXT NOT NULL,
    #            \"age\" TEXT NOT NULL,
    #            \"time\" TEXT NOT NULL,
    #            \"scene\" TEXT NOT NULL,
    #            \"tickets\" TEXT NOT NULL,
    #            \"price\" TEXT)"""
    # cursor.execute(query2)

except:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM performances LIMIT 1")
    print(cursor.fetchall())
    # cursor.execute('DELETE FROM users')
    # conn.commit()
    # date = datetime.date(2000, 5, 23)
    # cursor.execute("INSERT INTO users (user_id, fisrt_name, nickname, birthday)\
    #                   VALUES (502830635, \"Sophie\", \"ethee_real\", \"2000-05-23\")")
    # conn.commit()
    # cursor.execute("SELECT * FROM users")
    # print(cursor.fetchall())
    pass


'''
# query3 = """CREATE TABLE \"testtable\" (
#                \"perf_name\" TEXT NOT NULL)"""
# cursor.execute(query3)

# cursor.execute("SELECT * FROM testtable")
# #print(cursor.fetchall())
# 
# for row in cursor.fetchall():
#     print(json.loads(row[0]))


# array1 = ["aaa", "bbb", "ddd"]
# array2 = ["aaa1", "bbb1", "ddd1"]
# jarray1 = json.dumps((array1))
# jarray2 = json.dumps((array2))


# cursor.execute("INSERT INTO testtable (perf_name) VALUES ('" + jarray2 + "')")
# conn.commit()

# cursor.execute("SELECT * FROM testtable")
# print(cursor.fetchall())
'''



bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_start_message(message):
    text1 = f"Приветствую, {message.from_user.first_name}, в телеграм-боте об анонсах Большого театра! \n\n" \
            f"Здесь ты будешь получать уведомления о новых спектаклях, как только они появятся в продаже."
    text2 = "Если хочешь получать уведомления о конкретных спектаклях, надо пройти регистрацию"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton(text="Регистрация", callback_data='registry')
    keyboard.add(itembtn1)
    bot.send_message(message.from_user.id, text=text1)
    bot.send_message(message.from_user.id, text=text2, reply_markup=keyboard)
    # print(message.from_user.first_name, message.from_user.username, message.from_user.last_name)

@bot.callback_query_handler(func=lambda call: call.data == 'registry')
def callback(call):
    text = "Укажите год, месяц и день вашего рождения в формате гггг-мм-дд"
    msg = bot.send_message(call.message.chat.id, text=text)
    bot.register_next_step_handler(msg, callback_user_registry)

def callback_user_registry(call):
    check1 = call.text.split('-')
    now = datetime.date.today().year
    if int(check1[0]) > now or int(check1[1]) > 12 or int(check1[2]) > 31 or \
            (len(check1[0]) != 4) or (len(check1[1]) != 2) or (len(check1[2]) != 2):
        text = "Дата указана неправильно.\nУкажите год, месяц и день вашего рождения в формате гггг-мм-дд"
        msg = bot.send_message(call.chat.id, text=text)
        bot.register_next_step_handler(msg, callback_user_registry)
    else:
        try:
            with sqlite3.connect('bolshoi_theater.db') as con:
                cursor = con.cursor()
                cursor.execute('INSERT INTO users (chat_id, fisrt_name, nickname, birthday)\
                          VALUES (?, ?, ?, ?)', (call.chat.id, call.from_user.first_name, call.from_user.username, call.text))
                con.commit()

                cursor.execute("SELECT * FROM users")
                print(cursor.fetchall())
            bot.send_message(call.chat.id, text="Вы успешно зарегистрированы!")
            bot.send_message(call.chat.id, text="Для того, чтобы подписаться на конкретные спектакли, введите команду /list")
        except:
            bot.send_message(call.chat.id, text="Вы уже зарегистрированы!")
            bot.send_message(call.chat.id, text="Если хотите подписаться на конкретные спектакли, введите команду /list")


def get_plans_string(tasks):
    tasks_str = []
    for val in list(enumerate(tasks)):
        tasks_str.append(str(val[0] + 1) + ') ' + val[1][0] + '\n')
    return ''.join(tasks_str)

@bot.message_handler(commands=['list'])
def show_list_of_performances(message):
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT DISTINCT name FROM performances")
        tasks = get_plans_string(cursor.fetchall())
#        bot.send_message(message.chat.id, text=tasks)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        itembtn1 = types.InlineKeyboardButton(text="Подписаться на спектакль", callback_data='subscribe_perf')
        itembtn2 = types.InlineKeyboardButton(text="Все спектакли на день недели", callback_data='subscribe_day')
        keyboard.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, text=tasks, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'subscribe_perf')
def callback_subscribe(call):
    text = "Укажите номер спектакля, на который вы хотите подписаться"
    msg = bot.send_message(call.message.chat.id, text=text)
    bot.register_next_step_handler(msg, callback_added_subscribe_perf)

@bot.callback_query_handler(func=lambda call: call.data == 'subscribe_day')
def callback_subscribe(call):
    text = "Выберете номер дня недели:\n\n " \
           "1. Понедельник\n " \
           "2. Вторник\n" \
           "3. Среда\n" \
           "4. Четверг\n" \
           "5. Пятница\n" \
           "6. Суббота\n" \
           "7. Воскресенье"

    msg = bot.send_message(call.message.chat.id, text=text)
    bot.register_next_step_handler(msg, callback_added_subscribe_day)


def callback_added_subscribe_perf(call):
    perf = int(call.text)
    with sqlite3.connect('bolshoi_theater.db') as con:
            cursor = con.cursor()
            cursor.execute("SELECT DISTINCT name FROM performances")
            tasks = cursor.fetchall()
            perf_name = list(enumerate(tasks))[perf - 1][1][0]
    try:
        with sqlite3.connect('bolshoi_theater.db') as con:
            cursor = con.cursor()
            cursor.execute('INSERT INTO subscribes (chat_id, perf_name, day_of_week, day)\
                            VALUES (?, ?, ?, ?)', (call.chat.id, perf_name, None, None))
            con.commit()

            text = f'Спектакль "{perf_name}" успешно добавлен в ваши анонсы!\n' \
                   f'Чтобы посмотреть, на какие спектакли вы подписаны, вызовите команду /mylist'
            bot.send_message(call.chat.id, text=text)

            # cursor.execute("SELECT * FROM subscribes")
            # print(cursor.fetchall())
    except:
        text = "Вы уже подписаны на данный спектакль.\nЕсли хотите изменить настройки " \
               "вашей подписки вызовите команду /change_mylist."
        bot.send_message(call.chat.id, text=text)

def callback_added_subscribe_day(call):
    num_day = int(call.text)
    days = {1: "понедельник", 2: "вторник", 3: "среда",
            4: "четверг", 5: "пятница", 6: "суббота", 7: "воскресенье"}
    day = days[num_day]
    try:
        with sqlite3.connect('bolshoi_theater.db') as con:
            cursor = con.cursor()
            cursor.execute('INSERT INTO subscribes (chat_id, perf_name, day_of_week, day)\
                            VALUES (?, ?, ?, ?)', (call.chat.id, None, day, None))
            con.commit()

            text = f'"{day[:1].upper() + day[1:]}" успешно добавлен в ваши анонсы!\n' \
                   f'Чтобы посмотреть, о каких днях недели вы получаете уведомления, вызовите команду /mylist'
            bot.send_message(call.chat.id, text=text)

            # cursor.execute("SELECT * FROM subscribes")
            # print(cursor.fetchall())
    except:
        text = "Вы уже получаете уведомления о всех спектаклях, проходящих в этот день недели.\n" \
               "Если хотите изменить настройки вашей подписки вызовите команду /change_mylist."
        bot.send_message(call.chat.id, text=text)


@bot.message_handler(commands=['mylist'])
def show_person_list(message):
    chat_id = message.chat.id
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        query1 = "SELECT perf_name FROM subscribes WHERE chat_id={} and perf_name IS NOT NULL".format(chat_id)
        cursor.execute(query1)
        tasks1 = get_plans_string(cursor.fetchall())
        query2 = "SELECT day_of_week FROM subscribes WHERE chat_id={} and day_of_week IS NOT NULL".format(chat_id)
        cursor.execute(query2)
        tasks2 = get_plans_string(cursor.fetchall())
    text = "*Спектакли:*\n" + tasks1 + "\n*Дни недели:*\n" + tasks2
    bot.send_message(message.chat.id, text=text, parse_mode="Markdown")

@bot.message_handler(commands=['change_mylist'])
def change_person_list(message):
    text = "Чтобы бы вы хотели изменить в вашей подписке?"
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Отписаться от спектакля')
    itembtn2 = types.KeyboardButton('Отписаться от дня недели')
    keyboard.add(itembtn1, itembtn2)
    msg = bot.send_message(message.chat.id,
                     text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_change_person_list)

def delete_perf(call):
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        query1 = "SELECT perf_name FROM subscribes WHERE chat_id={} and perf_name IS NOT NULL".format(call.chat.id)
        cursor.execute(query1)
        tasks1 = get_plans_string(cursor.fetchall())

    text = "Укажите номер спектакля, который хотите удалить\n\n" + tasks1
    msg = bot.send_message(call.chat.id, text=text)
    bot.register_next_step_handler(msg, delete_perf_)

def delete_perf_(msg):
    perf = int(msg.text)
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT perf_name FROM subscribes WHERE chat_id={} and perf_name IS NOT NULL".format(msg.chat.id))
        tasks = cursor.fetchall()
        perf_name = list(enumerate(tasks))[perf - 1][1][0]

        query = f"DELETE FROM subscribes WHERE chat_id={msg.chat.id} AND perf_name='{perf_name}'"
        cursor.execute(query)
        bot.send_message(msg.chat.id, text=f'Спектакль "{perf_name}" удален из подписки. Больше вы не будете получать о нем уведомлений')

def delete_day_of_week(call):
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        query2 = "SELECT day_of_week FROM subscribes WHERE chat_id={} and day_of_week IS NOT NULL".format(call.chat.id)
        cursor.execute(query2)
        tasks2 = get_plans_string(cursor.fetchall())

    text = "Укажите день недели, который хотите удалить\n\n" + tasks2
    msg = bot.send_message(call.chat.id, text=text)
    bot.register_next_step_handler(msg, delete_day_of_week_)

def delete_day_of_week_(msg):
    num_day = int(msg.text)
    with sqlite3.connect('bolshoi_theater.db') as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT day_of_week FROM subscribes WHERE chat_id={msg.chat.id} and day_of_week IS NOT NULL")
        tasks = cursor.fetchall()
        day = list(enumerate(tasks))[num_day - 1][1][0]

        query = f"DELETE FROM subscribes WHERE chat_id={msg.chat.id} AND day_of_week='{day}'"
        cursor.execute(query)
        bot.send_message(msg.chat.id, text=f'"{day}" удален(-a) из подписки. Больше вы не будете получать уведомления по этому дню')


def callback_change_person_list(call):
    if call.text == "Отписаться от спектакля":
        try:
            delete_perf(call)
        except:
            bot.send_message(call.chat.id, 'Что то пошло не так')

    elif call.text == "Отписаться от дня недели":
        try:
            delete_day_of_week(call)
        except:
            bot.send_message(call.chat.id, 'Что то пошло не так')




# ---------------------------------------------------------
def send_message(text='Это push уведомление'):
    telegram = get_notifier("telegram")
    message_text = text
    telegram.notify(token=token, chat_id=chat_id, message=message_text)


# import time
# print("Ждем 10 сек")
# time.sleep(10)
# send_message()
# ---------------------------------------------------------


@bot.message_handler(commands=['help'])
def show_list_of_performances(message):
    text = "/start - начало работы с ботом, прохождение регистрации \n"\
           "/help - показать все доступные команды \n"\
           "/list - показать все доступные спектакли \n"\
           "/mylist - показать мои подписки на спектакли \n"\
           "/change_mylist - изменить подписку"
    bot.send_message(message.chat.id, text=text)

bot.polling(none_stop=True)
