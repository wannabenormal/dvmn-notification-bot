import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv


def main():
    load_dotenv()
    dvmn_token = os.getenv('DVMN_TOKEN')
    timeout = int(os.getenv('POLLING_TIMEOUT'))
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')

    headers = {
        'Authorization': f'Token {dvmn_token}'
    }

    tg_bot = telegram.Bot(token=tg_bot_token)

    class LogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            tg_bot.send_message(chat_id=tg_chat_id, text=log_entry)

    logger = logging.getLogger('TG_Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsHandler)
    logging.info('Бот запущен')

    bad_requests_attempts = 0

    while True:
        url = 'https://dvmn.org/api/long_polling/'
        params = {}

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                params=params
            )
            response.raise_for_status()
            reviews = response.json()

            if reviews['status'] == 'timeout':
                params['timestamp'] = reviews['timestamp_to_request']
            else:
                for attempt in reviews['new_attempts']:
                    attempt_status = (
                        'К сожалению, в работе обнаружились ошибки'
                        if attempt['is_negative']
                        else 'Преподавателю все понравилось!'
                    )
                    message_template = (
                        'У вас проверили работу "{}"\n'
                        'Ссылка на работу: {}\n'
                        '{}'
                    )

                    message = message_template.format(
                        attempt['lesson_title'],
                        attempt['lesson_url'],
                        attempt_status
                    )
                    tg_bot.send_message(text=message, chat_id=tg_chat_id)
                params['timestamp'] = reviews['last_attempt_timestamp']

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            bad_requests_attempts += 1

            if bad_requests_attempts == 5:
                logger.warning(
                    'Ошибка соеденения. Повторная попытка через 1 мин.'
                )
                time.sleep(60)
                bad_requests_attempts = 0

            continue
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    main()
