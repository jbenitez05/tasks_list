# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from ..models.db import db

main_bp = Blueprint('main', __name__)

def get_member_name(id,type):
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
    session.pop('_flashes', None)
    return redirect(url_for('index'))

@main_bp.route('/about')
def about():
    return render_template('index.html')

@main_bp.route('/contact')
def contact():
    return render_template('index.html')

@main_bp.route('/home')
def home():
    flash('Aquí puedes crear o gestionar proyectos')
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
    return redirect(url_for('main.home'))