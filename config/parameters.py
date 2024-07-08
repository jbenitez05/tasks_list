# -*- coding: utf-8 -*-

from configparser import ConfigParser 
from pydal import DAL
import os

pwd = os.getcwd()
try:
    os.stat(pwd + '/databases')
except:
    os.mkdir(pwd + '/databases')

try:
    os.stat(pwd + '/uploads')
except:
    os.mkdir(pwd + '/uploads')
    
configuration = ConfigParser()
configuration.read('private/appconfig.ini')

db = DAL(configuration.get('db','uri'),
            pool_size=configuration.get('db','pool_size'),
            migrate_enabled=configuration.get('db','migrate'),
            folder=configuration.get('db','folder'),
            check_reserved=['all']
        )

secret_key = configuration.get('secret','secret_key') or None