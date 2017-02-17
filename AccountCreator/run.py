from Instagram import *
from Dongle import *
from Exceptions import *
from Igerslike import *
from Database import *
import time
import sys

# Create class instances
Instagram = Instagram()
Database = Database()
Dongle = Modem()
Igerslike = Igerslike()

# Set file variables
#fullnames = open('_fullnames.txt').readlines()
recovery = open('_recovery.txt', 'a')

# Set script variables
offset = 0
e_offset = 0
items = []

# print how many accounts we need
print('\nAccount to create: ', str(Database.calculate_accounts()) + '\n')

while offset < Database.calculate_accounts():

    # Restart 3G modem
    Dongle.restart()

    # Fetch account_creation paramaters from our Database
    username, password, email = Database.get_values()

    # Get mid & csrf cookies
    try:
        cookies = Instagram.cookies()
    except requests.exceptions.ReadTimeout:
        continue

    # Check if account username is available
    check = Instagram.check_username(username)

    if check.status_code == 200 and check.json()['available'] == False:
        continue

    # Start creating account(s)
    try:
        account = Instagram.create_accounts(username, password, email)
    except requests.exceptions.ReadTimeout:
        continue

    if account.status_code == 200 and account.json()['account_created'] == True:
        items.append(str(username) + ':' + str(password))
        recovery.write(username + ':' + password + '\n')
        offset+=1
        print('[*]' + ' [' + str(Dongle.IP) + '] ' + str(username) + ' - ' + str(password) + ' created')

    elif account.status_code == 400 and account.json()['spam'] == True:
        e_offset += 1
        print('[-] IP ' + str(Dongle.IP) + ' Is flagged as spam')
        continue

    else:
        print(account.json())

    if e_offset == 50:
        print('Max amount of errors reached :/')
        sys.exit(1)

    # After account creation do some follow
    follow = Instagram.follow()

    Instagram.Session.close()

# Upload the account to Igerslike!
upload = Igerslike.upload_accounts(items)

if upload.status_code == 200:
    print('[*] Successfully added ' + str(len(items)) + ' item to Igerslike')
