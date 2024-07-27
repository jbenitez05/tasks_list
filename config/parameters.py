# -*- coding: utf-8 -*-

from configparser import ConfigParser 
from pydal import DAL
import os

pwd = os.getcwd()
try:
    os.stat(pwd + '/app/databases')
except:
    os.mkdir(pwd + '/app/databases')
    
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

google_client_id = configuration.get('google','client_id') or None
google_client_secret = configuration.get('google','client_secret') or None

logging_file = configuration.get('logs','route') or pwd