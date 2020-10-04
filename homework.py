import os
import time
import requests
import telegram
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']

    try:
        status = homework['status']
        if status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            if status == 'approved':
                verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
            logger.error(parse_homework_status)
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

    except Exception as e:
        logger.error(parse_homework_status)


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    data = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(URL, headers=headers, params=data)
    if homework_statuses.status_code != 200:
        logger.error(homework_statuses)
        return
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            if new_homework.get('current_date') is not None:
                current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(600)  # опрашивать раз в десять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    send_message('Start Bot')
    main()
