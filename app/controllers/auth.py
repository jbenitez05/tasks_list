# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, current_app, flash
from ..models.db import db
from authlib.oauth2.rfc6749.errors import OAuth2Error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/logout')
def logout():
    """
    Cierra la sesión del usuario y redirige a una URL específica.

    Esta función limpia la sesión del usuario, eliminando cualquier dato almacenado en la sesión actual, y luego redirige al usuario a una URL especificada.

    Returns:
        werkzeug.wrappers.Response: Una redirección HTTP a la URL especificada.
    """
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    """
    Muestra el perfil del usuario si está autenticado.

    Esta función verifica si el perfil del usuario está en la sesión. 
    Si no lo está, redirige al usuario a la página principal. 
    Si el perfil está en la sesión, se obtiene y se pasa a la plantilla del perfil para su renderizado.

    Returns:
        werkzeug.wrappers.Response: La página de perfil del usuario si está autenticado, 
        de lo contrario, una redirección a la página principal.
    """
    if not 'profile' in session:
        return redirect(url_for('main.home'))
    profile = session.get('profile')
    user_logged_in = 'profile' in session
    return render_template('profile.html', profile=profile, user_logged_in=user_logged_in)

@auth_bp.route('/login')
def login():
    """
    Muestra la página de inicio de sesión o redirige al perfil del usuario si ya está autenticado.

    Esta función verifica si el usuario ya ha iniciado sesión comprobando si hay un perfil en la sesión.
    Si el perfil está en la sesión, redirige al usuario a la página de perfil.
    Si no, muestra la página de inicio de sesión.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página de perfil del usuario si está autenticado, 
        de lo contrario, la página de inicio de sesión.
    """
    flash("Inicia sesión con el servicio de tu preferencia")
    if 'profile' in session:
        return redirect(url_for('auth.profile'))
    return render_template('login.html', user_logged_in=False)

@auth_bp.route('/login/github')
def login_github():
    """
    Inicia el proceso de autenticación con GitHub.

    Esta función verifica si el usuario ya ha iniciado sesión comprobando si hay un perfil en la sesión.
    Si el perfil está en la sesión, redirige al usuario a la página principal.
    Si no, inicia el proceso de autenticación con GitHub, redirigiendo al usuario a la URL de autorización de GitHub.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página principal si el usuario ya está autenticado, 
        de lo contrario, una redirección a la página de autorización de GitHub.
    """
    if 'profile' in session:
        return redirect(url_for('main.home'))
    github = current_app.oauth_clients['github']
    redirect_uri = url_for('auth.authorize_github', _external=True)
    return github.authorize_redirect(redirect_uri)    

@auth_bp.route('/login/google')
def login_google():
    """
    Inicia el proceso de autenticación con Google.

    Esta función verifica si el usuario ya ha iniciado sesión comprobando si hay un perfil en la sesión.
    Si el perfil está en la sesión, redirige al usuario a la página principal.
    Si no, inicia el proceso de autenticación con Google, redirigiendo al usuario a la URL de autorización de Google.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página principal si el usuario ya está autenticado, 
        de lo contrario, una redirección a la página de autorización de Google.
    """
    if 'profile' in session:
        return redirect(url_for('main.home'))
    google = current_app.oauth_clients['google']
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/github')
def authorize_github():
    """
    Maneja la devolución de llamada de GitHub y autentica al usuario.

    Esta función es llamada después de que el usuario haya autorizado la aplicación en GitHub.
    Obtiene el token de acceso de GitHub y utiliza este token para obtener la información del perfil del usuario.
    Luego, guarda o actualiza la información del usuario en la base de datos y establece la información del perfil en la sesión.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página principal.
    """

    github = current_app.oauth_clients['github']
    try:
        token = github.authorize_access_token()
    except OAuth2Error as error:
        return f'Error: {error.error}'
    resp = github.get('user')
    profile = resp.json()
    
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
    flash(f"Bienvenido(a) {user_name}")
    return redirect(url_for('main.home'))

@auth_bp.route('/callback/google')
def authorize_google():
    """
    Maneja la devolución de llamada de Google y autentica al usuario.

    Esta función es llamada después de que el usuario haya autorizado la aplicación en Google.
    Obtiene el token de acceso de Google y utiliza este token para obtener la información del perfil del usuario.
    Luego, guarda o actualiza la información del usuario en la base de datos y establece la información del perfil en la sesión.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página principal.
    """

    google = current_app.oauth_clients['google']
    try:
        token = google.authorize_access_token()
    except OAuth2Error as error:
        return f'Error: {error.error}'
    
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    profile = resp.json()
    
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
    flash(f"Bienvenido(a) {user_login}")
    return redirect(url_for('main.home'))

