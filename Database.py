import requests
import re
import sqlite3
import sys
import subprocess
from collections import namedtuple

# Custom modules
from Igerslike import Igerslike


class Database(object):

    def __init__(self):

        try:
            self.conn = sqlite3.connect('Database/Magic.db')
            self.c = self.conn.cursor()
            self.c.execute("SELECT SQLITE_VERSION()")
            data = self.c.fetchone()

            print('Successfully connected to database.\nSQLite version %s' % data)

        except sqlite3.Error as error:
            print('Error connecting to database:\n%s' % error)
            sys.exit(1)


    def create_overview(self, overviews):

        for data in overviews:

            self.c.execute(
                "INSERT OR IGNORE INTO account_overview (id, username, status, category, blog)"
                "VALUES (?, ?, ?, ?, ?)", (data.id, data.username, data.status, data.category, data.blog))


    def update_overview(self, overviews):

        for data in overviews:

            self.c.execute(
                "UPDATE account_overview "
                "SET username = ?, status = ?, category = ? "
                "WHERE ID = ?", (data.username, data.status, data.category, data.id))


    def update_ban_manager(self):

        self.c.execute("INSERT OR IGNORE INTO ban_manager (ID, Username) "
                       "SELECT ID, username "
                       "FROM account_overview;")


    def update_phone_verifier(self):

        self.c.execute("INSERT OR IGNORE INTO phone_verifier (ID) "
                       "SELECT ID "
                       "FROM account_overview;")


    def delete_items(self, items):

        a = [int(item[0]) for item in items]
        b = [x[0] for x in self.c.execute("SELECT ID from account_overview").fetchall()]

        for uid in b:
            if uid not in a:
                self.c.execute("DELETE from account_overview "
                               "WHERE ID=?", (uid,))

                self.c.execute("DELETE from ban_manager "
                               "WHERE ID=?", (uid,))

                self.c.execute("DELETE from phone_verifier "
                               "WHERE ID=?", (uid,))


    def data_save(self):

        self.conn.commit()