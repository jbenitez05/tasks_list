# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from ..models.db import db
from ..classes.populate import Populate
import logging

main_bp = Blueprint('main', __name__)

def get_member_name(id,type):
    """
    Obtiene el nombre del miembro y, opcionalmente, su correo electrónico.

    Esta función busca un usuario en la base de datos por su ID. Si se encuentra un usuario, 
    retorna su nombre. Dependiendo del valor de `type`, también puede incluir el correo electrónico del usuario.
    Si no se encuentra el usuario, retorna "Desconocido".

    Args:
        id (int): El ID del usuario a buscar.
        type (int): Tipo de información a retornar. Si es 0, retorna solo el nombre.
                    Si es 1, retorna el nombre y el correo electrónico.

    Returns:
        str: El nombre del usuario, opcionalmente con su correo electrónico, o "Desconocido" si no se encuentra el usuario.
    """

    if id:
        user = db(db.auth_user.id == id).select().last()
        if user:
            if type == 0:
                return f"{user['name']}"
            elif type == 1:
                return f"{user['name']} - {user['email']}"
    return "Desconocido"

@main_bp.route('/clear_flash')
def clear_flash():
    """
    Limpia los mensajes flash de la sesión y redirige a la página de inicio.

    Esta función elimina los mensajes flash almacenados en la sesión para limpiar cualquier notificación o mensaje temporal
    y luego redirige al usuario a la página de inicio.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página de inicio.
    """
    session.pop('_flashes', None)
    return redirect(url_for('index'))

@main_bp.route('/about')
def about():
    """
    Renderiza la página de información.

    Esta función muestra la página de información al usuario, generando el contenido basado en la plantilla 'index.html'.

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'index.html'.
    """

    return render_template('index.html')

@main_bp.route('/contact')
def contact():
    """
    Renderiza la página de contacto.

    Esta función muestra la página de contacto al usuario, generando el contenido basado en la plantilla 'index.html'.

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'index.html'.
    """

    return render_template('index.html')

@main_bp.route('/home')
def home():
    """
    Muestra la página de inicio con una lista de proyectos.

    Esta función verifica si el usuario está autenticado; si no lo está, redirige a la página de inicio de sesión. 
    Luego, recupera y ordena los proyectos asociados al usuario actual, ya sea como creador o miembro.
    Los proyectos activos se obtienen y se enriquecen con información adicional como los nombres de los miembros. 
    Finalmente, renderiza la plantilla 'index.html' con la información de los proyectos y el estado de autenticación del usuario.

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'index.html' con los proyectos y el estado de autenticación del usuario.
    """
    
    if not 'profile' in session:
        return redirect(url_for('auth.login'))
    
    orderby = request.args.get('orderby') or "id"
    if orderby.startswith('~'):
        _orderby = ~db.projects[orderby.replace('~', '')]
    else:
        _orderby = db.projects[orderby]
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    projects = db(
        (
            (db.projects.created_by == user['id']) |
            (db.projects.members.contains(user['id']))
        ) &
        (db.projects.is_active == True)
        ).select(orderby=_orderby)
    
    for project in projects:
        project['created_by'] = get_member_name(project['created_by'],0)
        project['len_members'] = len(project['members']) if project['members'] else 0
        project['member_list'] = ""
        if project['members'] != None:
            for member in project['members']:
                name = get_member_name(member,1)
                project['member_list'] = project['member_list'] + "\n" + name
    
    user_logged_in = 'profile' in session
    return render_template('index.html', user_logged_in=user_logged_in, rows=projects, orderby=orderby)

@main_bp.route('/')
def index():
    """
    Redirige a la página de inicio.

    Esta función redirige a los usuarios a la página de inicio del sitio, definida por la ruta '/home'.

    Returns:
        werkzeug.wrappers.Response: Una redirección a la página de inicio.
    """
    len_users = db(db.auth_user).count()
    if len_users < 2:
        populate = Populate()
        populate.populate_auth_user_table()
    return redirect(url_for('main.home'))