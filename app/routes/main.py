# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request
from config.parameters import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/about')
def about():
    return render_template('index.html')

@main_bp.route('/contact')
def contact():
    return render_template('index.html')

@main_bp.route('/home')
def home():
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
        (db.projects.members.contains(user['id'])) &
        (db.projects.created_by == user['id'])
        ).select()
    
    user_logged_in = 'profile' in session
    return render_template('index.html', user_logged_in=user_logged_in, rows=projects, orderby=orderby)

@main_bp.route('/')
def index():
    return redirect(url_for('main.home'))