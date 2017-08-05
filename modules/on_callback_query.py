""" -*- coding: utf-8 -*- """

import sqlite3
import telepot
from telepot import Bot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from jira import JIRA
from modules.JiraUser import JiraUser
from settings import TOKEN

BOT = Bot(TOKEN)

def on_callback_query(msg):
    """ This function return result for the callback query (inline buttons in chats) """
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    del query_id

    #parse query
    state = query_data[0]
    issue_key = query_data[1:]

    #create DB connection and USER object
    connect = sqlite3.connect('JSBOT.db')
    current_user = JiraUser(chat_id=from_id, connect=connect, JIRA=JIRA)

    #parse issue info from JIRA according to query
    issue_object = current_user.get_issue_object(issue_key)
    issue = current_user.parse_issue(issue_object)

    #if state is 1 – this mean that before the state was short (summary)
    if state == '1':

        #make inline buttons with another state
        markup_link = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Show less', callback_data='0'+issue_key)]
            ])

        #make answer string. It is the original string with change summery to description
        #check special logic if HFLabs
        server = current_user.get_server()
        if server == 'https://jira.hflabs.ru/':
            answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n*Закрывает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                issue['author'], issue['author_link'], issue['worker'], issue['worker_link'],\
                issue['closer'], issue['closer_link'], issue['desc'])
        else:
            answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                issue['author'], issue['author_link'], issue['worker'], issue['worker_link'],\
                issue['desc'])

    #if state is 0 – this mean that before the state was long (description)
    elif state == '0':

        #make inline buttons with another state
        markup_link = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Add worklog', url=issue['worklog_link']),
             InlineKeyboardButton(text='More info', callback_data='1'+issue_key)],
            ])

        #make answer string. It is the original string with change summery to description
        #check special logic if HFLabs
        server = current_user.get_server()
        if server == 'https://jira.hflabs.ru/':
            answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n*Закрывает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                issue['author'], issue['author_link'], issue['worker'], issue['worker_link'],\
                issue['closer'], issue['closer_link'], issue['summary'])
        else:
            answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                issue['author'], issue['author_link'], issue['worker'], issue['worker_link'],\
                issue['summary'])

    #get the message to edit using inline message id and than EDIT message
    message_to_edit = msg['inline_message_id']
    BOT.editMessageText(message_to_edit, text=answer_text, reply_markup=markup_link,\
                        parse_mode='Markdown', disable_web_page_preview=True)
