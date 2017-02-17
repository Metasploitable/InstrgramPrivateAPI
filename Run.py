import time
import sqlite3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import custom modules
from Database import Database
from Igerslike import Igerslike

# Create class instances
Database = Database()
Igerslike = Igerslike()

# Login parameters
username = '' # Super secret username bruh
password = '' # Super secret password bruh

# Login on Igerslike and fetch account data
Igerslike.login(username, password)
overviews = Igerslike.fetch_overviews()

# Insert the account data into our Database and update existing data
Database.create_overview(overviews)
Database.update_overview(overviews)
Database.update_ban_manager()
Database.update_phone_verifier()
Database.data_save()

# Delete accounts that have been removed from Igerslike dashboard or banned by Instagram
Database.delete_items(overviews)
Database.data_save()

Igerslike.ban_manager()
UID = Igerslike.select_delete()
Igerslike.delete(UID)

# Edit the accounts that have just been imported by the account creator
Igerslike.edit()
Database.data_save()

# Login accounts that have just been editted
Igerslike.login_accounts()
Database.data_save()

# Save all changes to the database and close it
Database.data_save()
