""" -*- coding: utf-8 -*- """

import time
from telepot import Bot
from telepot.loop import MessageLoop
from settings import TOKEN
from modules.on_callback_query import on_callback_query
from modules.on_chat_message import on_chat_message
from modules.on_inline_query import on_inline_query

BOT = Bot(TOKEN)

MessageLoop(BOT, {'chat': on_chat_message,
                  'inline_query': on_inline_query,
                  'callback_query': on_callback_query,}).run_as_thread()

while 1:
    time.sleep(10)
