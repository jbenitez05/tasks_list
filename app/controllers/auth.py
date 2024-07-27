# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, current_app
from ..models.db import db
from authlib.oauth2.rfc6749.errors import OAuth2Error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    if not 'profile' in session:
        return redirect(url_for('main.home'))
    profile = session.get('profile')
    user_logged_in = 'profile' in session
    return render_template('profile.html', profile=profile, user_logged_in=user_logged_in)

@auth_bp.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('auth.profile'))
    return render_template('login.html', user_logged_in=False)

@auth_bp.route('/login/github')
def login_github():
    if 'profile' in session:
        return redirect(url_for('main.home'))
    github = current_app.oauth_clients['github']
    redirect_uri = url_for('auth.authorize_github', _external=True)
    return github.authorize_redirect(redirect_uri)    

@auth_bp.route('/login/google')
def login_google():
    if 'profile' in session:
        return redirect(url_for('main.home'))
    google = current_app.oauth_clients['google']
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/github')
def authorize_github():
    github = current_app.oauth_clients['github']
    try:
        token = github.authorize_access_token()
    except OAuth2Error as error:
        return f'Error: {error.error}'
    resp = github.get('user')
    profile = resp.json()

    # Guardar los datos del usuario en la base de datos
    user_id = profile['id']
    user_login = profile['login']
    user_name = profile.get('name')
    user_email = profile.get('email')

    user = db(db.auth_user.github_id == user_id).select().first()
    if user:
        user.update_record(username=user_login, name=user_name, email=user_email)
    else:
        db.auth_user.insert(github_id=user_id, username=user_login, name=user_name, email=user_email)
    db.commit()

    session['profile'] = profile
    return redirect(url_for('main.home'))

@auth_bp.route('/callback/google')
def authorize_google():
    google = current_app.oauth_clients['google']
    try:
        token = google.authorize_access_token()
    except OAuth2Error as error:
        return f'Error: {error.error}'
    # Cambia la URL del endpoint para obtener la información del usuario
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    profile = resp.json()

    # Guardar los datos del usuario en la base de datos
    user_id = profile['sub']
    user_login = profile.get('name')
    user_email = profile.get('email')

    user = db(db.auth_user.google_id == user_id).select().first()
    if user:
        user.update_record(name=user_login, email=user_email)
    else:
        db.auth_user.insert(google_id=user_id, name=user_login, email=user_email)
    db.commit()
    
    session['profile'] = profile
    return redirect(url_for('main.home'))

