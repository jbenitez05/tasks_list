# -*- coding: utf-8 -*-

"""
Configura la conexión a la base de datos y las credenciales de autenticación.

Esta sección configura la conexión a la base de datos usando `pydal` y lee las configuraciones desde un archivo `.ini`. 
Crea el directorio de bases de datos si no existe y obtiene las configuraciones necesarias para la autenticación con GitHub y Google, 
así como la configuración para el archivo de logging.

- `db`: Instancia de la conexión a la base de datos.
- `secret_key`: Clave secreta para la aplicación.
- `github_client_id`, `github_client_secret`, `github_callback`: Configuración para la autenticación con GitHub.
- `google_client_id`, `google_client_secret`, `google_callback`: Configuración para la autenticación con Google.
- `logging_file`: Ruta del archivo de logging.
"""

from configparser import ConfigParser 
from pydal import DAL
import os

pwd = os.getcwd()
try:
    os.stat(pwd + '/databases')
except:
    os.mkdir(pwd + '/databases')
    
try:
    os.stat(pwd + '/sessions')
except:
    os.mkdir(pwd + '/sessions')
    
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