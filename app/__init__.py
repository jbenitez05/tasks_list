# -*- coding: utf-8 -*-

from flask import Flask
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from config import parameters
import logging, os

def create_app():
    """
    Crea y configura una instancia de la aplicación Flask.

    Esta función configura una instancia de Flask con las configuraciones necesarias para la autenticación con OAuth 
    usando GitHub y Google. Establece la clave secreta de la aplicación y configura el sistema de logging. 
    También registra los blueprints para las rutas principales, de autenticación, de proyectos y de tareas.

    Returns:
        Flask: La instancia configurada de la aplicación Flask.
    """

    app = Flask(__name__)
    app.secret_key = parameters.secret_key

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(asctime)s - %(message)s',
        filename=parameters.logging_file,
        filemode='a'
    )

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'sessions')  # Directorio para almacenar sesiones
    app.config['SESSION_PERMANENT'] = False  # La sesión no expira automáticamente
    app.config['SESSION_USE_SIGNER'] = True  # Para firmar la cookie de sesión
    
    Session(app)
    
    app.config['GITHUB_CLIENT_ID'] = parameters.github_client_id
    app.config['GITHUB_CLIENT_SECRET'] = parameters.github_client_secret
    app.config['GOOGLE_CLIENT_ID'] = parameters.google_client_id
    app.config['GOOGLE_CLIENT_SECRET'] = parameters.google_client_secret

    oauth = OAuth(app)
    
    app.oauth_clients = {
        'github': oauth.register(
            name='github',
            client_id=app.config['GITHUB_CLIENT_ID'],
            client_secret=app.config['GITHUB_CLIENT_SECRET'],
            authorize_url='https://github.com/login/oauth/authorize',
            access_token_url='https://github.com/login/oauth/access_token',
            redirect_uri=parameters.github_callback,
            client_kwargs={'scope': 'user:email'},
            api_base_url='https://api.github.com/'
        ),
        'google': oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            redirect_uri=parameters.google_callback,
            client_kwargs={'scope': 'profile email'},
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
        )
    }

    from .controllers.main import main_bp
    from .controllers.auth import auth_bp
    from .controllers.project import project_bp
    from .controllers.task import task_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)

    return app
