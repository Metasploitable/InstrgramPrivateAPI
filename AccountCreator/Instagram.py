import requests
import configparser
import json
import uuid
import hmac
import time
import hashlib
from urllib.parse import urlencode

# Import custom modules
from Constants import Constants
from Dongle import Modem

# Open config file
Config = configparser.ConfigParser()
Config.read('_Configs/android.ini')


class Instagram(object):

    def __init__(self):

        # Create user-agent
        self.userAgent = 'Instagram' + ' ' + str(Constants.VERSION) + ' ' + 'Android (21/5.0.2; 480dpi; 1080x1920; HTC/htc; HTC One; m7; m7; nl_NL)'

        # Set headers
        self.headers = dict(Config.items('headers'))
        self.headers['user-agent'] = self.userAgent

        # Set static uuid
        self.uuid = self.generate_uuid()

        # Make session
        self.Session = requests.Session()

    def cookies(self):
        # Start by filling the cookiejar with valid cookies

        data = {'id': self.uuid, 'experiments': Constants.EXPERIMENTS}

        resp = self.Session.post(Constants.API_URL + 'qe/sync/', headers=self.headers, data=self.signature(data), timeout=30.000).cookies


    def check_username(self, username):
        # Check is username is available before passing it to the create_accounts function

        data = {
            '_uuid':         self.uuid,
            'username':      username,
            '_csrftoken':    self.Session.cookies['csrftoken']
        }

        return self.Session.post(Constants.API_URL + 'users/check_username/',
            headers=self.headers, data=self.signature(data), verify=False)


    def create_accounts(self, username, password, email):

        data = {
            'phone_id':              self.generate_uuid(),
            '_csrftoken':            self.Session.cookies['csrftoken'],
            'username':              username,
            'first_name':            '',
            'guid':                  self.uuid,
            'device_id':             self.device_id(hashlib.md5((str(username) + str(password)).encode("utf-8"))),
            'email':                 email,
            'waterfall_id':          self.generate_uuid(),
            'force_sign_up_code':    '',
            'qs_stamp':              '',
            'password':              password
        }

        return self.Session.post(Constants.API_URL + 'accounts/create/',
            headers=self.headers, data=self.signature(data), timeout=30.00)


    def generate_uuid(self):

        return str(uuid.uuid4())


    def device_id(self, seed):

        return 'android-' + hashlib.md5(seed.digest()).hexdigest()[16:]


    def signature(self, data):

        body = json.dumps(data).encode('utf-8')
        hmacForBody = hmac.new(Constants.IG_SIG_KEY, msg=body, digestmod=hashlib.sha256).hexdigest()
        return urlencode({'ig_sig_key_version': Constants.SIG_KEY_VERSION, 'signed_body': hmacForBody + '.' + body.decode('utf-8')})


    def follow(self):

        # Follow method
        notes = ['460563723', '12281817', '173560420', '7719696', '6860189', '247944034']

        data = {
            '_csrftoken': self.Session.cookies['csrftoken'],
            'user_id': '',
            '_uid': self.Session.cookies['ds_user_id'],
            '_uuid': self.uuid
        }

        for user in notes:
            time.sleep(1)
            data['user_id'] = str(user)

            self.Session.post(Constants.API_URL + 'friendships/create/' + str(user) + '/',
                headers=self.headers, data=self.signature(data))


    def upload_profile_picture(self, ImagePath):

        data = {
            '_csrftoken': self.Session.cookies['csrftoken'],
            '_uid': self.Session.cookies['ds_user_id'],
            '_uuid': self.uuid
        }

        self.Session.post(Constants.API_URL + 'accounts/change_profile_picture/')
