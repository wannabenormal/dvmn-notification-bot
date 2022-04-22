import os

import requests
import telegram
from dotenv import load_dotenv


def main():
    load_dotenv()
    dvmn_token = os.getenv('DVMN_TOKEN')
    timeout = int(os.getenv('POLLING_TIMEOUT'))
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    headers = {
        'Authorization': f'Token {dvmn_token}'
    }

    bot = telegram.Bot(token=bot_token)

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
            response_body = response.json()

            if response_body['status'] == 'timeout':
                params['timestamp'] = response_body['timestamp_to_request']
            else:
                for attempt in response_body['new_attempts']:
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
                bot.send_message(text=message, chat_id=chat_id)
                params['timestamp'] = response_body['last_attempt_timestamp']

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue


if __name__ == '__main__':
    main()
