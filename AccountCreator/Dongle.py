import time
import requests
import subprocess
import lxml.html

class Modem(object):

    def __init__(self):

        self.IP = None
        self.url = 'http://192.168.8.1/api/'

    def restart(self):

        # Fetch verification token for the 3G modem
        token = requests.get(self.url + 'webserver/token').content
        token = lxml.html.fromstring(token).xpath('//token/text()')[0]


        # Change 3G session variable by logging in
        requests.post(self.url + 'user/login',
            headers={'__RequestVerificationToken': token},
            data= '<?xml version="1.0" encoding="UTF-8"?><request><Username>admin</Username><Password>YWRtaW4=</Password></request>'
        )

        # Disconnect from 3G network

        requests.post(self.url + 'dialup/mobile-dataswitch',
            headers={'__RequestVerificationToken': token},
            data= '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>0</dataswitch></request>'
        )


        # Connect to 3G network, with a new IP (hopefully)
        requests.post(self.url + 'dialup/mobile-dataswitch',
            headers={'__RequestVerificationToken': token},
            data= '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>1</dataswitch></request>'
        )

        while True:
            time.sleep(1)
            try:
                self.IP = requests.get('https://httpbin.org/ip').json()['origin']
                break
            except Exception:
                pass
