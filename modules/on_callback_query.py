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

    #parse query
    state = query_data[0]
    issue_key = query_data[1:]

    #create DB connection and USER object
    connect = sqlite3.connect('JSBOT.db')
    current_user = JiraUser(chat_id=from_id, connect=connect, JIRA=JIRA)

    if not current_user.login_is_ok():
        BOT.answerCallbackQuery(query_id, text='You need registration to do this')
        return

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
        answer_text = current_user.collect_issue(issue, desc = 'desc')

    #if state is 0 – this mean that before the state was long (description)
    elif state == '0':

        #make inline buttons with another state
        markup_link = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Add worklog', url=issue['worklog_link']),
             InlineKeyboardButton(text='More info', callback_data='1'+issue_key)],
            ])

        #make answer string. It is the original string with change summery to description
        answer_text = current_user.collect_issue(issue)

    #get the message to edit using inline message id and than EDIT message
    message_to_edit = msg['inline_message_id']
    BOT.editMessageText(message_to_edit, text=answer_text, reply_markup=markup_link,\
                        parse_mode='Markdown', disable_web_page_preview=True)
