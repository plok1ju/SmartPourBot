import telebot
import webbrowser
import time
import sqlite3
import config

from telebot.types import WebAppInfo
from telebot import types

bot = telebot.TeleBot(config.BOT_TOKEN)

array_drinks = ['вода', 'энергетик', 'сок яблочный', 'сок апельсиновый']

volume = ""
volume_to_data = 0
drink = ''


@bot.message_handler(commands=[config.print_data])
def show_data(message):
    conn = sqlite3.connect(config.NAME_DATABASE)
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM drinks')
        data = cur.fetchall()
        info = 'Напиток Объем Почта\n'
        for element in data:
            info += f'{element[1]} {element[2]} {element[3]}\n'
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, info)

    except Exception:
        bot.send_message(message.chat.id, 'Нет данных')


@bot.message_handler(commands=[config.delete_data])
def delite_data(message):
    conn = sqlite3.connect(config.NAME_DATABASE)
    cur = conn.cursor()
    cur.execute('DELETE FROM drinks')
    conn.commit()
    cur.close()
    conn.close()


@bot.message_handler(commands=['site'])
def site(message):
    webbrowser.open('https://vk.com')


@bot.message_handler(commands=['collab'])
def collab(message):
    bot.send_message(message.chat.id, "Здесь вы можете оставить свои контакты и сопроводительное письмо для "
                                      "сотрудничества!")
    bot.register_next_step_handler(message, get_collab)


@bot.message_handler(commands=['review'], content_types=['text', 'photo', 'audio'])
def review(message):
    bot.send_message(message.chat.id, "Отправьте свой отзыв в чат)")
    bot.register_next_step_handler(message, get_review)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Help information")


@bot.message_handler(content_types=['text'])
def buy(message):
    if message.text == '/start':
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        key_water = types.KeyboardButton(text='Вода')
        keyboard.add(key_water)
        key_energo = types.KeyboardButton(text='Энергетик')
        keyboard.add(key_energo)
        key_orange_juice = types.KeyboardButton(text='Сок апельсиновый')
        keyboard.add(key_orange_juice)  # добавляем кнопку в клавиатуру
        key_apple_juice = types.KeyboardButton(text='Сок яблочный')
        keyboard.add(key_apple_juice)
        question = 'Здравствуйте! Выберите напиток:'
        bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
        bot.register_next_step_handler(message, check_click_drinks)
    else:
        bot.send_message(message.from_user.id, 'Напишите /start для нового заказа\n           /review чтобы оставить '
                                               'отзыв')


def check_click_drinks(message):
    global drink
    if message.text.lower() in array_drinks:
        drink = message.text
        bot.send_message(message.from_user.id, 'Введите объем напитка, можно приобрести от 50 до 5000 миллилитров');
        bot.register_next_step_handler(message, get_volume)
    else:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        key_water = types.KeyboardButton(text='Вода')
        keyboard.add(key_water)
        key_energo = types.KeyboardButton(text='Энергетик')
        keyboard.add(key_energo)
        key_orange_juice = types.KeyboardButton(text='Сок апельсиновый')
        keyboard.add(key_orange_juice)
        key_apple_juice = types.KeyboardButton(text='Сок яблочный')
        keyboard.add(key_apple_juice)
        question = 'Выберите напитки из предложенных'
        bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
        bot.register_next_step_handler(message, check_click_drinks)


def get_volume(message):
    global volume
    global volume_to_data
    while volume == "":
        try:
            volume = int(message.text)
            if volume < 50 or volume > 5000:
                raise Exception()
            keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            key_yes = types.KeyboardButton(text='Да')
            keyboard1.add(key_yes)
            key_no = types.KeyboardButton(text='Нет')
            keyboard1.add(key_no)
            question = 'Подтвердите ваш заказ\nВаш напиток: ' + drink.lower() + ' объемом ' + str(volume)
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard1)
            bot.register_next_step_handler(message, check_click_state)
        except Exception:
            bot.send_message(message.from_user.id, 'Введите цифрами от 50 до 5000, например "200"')
            bot.register_next_step_handler(message, get_volume)
            break

    volume_to_data = volume
    volume = ""


def check_click_state(message):
    if message.text.lower() == 'да':
        keyboard2 = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        key_pay = types.KeyboardButton('Перейдите на окошко оплаты',
                                       web_app=WebAppInfo(url='https://www.youtube.com/watch?v=-452p_9ESbM'))
        keyboard2.add(key_pay)
        bot.send_message(message.from_user.id, 'Отлично!', reply_markup=keyboard2)
        time.sleep(5)
        bot.send_message(message.chat.id, 'Простите, на самом деле, нашего сервиса еще не существует.\n'
                                          'Вы помогли собрать данные о предпочтении будущих '
                                          'покупателей\nВ благодарность мы предлагаем вам скидку в 25% на '
                                          'первые 5 заказов\nВведите свою почту ниже, для получения '
                                          'скидки\nМы будем очень вас ждать!')
        bot.register_next_step_handler(message, get_data)

    elif message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, 'Пожалуйста, попробуйте заказать снова, напишите /start для заказа')
        bot.register_next_step_handler(message, buy)
    else:
        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        key_yes = types.KeyboardButton(text='Да')
        keyboard1.add(key_yes)
        key_no = types.KeyboardButton(text='Нет')
        keyboard1.add(key_no)
        question = 'Подтвердите ваш заказ используя кнопки'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard1)
        bot.register_next_step_handler(message, check_click_state)


def get_data(message):
    email = message.text
    conn = sqlite3.connect(config.NAME_DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS drinks (id int auto_increment primary key, drink varchar(50), volume int, '
                'email varchar(50) )')
    cur.execute("INSERT INTO drinks (drink, volume, email) VALUES ('%s', '%s', '%s')" % (drink, volume_to_data, email))
    conn.commit()
    cur.close()
    conn.close()
    buy(message)


def get_review(message):
    answer = message.text
    conn = sqlite3.connect(config.REVIEW_DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS reviews (id int auto_increment primary key, review varchar(500))')
    cur.execute("INSERT INTO reviews (review) VALUES ('%s')" % answer)
    conn.commit()
    cur.close()
    conn.close()
    buy(message)


def get_collab(message):
    answer = message.text
    conn = sqlite3.connect(config.COLLAB_DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS collabs (id int auto_increment primary key, text varchar(500)')
    cur.execute("INSERT INTO collabs (text) VALUES ('%s')" % answer)
    conn.commit()
    cur.close()
    conn.close()
    buy(message)


bot.polling(none_stop=True)

# @bot.message_handler(commands=['start'])
# def main(message):
#     bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
