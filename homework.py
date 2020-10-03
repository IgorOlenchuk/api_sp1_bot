import os
import time
import requests
import telegram

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):

    while True:
        try:
            homework_name = homework['homework_name']
            status = homework['status']
            if status == 'rejected':
                verdict = 'К сожалению в работе нашлись ошибки.'
            else:
                verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

        except Exception as e:
            print(f'Сервер данных не доступен: {e}')
            time.sleep(5)
            continue


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    data = {
        'from_date': current_timestamp
    }

    while True:
        try:
            homework_statuses = requests.get(URL, headers=headers, params=data)
            print(homework_statuses.status_code)
            return homework_statuses.json()

        except Exception as e:
            print(f'Сервер данных не доступен: {e}')
            time.sleep(5)
            continue


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
            time.sleep(300)  # опрашивать раз в десять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    send_message('Бот запустился')
    main()
