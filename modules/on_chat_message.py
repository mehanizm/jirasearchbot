""" -*- coding: utf-8 -*- """

import sqlite3
import telepot
from telepot import Bot
from telepot.helper import Answerer
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent,\
                                    InlineKeyboardMarkup, InlineKeyboardButton
from jira import JIRA
from modules.JiraUser import JiraUser
from settings import TOKEN

BOT = Bot(TOKEN)
ANSWERER = Answerer(BOT)

def on_inline_query(msg):
    """ return results to inline queries """

    def compute():
        """ compute results to inline queries """

        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        del query_id
        cache_time = 0

        connect = sqlite3.connect('JSBOT.db')
        current_user = JiraUser(chat_id=from_id, connect=connect, JIRA=JIRA)

        articles = []

        #if the USER have success registration
        if current_user.login_is_ok():

            #search strings
            search_string = '''(text ~ '{}*') AND (resolution = Unresolved)
                                    order by updated'''.format(query_string)
            if current_user.get_server() == 'https://jira.hflabs.ru/':
                search_string_default = '''assignee = currentUser() AND fixVersion not in
                            (backlog, future) AND resolution = Unresolved order by updated'''
            else:
                search_string_default = '''assignee = currentUser()
                            AND resolution = Unresolved order by updated'''
            serch_string_in_default = '''(text ~ '{}*') AND (assignee = currentUser()
                        and resolution = Unresolved) order by updated'''.format(query_string)
            search_string_all = "(text ~ '{}*') order by updated".format(query_string)
            search_string_issue = "issue = '{}'".format(query_string)

            #searching in JIRA
            if len(query_string) == 0:
                get_issues = current_user.search_issues(search_string_default, 30)
            else:
                try:
                    get_issues = current_user.search_issues(search_string_issue)
                except:
                    get_issues = current_user.search_issues(serch_string_in_default)
                    if len(get_issues) < 3:
                        get_issues = current_user.search_issues(search_string)
                        if len(get_issues) < 3:
                            get_issues = current_user.search_issues(search_string_all)

            #convert issues to telegram inline query format
            for issue_object in get_issues:

                issue = current_user.parse_issue(issue_object)
                issue_key = issue['key']

                #make answer
                server = current_user.get_server()
                if server == 'https://jira.hflabs.ru/':
                    answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n*Закрывает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                        format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                        issue['author'], issue['author_link'], issue['worker'],\
                        issue['worker_link'], issue['closer'], issue['closer_link'],\
                        issue['summary'])
                else:
                    answer_text = '{} [{}: {}]({})\n*Поставил:* [{}]({})\n*Делает:* [{}]({})\n\n📄 *Подробности:*\n{}'.\
                        format(issue['status_logo'], issue['key'], issue['status'], issue['link'],\
                        issue['author'], issue['author_link'], issue['worker'],\
                        issue['worker_link'], issue['summary'])

                #make buttons
                markup_link = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Add worklog', url=issue['worklog_link']),
                     InlineKeyboardButton(text='More info', callback_data='1'+issue_key)],
                    ])

                #make inline Telegram answer
                articles.append(InlineQueryResultArticle(
                    id=issue_key,
                    title="{}. {} {}".format(issue_key, issue['status_logo'], issue['status']),
                    description=issue['summary'],
                    input_message_content=InputTextMessageContent(
                        message_text=answer_text,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    ),
                    reply_markup=markup_link,
                    thumb_url=issue['thumb_url'],
                    thumb_width=48,
                    thumb_height=48
                    ))

        #if the USER have NOT successful registration
        else:
            articles.append(InlineQueryResultArticle(
                id='login',
                title="You did not login to JIRA. Click here to login",
                input_message_content=InputTextMessageContent(
                    message_text="Please use command /login in @jirasearchBOT directly"
                    )
                )
                           )

        #clean memory
        del current_user
        connect.close()
        return articles, cache_time

    ANSWERER.answer(msg, compute)
