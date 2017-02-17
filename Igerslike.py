import requests
import grequests
import re
import sqlite3
from collections import namedtuple

# Custom modules
from Exceptions import MyException

class Igerslike(object):

    def __init__(self):

        self.url = 'https://www.igerslike.com'
        self.endpoint = 'ig/accounts/add/'
        self.query_string = {'action': 'add'}

        self.Session = requests.Session()

        try:
            self.conn = sqlite3.connect('Database/Magic.db')
            self.c = self.conn.cursor()

        except sqlite3.Error as error:
            print('Error connecting to database:\n%s' % error)
            sys.exit(1)


    def login(self, username, password):

        self.Session.post(self.url + '/login/',
            params = {
              'login': '1'
            },
            data = {
              'login_username': username,
              'login_password': password
            },
            cookies = {
              'PHPSESSID': ''
            },verify=False)


    def fetch_overviews(self):

        AccountOverview = namedtuple(
            'AccountOverview',
            ['id', 'username', 'status', 'category', 'blog']
        )

        raw_overviews = self.Session.post(self.url + '/ig/accounts/home/?ajax=1',
            data = {
              'length': '152'
            }).json()['data']

        return [
            AccountOverview(
                id       = raw_overview_data[1],
                username = re.findall(r'@(.*)</a>', raw_overview_data[2])[0],
                status   = re.findall(r'<span class="badge .*">(.*)</span>', raw_overview_data[8])[0],
                category = re.findall(r'<span class="badge .*">(.*)</span>', raw_overview_data[7])[0],
                blog     = re.findall(r'@(.*)</a>', raw_overview_data[2])[0]
            )
            for raw_overview_data in raw_overviews
            ]


    def upload_accounts(self, items):

        if not items:
            sys.exit(1)

        payload = {
            'userid': (None, '8650'),
            'submit': (None, 'submit'),
            'accounts': (None, '\n'.join(items)),
            'format': (None, '2'),
            'submit': (None, '')
        }

        return self.Session.post(self.url + self.endpoint,
                                 params=self.query_string, files=payload)


    def delete(self, UID):

        payload = {'customActionType': 'group_action', 'customActionName': 'remove', 'id[]': UID}

        post = self.Session.post(self.url + '/ig/accounts/home/?ajax=1',
            data=payload)

        return post.json()['customActionMessage']


    def edit(self):

        # Select item(s) where group = - none -
        ID = [x[0] for x in self.c.execute("SELECT ID FROM account_overview WHERE status = 'Login Required' AND category = '- none -'").fetchall()]

        if not ID:
            return None

        post = self.Session.post(
            self.url + '/ig/accounts/home/?ajax=1',
            data = {
                'customActionType': 'group_action',
                'customActionName': 'edit',
                'id[]': ID
            }
        )

        if post.status_code == 504:
            print(str(post.status_code) + ' [ERROR] Server timed out, please check Igerslike for updated.')
        elif post.status_code == 200:
            print(post.json()['customActionMessage'])

        g = self.Session.get(self.url + '/ig/accounts/edit/')

        r = self.Session.post(
            self.url + '/ig/accounts/edit/',
            params = {
                'id[0]': ID
            },
            data = {
                'submit': 'submit',
                'proxy': 'private_less',
                'proxy_select': 'private_less',
                'config_group': '2266',
                'settings_log_warnings': '1',
                'status': '',
                'default_tags': '',
                'default_comments': '',
                'default_userlist': '',
                'default_whitelist': '',
                'default_blacklist': '',
                'default_folder': '',
                'default_location': '',
                'submit': ''
            }
        )

        if r.status_code == 302 or 200:
            print('\nAccount(s) have been updated')


    def login_accounts(self):

        # Select item(s) that just got editted, they need login
        ID = [x[0] for x in self.c.execute("SELECT ID FROM account_overview WHERE status = 'Login Required' AND category = 'Profiling!'").fetchall()]

        if not ID:
            return None

        try:
            r = self.Session.post(
                self.url + '/ig/accounts/home/?ajax=1',
                data = {
                    'customActionType': 'group_action',
                    'customActionName': 'login_normal',
                    'id[]': ID
                }
            )

            print(r.json()['customActionMessage'])

        except Exception as e:
            print(e)

        # Another useless requests, reasons unknown, expect 302 stastus code!
        self.Session.post(self.url + '/ig/accounts/login/?action=1', data={'submit': 'submit', 'submit': ''})


    def account_creation(self):

        print('Starting account creation module...')
        if len(self.c.execute("SELECT count(*)").fetchall()) < 132:
            subprocess.run('python35 AccountCreation.py', shell=True)


    def post_id(self):

        endpoint = '/ig/tasks/start/'

        ID = [str(x[0]) for x in self.c.execute("SELECT ID FROM account_overview WHERE category = 'DirectLinking'").fetchall()]
        print(ID)

        self.Session.post(self.url + endpoint,
            params = {
              'x_requested_with': '1',
              'id': ', '.join(ID),
              'start': 'true'
            })


    def follow_task(self):

        endpoint = '/ig/tasks/start/'

        payload = {
            'task_type': '8',
            'pause_time': '25',
            'actions_amount': '1',
            'pause_from': '18',
            'pause_to': '34',
            'require_tags': 'default',
            'require_userlist': '11079',
            'require_location': 'default',
            'require_comments': 'default',
            'require_biography': '0',
            'require_links': '0',
            'require_folder_pp': '0',
            'require_folder_up': 'default',
            'require_caption': '0',
            'require_whitelist': 'default',
            'feed_users_load': '7',
            'feed_images_load': '5',
            'filter': '3',
            'require_blacklist': '0',
            'require_keywords': '0',
            'require_private_users': '0',
            'task_limits': '0',
            'task_schedule_start': '0',
            'task_schedule_end': '0',
            'task_actions_limit': ''
        }

        post = self.Session.post(self.url + endpoint,
                                 data=payload)

        if post.status_code == 200:
            print('\n' + 'Started account(s) task: Follow')
            print('\t' + '- Account(s) started with success: ' + str(post.json()['done']))
            print('\t' + '- Account(s) failed: ' + str(post.json()['failed']) + '\n')

        else:
            print(str(post.status_code) + ' Unexpected error :/')


    def like_task(self):

        endpoint = '/ig/tasks/start/'

        payload = {
            'task_type': '26',
            'pause_time': '5',
            'actions_amount': '20',
            'pause_from': '18',
            'pause_to': '34',
            'require_tags': 'default',
            'require_userlist': '11079',
            'require_location': 'default',
            'require_comments': 'default',
            'require_biography': '0',
            'require_links': '0',
            'require_folder_pp': '0',
            'require_folder_up': 'default',
            'require_caption': '0',
            'require_whitelist': 'default',
            'feed_users_load': '50',
            'feed_images_load': '1',
            'filter': '1',
            'require_blacklist': '0',
            'require_keywords': '0',
            'require_private_users': '0',
            'task_limits': '0',
            'task_schedule_start': '0',
            'task_schedule_end': '0',
            'task_actions_limit': ''
        }

        post = self.Session.post(self.url + endpoint,
                                 data=payload)

        if post.status_code == 200:
            print('Started account(s) task: Like')
            print('\t' + '- Account(s) started with success: ' + str(post.json()['done']))
            print('\t' + '- Account(s) failed: ' + str(post.json()['failed']))

        else:
            print(str(post.status_code) + ' Unexpected error :/')


    def stop_task(self):

        endpoint = '/ig/accounts/home/'

        ID = [x[0] for x in self.c.execute("SELECT ID FROM account_overview").fetchall()]

        post = self.Session.post(self.url + endpoint,
            params = {
                'ajax': '1'
            },
            data = {
                'customActionType': 'group_action',
                'customActionName': 'stop',
                'id[]': ID
            })

        print('\n' + post.json()['customActionMessage'])


    def ban_manager(self):

        data = [x[0] for x in self.c.execute("SELECT username FROM account_overview WHERE category = 'DirectLinking'").fetchall()]
        url_list = ['https://www.instagram.com/%s/' % (username) for username in data]
        responses = grequests.map((grequests.get(u, params={'__a': '1'}, verify=False) for u in url_list))

        for response in responses:
            username = response.request.url.split('/')[-2]

            if response.status_code == 404:
                banned = self.c.execute("UPDATE ban_manager SET banned = 1 WHERE username = ?", (username,))
                continue

            if not response.json()['user']['biography']:
                not_profiled = self.c.execute("UPDATE ban_manager SET not_profiled = 1 WHERE username =  ?", (username,))
                continue


    def select_delete(self):

        uid = [x[0] for x in self.c.execute("SELECT ID FROM ban_manager WHERE banned = 1 OR not_profiled = 1")]

        if not uid:
            print('\nNo account(s) have been flagged')

        else:
            for x in uid:

                self.c.execute("DELETE FROM account_overview "
                               "WHERE ID = ?", (x,))

                self.c.execute("DELETE FROM ban_manager "
                               "WHERE ID = ?", (x,))

                self.c.execute("DELETE FROM phone_verifier "
                               "WHERE ID = ?", (x,))

        return uid
