import csv
import datetime
import logging

import ephem
from settings import API_KEY, PROXY
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


class BotException(Exception):
    pass


def greet_user(bot, update):
    """
    Вызывается при использовании команды /start
    Arguments:
        bot {[type]} -- [description]
        update {[type]} -- [description]
    """
    text = 'Вызов /start'
    logging.info(text)
    update.message.reply_text(text)


def greet_ephem(bot, update):
    """
    Вызывается при использовании команды /planet
    Arguments:
        bot {[type]} -- [description]
        update {[type]} -- [description]
    """
    try:
        text = update.message.text.split()
        text = text[1].capitalize()

        logging.info(text)
        # список планет, которые возможно обработать
        planets = [
            str(name) for _0, _1, name in ephem._libastro.builtin_planets()]

        if str(text) in planets:
            logging.info('Данная планета есть в списке!!!')
            # получим атрибут
            _attr = getattr(ephem, text)
            if _attr is not None:
                answer = ephem.constellation(_attr(
                    datetime.datetime.now().strftime('%Y')))
            ans_text = "В '%s' созвездии сегодня находится планета '%s' " % (
                answer[1], text)
            bot.sendMessage(update.message.chat_id, ans_text)
            logging.info('Отправка ответа в чат!!!')
        else:
            logging.info('Данной планеты нет в списке!!!')
            bot.sendMessage(
                update.message.chat_id, 'Данной планеты нет в списке!!!')

    except (TypeError, ValueError):
        logging.info('Exception in greet_ephem')
        bot.sendMessage(
            update.message.chat_id, 'Произошла ошибка!!!')
    except IndexError:
        logging.info('IndexError in greet_ephem')
        bot.sendMessage(
            update.message.chat_id,
            "Введите планету через пробел (exsamole: /planet Mars)")


def talk_to_me(bot, update):
    """
    Обработчик сообщений от пользователя
    Arguments:
        bot {[type]} -- [description]
        update {[type]} -- [description]
    """
    user_text = "Привет {}! Ты написал {}".format(
        update.message.chat.first_name, update.message.text)
    logging.info("User: %s, Chat id: %s, Message: %s" % (
        update.message.chat.username,
        update.message.chat.id, update.message.text))
    update.message.reply_text(user_text)


def greet_wordcount(bot, update):
    try:
        words = update.message.text.split()
        _cnt = len(words) - 1  # убираем команду

        logging.info("User: %s, Chat id: %s, Message: %s" % (
            update.message.chat.username,
            update.message.chat.id, update.message.text))

        if _cnt < 1:
            raise BotException('Вы отправили пустую команду!')

        update.message.reply_text('Вы написали %d слова' % _cnt)
    except (TypeError, BotException) as ex:
        update.message.reply_text(str(ex))


def next_full_moon(bot, update):
    try:
        words = update.message.text.split()
        date_ = words[1]

        try:
            datetime.datetime.strptime(date_, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Неккоректный формат даты, пример YYYY-MM-DD")

        update.message.reply_text(
            'Ближайшее полнолуние %s' % ephem.next_full_moon(date_))
    except IndexError:
        logging.info('IndexError in next_full_moon')
        bot.sendMessage(
            update.message.chat_id,
            "Введите дату через пробел (example: /next_full_moon %s)" %
            datetime.datetime.now().strftime('%Y-%m-%d'))
    except (ValueError, BotException) as ex:
        update.message.reply_text(str(ex))


# собирем список городов
_cities = []
with open('cities.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    if reader:
        for row in reader:
            if row['Город']:
                _cities.append(row['Город'])
            else:
                _cities.append(row['Регион'])


def cities_game(bot, update):
    try:
        if _cities:
            cities = _cities
            words = update.message.text.split()
            city = words[1].capitalize()
            if city in cities:
                cities.remove(city)

                _b = city[-1]
                if _b == 'ь' or _b == 'ъ' or _b == 'ы':
                    _b = city[-2]

                if _b:
                    _bb = ''
                    for _city in cities:
                        if _b.capitalize() == _city[0]:
                            _bb = _city
                            cities.remove(_bb)
                            break
                    if _bb:
                        _bb_ = _bb[-1]
                        if _bb_ == 'ь' or _bb_ == 'ъ' or _bb_ == 'ы':
                            _bb_ = _bb[-2]
                        update.message.reply_text(str(
                            f'{_bb} вам на букву "{_bb_}"'))
                    else:
                        update.message.reply_text(str(
                            f'В списке на букву "{_bb}" закончились!'))
            else:
                update.message.reply_text(str(
                    'Города в списке нет!'))

    except (IndexError) as ex:
        logging.info('IndexError in cities_game')
        bot.sendMessage(
            update.message.chat_id,
            "Введите Город (example: /cities Москва)")
    except (ValueError, BotException, TypeError) as ex:
        update.message.reply_text('Что то пошло не так!!!')


def calculator(bot, update):
    """
    Очень простой калькулятор в одно действие
    """
    try:

        words = update.message.text.lower().replace(' ', '')
        words = words.replace('/calc', '')

        if words:
            if '+' in words:
                words = words.split('+')
                result = int(words[0]) + int(words[1])
                update.message.reply_text(f'Результат: {result}')
            elif '-' in words:
                words = words.split('-')
                result = int(words[0]) - int(words[1])
                update.message.reply_text(f'Результат: {result}')
            elif '/' in words:
                try:
                    words = words.split('/')
                    result = int(words[0]) / int(words[1])
                    update.message.reply_text(f'Результат: {result}')
                except ZeroDivisionError:
                    update.message.reply_text(f'Делить на ноль нельзя!!!')
            elif '*' in words:
                words = words.split('*')
                result = int(words[0]) * int(words[1])
                update.message.reply_text(f'Результат: {result}')
            else:
                raise BotException('Неверные данные!(example /calc 5+1)')

    except (TypeError, IndexError, ValueError) as ex:
        update.message.reply_text('Неверные данные!(example /calc 5+1)')


def main():
    """
    Основной метод запуска
    """
    mybot = Updater(API_KEY, request_kwargs=PROXY)

    logging.info('Бот запускается!!!')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', greet_ephem))
    dp.add_handler(CommandHandler('wordcount', greet_wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(CommandHandler('cities', cities_game))
    dp.add_handler(CommandHandler('calc', calculator))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
