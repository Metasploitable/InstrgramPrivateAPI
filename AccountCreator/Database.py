import sqlite3
import sys
import random
import string

class Database(object):

    def __init__(self):

        self.domains = [ "hotmail.com", "gmail.com", "mail.com", "yahoo.com"]

        try:
            self.conn = sqlite3.connect('../Database/Magic.db')
            self.c = self.conn.cursor()
            self.c.execute("SELECT SQLITE_VERSION()")
            data = self.c.fetchone()

            print ('\n[!] Successfully connected to database.\n[!] SQLite version %s' % data + '\n')

        except sqlite3.Error as e:
            print('[-] Error connecting to Database: \n%s' % e)
            sys.exit(1)

    def calculate_accounts(self):

        route = []
        self.c.execute("SELECT username FROM account_overview")
        for row in self.c.fetchall():
            route.append(row)

        return 152 - len(route)


    def get_values(self, size=3):

        username = self.c.execute("SELECT username from AccountCreationData ORDER BY RANDOM() LIMIT 1").fetchone()[0] \
            + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))

        password = self.c.execute("SELECT password FROM AccountCreationData ORDER BY RANDOM() LIMIT 1").fetchone()[0]

        email = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)]) + '@' + \
            random.choice(self.domains)

        return username, password, email
