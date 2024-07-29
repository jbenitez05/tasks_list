# -*- coding: utf-8 -*-

from configparser import ConfigParser 
from pydal import DAL
import os

pwd = os.getcwd()
try:
    os.stat(pwd + '/databases')
except:
    os.mkdir(pwd + '/databases')
    
configuration = ConfigParser()
configuration.read('private/appconfig.ini')

db = DAL(configuration.get('db','uri'),
            pool_size=configuration.get('db','pool_size'),
            migrate_enabled=configuration.get('db','migrate'),
            folder=configuration.get('db','folder'),
            check_reserved=['all']
        )

secret_key = configuration.get('secret','secret_key') or None

github_client_id = configuration.get('github','client_id') or None
github_client_secret = configuration.get('github','client_secret') or None
github_callback = configuration.get('github','callback') or "http://127.0.0.1:5000/callback/github"

google_client_id = configuration.get('google','client_id') or None
google_client_secret = configuration.get('google','client_secret') or None
google_callback = configuration.get('google','callback') or "http://127.0.0.1:5000/callback/google"

logging_file = configuration.get('logs','route') or pwd