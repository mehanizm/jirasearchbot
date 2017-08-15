""" -*- coding: utf-8 -*- """

PROD = False

if PROD:
    TOKEN = '416537278:AAE4yPPd_P3XbXBCsHC9UanRy_8IdkPcmqg'
else:
    TOKEN = '422033407:AAG1zhLbyhh8vuQ5POjwQWoQc4q4BS4A7lI'

TEXTS = {
    'hello': '''Hi, I\'m Jira Bot!👻 Lets start with command /login.''',
    'link': '''1️⃣ First, send me your company JIRA link.\n\n
Something like https://jira.mycompany.com/''',
    'login': '''✅ Link is OK.\n\n2️⃣ Now send me your JIRA login:''',
    'password': '''✅ OK.\n\n3️⃣ Now send me your JIRA password:''',
    'login_error': '''🚫 Something is wrong.\n\nPlease try one more time /login.''',
    'end_ok': '''✅ Your login is OK.\n\nNow try to search inline!''',
    'not_work': '''🚫 Your registration does not work. Try one more time.\n\n1️⃣ First, send me your company JIRA link.\n
Something like https://jira.mycompany.com/\n\n''',
    'ok_inline': '''✅ Your login is OK. \nTry to search inline!''',
    'cant_logout': '''❓ Sorry, you have not succesfully registered yet. I cannot logout you.''',
    'logout_success': '''👋 Your logout was success. Buy!''',
    'check_login': '''⏳ I'm checking your connection. Please, wait.'''
}
