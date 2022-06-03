import logging


class TgLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id, level=logging.NOTSET):
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)
