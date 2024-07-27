# -*- coding: utf-8 -*-

from flask import Flask
from authlib.integrations.flask_client import OAuth
from config import parameters
import logging

def create_app():
    app = Flask(__name__)
    app.secret_key = parameters.secret_key

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(asctime)s - %(message)s',
        filename=parameters.logging_file,
        filemode='a'
    )

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
            redirect_uri='http://127.0.0.1:5000/callback/github',
            client_kwargs={'scope': 'user:email'},
            api_base_url='https://api.github.com/'
        ),
        'google': oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            redirect_uri='http://127.0.0.1:5000/callback/google',
            client_kwargs={'scope': 'profile email'},
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
        )
    }

    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.project import project_bp
    from .routes.task import task_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)

    return app
