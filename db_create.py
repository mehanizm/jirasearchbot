import sqlite3

conn = sqlite3.connect('JSBOT.db')
c = conn.cursor()
c.execute('''CREATE TABLE users
             (ID INTEGER PRIMARY KEY, 
             FROM_ID INTEGER, 
             LINK TEXT, 
             LOGIN TEXT,
             PASSWORD TEXT,
             STATUS INTEGER,
             USERNAME TEXT,
             JIRAUSER TEXT)''')

conn.commit()
conn.close()