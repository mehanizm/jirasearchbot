""" -*- coding: utf-8 -*- """

import sqlite3
import telepot
from telepot import Bot
from jira import JIRA
from modules.JiraUser import JiraUser
from settings import TOKEN, TEXTS

BOT = Bot(TOKEN)

def on_chat_message(msg):
    """ registration and work with text messages """
    #parse message to get usefull info
    content_type, chat_type, chat_id = telepot.glance(msg)
    del content_type, chat_type
    username = None
    if 'username' in msg['chat'].keys():
        username = msg['chat']['username']

    #connect to DB
    connect = sqlite3.connect('JSBOT.db')

    #if message is not a text – return
    if 'text' in msg.keys():
        command = msg['text']
    else:
        return

    #if it is a reply do some special logic – send comment to JIRA if we know user
    if 'reply_to_message' in msg.keys() and 'entities' in msg['reply_to_message'].keys():
        user_id = msg['from']['id']
        comment_text = msg['text']
        issue_key = msg['reply_to_message']['entities'][0]['url'].split('/')[-1]
        comment_user = JiraUser(chat_id=user_id, connect=connect, JIRA=JIRA)
        comment_user.add_comment(issue_key, comment_text)
        return

    #create current user object
    current_user = JiraUser(chat_id=chat_id, connect=connect, JIRA=JIRA)

    #LOGOUT logic
    if command == '/logout':

        if current_user.is_exist():

            current_user.erase_from_db()
            BOT.sendMessage(chat_id, TEXTS['logout_success'])
            return

        else:

            BOT.sendMessage(chat_id, TEXTS['cant_logout'])
            return

    #START logic
    if command.split(' ')[0] == '/start':
        
        BOT.sendMessage(chat_id, TEXTS['hello'])
        BOT.sendMessage('41591017', 'New user! {}'.format(msg['chat']))

    #LOGIN logic
    if command == '/login':

        if not current_user.is_exist():

            BOT.sendMessage(chat_id, TEXTS['link'])
            current_user.add_to_db(username)
            current_user.update_status(2)

        else:

            if current_user.get_status() == 1:
                BOT.sendMessage(chat_id, TEXTS['ok_inline'])

            else:
                current_user.erase_from_db()
                BOT.sendMessage(chat_id, TEXTS['not_work'])
                current_user.update_status(2)

    #logic to parse login and password from user. State == 2
    else:

        if current_user.get_status() == 2:

            #save server link and ask for login
            if not current_user.get_server():

                current_user.update_server(command, username)
                BOT.sendMessage(chat_id, TEXTS['login'])

            #save login and ask for password
            elif not current_user.get_auth()[0]:

                current_user.update_login(command)
                BOT.sendMessage(chat_id, TEXTS['password'])

            #save password and check connection
            elif not current_user.get_auth()[1]:

                current_user.update_password(command)
                server = current_user.get_server()
                basic_auth = current_user.get_auth()

                try:
                    BOT.sendMessage(chat_id, TEXTS['check_login'])
                    JIRA(server=server, basic_auth=basic_auth)
                except:
                    current_user.update_status(0)
                    BOT.sendMessage(chat_id, TEXTS['login_error'])
                else:
                    current_user.update_status(1)
                    current_user.update_jira_name()
                    BOT.sendMessage(chat_id, TEXTS['end_ok'])

    #clean memory
    del current_user
    connect.close()
