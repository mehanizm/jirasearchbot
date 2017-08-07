# -*- coding: utf-8 -*-
# class to work with users

class JiraUser:

    def __init__(self, chat_id, connect, JIRA):
        self.chat_id = chat_id
        self.connect = connect
        self.cursor = connect.cursor()
        self.JIRA = JIRA

#CHECKING AND ERASE FROM DB

    def is_exist(self):
        c = self.cursor
        c.execute('SELECT FROM_ID FROM users')
        users = c.fetchall()
        if (self.chat_id,) in users:
            return True
        else:
            return False

    def login_is_ok(self):
        if self.is_exist() and self.get_status() == 1:
            return True
        else:
            return False

    def erase_from_db(self):
        c = self.cursor
        if self.is_exist():
            c.execute('''UPDATE users SET LINK = NULL, LOGIN = NULL, PASSWORD = NULL,
                        STATUS = 0, USERNAME = NULL, JIRANAME = NULL WHERE FROM_ID = ?''', (self.chat_id,))
            self.connect.commit()
            return True
        else:
            return False

#UPDATE DB

    def add_to_db(self, username=None):
        c = self.cursor
        if not self.is_exist():
            c.execute('INSERT INTO users (FROM_ID, USERNAME) VALUES (?,?)',\
                                                     (self.chat_id, username))
            self.connect.commit()
            return self.chat_id
        else:
            return False

    def update_status(self, status):
        c = self.cursor
        if self.is_exist():
            c.execute('UPDATE users SET STATUS = ? WHERE FROM_ID = ?', (status, self.chat_id))
            self.connect.commit()
            return status
        else:
            return False

    def update_server(self, link, username):
        c = self.cursor
        if link[-1] != '/':
            link += '/'
        if link[0] != 'h':
            link = 'https://' + link
        link = link.replace('http:', 'https:')
        if self.is_exist():
            c.execute('UPDATE users SET LINK = ?, USERNAME = ? WHERE FROM_ID = ?',\
                (link, username, self.chat_id))
            self.connect.commit()
            return True
        else:
            return False

    def update_login(self, login):
        c = self.cursor
        if self.is_exist():
            c.execute('UPDATE users SET LOGIN = ? WHERE FROM_ID = ?', (login, self.chat_id))
            self.connect.commit()
            return True
        else:
            return False

    def update_password(self, password):
        c = self.cursor
        if self.is_exist():
            c.execute('UPDATE users SET PASSWORD = ? WHERE FROM_ID = ?', (password, self.chat_id))
            self.connect.commit()
            return True
        else:
            return False

    def update_jira_name(self):
        c = self.cursor
        if self.is_exist():
            jira = self.JIRA(server = self.get_server(), basic_auth = self.get_auth())
            jiraname = jira.current_user()
            c.execute('UPDATE users SET JIRANAME = ? WHERE FROM_ID = ?', (jiraname, self.chat_id))
            self.connect.commit()
            return True
        else:
            return False

#GETTING FROM DB

    def get_from_db(self):
        c = self.cursor
        if self.is_exist():
            c.execute('SELECT * FROM users WHERE FROM_ID = ?', (self.chat_id,))
            user = c.fetchall()
            return user[0]
        else:
            return False

    def get_server(self):
        if self.is_exist():
            return self.get_from_db()[2]
        else:
            return False

    def get_auth(self):
        if self.is_exist():
            return (self.get_from_db()[3], self.get_from_db()[4])
        else:
            return False

    def get_status(self):
        if self.is_exist():
            return self.get_from_db()[5]
        else:
            return False

    def get_username(self, JiraName=None):
        c = self.cursor
        if JiraName:
            c.execute('SELECT USERNAME FROM users WHERE JIRANAME = ?', (JiraName,))
            username = c.fetchall()
            if username:
                return username[0][0]
            else:
                return False
        else:
            username = self.get_from_db()[6]
            if username:
                return username
            else:
                return False

    def get_jira_name(self):
        if self.is_exist():
            return self.get_from_db()[7]
        else:
            return False

#GETTING AND SENDING TO JIRA

    def get_issue_object(self, issue_key):
        if self.login_is_ok():
            SERVER = self.get_server()
            jira = self.JIRA(server=SERVER, basic_auth=self.get_auth())
            issue_object = jira.issue(issue_key)
            return issue_object
        else:
            return False

    def parse_issue(self, issue):
        if self.login_is_ok():
            SERVER = self.get_server()
            BASIC_AUTH = self.get_auth()

            current_issue = issue
            issue_key = current_issue.key

            summary = str(current_issue.fields.summary)
            desc = str(current_issue.fields.description)

            chars = '_*`[]'
            for c in chars:
                summary = summary.replace(c, ' ')
                desc = desc.replace(c, ' ')

            summary = summary.replace('{noformat}', '```')
            desc = desc.replace('{noformat}', '```')

            statuses_emoji_dictionary = {
                                            '1': '📌', #open
                                            '3': '🔧', #in-progress
                                            '4': '💣', #reopen
                                            '5': '✅', #resolved
                                            '6': '❌'  #closed
                                        }

            if current_issue.fields.status.id in statuses_emoji_dictionary.keys():
                status_logo = statuses_emoji_dictionary[current_issue.fields.status.id]
            else: 
                status_logo = '⁉️'

            author_username = self.get_username(JiraName = current_issue.fields.creator.name)
            worker_username = self.get_username(JiraName = current_issue.fields.assignee.name)
            if author_username:
                author_link = 't.me/{}'.format(author_username)
            else:
                author_link = None
            if worker_username:
                worker_link = 't.me/{}'.format(worker_username)
            else:
                worker_link = None

            issue = {
                        'id': current_issue.id,
                        'key': issue_key,
                        'author': str(current_issue.fields.creator),
                        'author_link': author_link,
                        'worker': str(current_issue.fields.assignee),
                        'worker_link': worker_link,
                        'status_logo': status_logo,
                        'status': str(current_issue.fields.status),
                        'summary': summary,
                        'desc': desc,
                        'link': '{}browse/{}'.format(SERVER, issue_key),
                        'worklog_link': '{}secure/CreateWorklog!default.jspa?id={}'.format(SERVER, current_issue.id),
                        'thumb_url': '{}/secure/projectavatar?pid={}&os_username={}&os_password={}'\
                                            .format(SERVER, current_issue.fields.project.id, BASIC_AUTH[0], BASIC_AUTH[1])
                    }
            
            return issue
        else:
            return False

    def search_issues(self, search_string, max_results=10):
        if self.login_is_ok():
            SERVER = self.get_server()
            jira = self.JIRA(server = SERVER, basic_auth = self.get_auth())
            get_issues = jira.search_issues(search_string, maxResults=max_results)
            return get_issues
        else:
            return False

    def add_comment(self, issue_key, comment):
        if self.login_is_ok():
            jira = self.JIRA(server = self.get_server(), basic_auth = self.get_auth())
            jira.add_comment(issue_key, comment)
            return True
        else:
            return False