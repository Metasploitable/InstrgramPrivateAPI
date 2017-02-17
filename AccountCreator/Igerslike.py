import requests

class Igerslike(object):

    def __init__(self):

        self.url = 'https://www.igerslike.com/'
        self.endpoint = 'ig/accounts/add/'
        self.query_string = {'action': 'add'}


    def upload_accounts(self, items):

        if not items:
            print('\n[-] No account to add, closing application')
            sys.exit(1)

        print('\n[*] Adding account(s) to Igerslike... Please wait')

        payload = {
            'userid': (None, '8650'),
            'submit': (None, 'submit'),
            'accounts': (None, '\n'.join(items)),
            'format': (None, '2'),
            'submit': (None, '')
        }

        return requests.post(self.url + self.endpoint,
            cookies= {
                'PHPSESSID': '',
                'zgusername': '',
                'zgpassword': ''
            }, params=self.query_string, files=payload)
