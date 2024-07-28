# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from ..models.db import db

project_bp = Blueprint('project', __name__)

@project_bp.route('/project/<arg>', defaults={'id': None})
@project_bp.route('/project/<arg>/<id>')
def project(arg,id):
    
    if not 'profile' in session:
        return redirect(url_for('auth.login'))
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
        
    users = db(db.auth_user).select()
    
    long_members = len(users)
    if long_members > 4:
        long_members = long_members / 2
    
    if arg == "new":
        flash('Crea un nuevo proyecto')
        name = ""
        description = ""
        id = 0
        members = []
        
    elif arg == "edit":
        flash('Edita un proyecto')
        row = db(
            (db.projects.id == id) &
            (db.projects.created_by == user['id'])
            ).select().last()
        if row:            
            name = row['name']
            description = row['description']
            members = row['members']            
        else:
            flash('No es posible editar el proyecto')
            return redirect(url_for('main.home'))        
    
    return render_template('project_form.html', arg=arg, name=name, description=description, id=id, users=users, long_members=long_members, members=members)

@project_bp.route('/api/project', methods=['POST'])
def api_project():
    data = request.get_json()
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    
    code = 400
    response = {
        'message': 'Ha ocurrido un error'
    }
    
    name = data.get('name')
    description = data.get('description')
    members = data.get('members')
    arg = data.get('arg')
    id = data.get('id')
    
    if arg == "new":
        insert = db.projects.validate_and_insert(
            name = name,
            description = description,
            members = members,
            created_by = user['id']
        )
        db.commit()        
        
        if insert['id'] != None :
    
            response = {
                'message': 'Tarea creada exitosamente'
            }            
            code = 201
            
        else:
            data = insert['errors']
            first_key = next(iter(data))  
            first_value = data[first_key]  
            error = f"{first_key}: {first_value}"

            response = {'message': error}
            code = 400
            
    elif arg == "edit":
        row = db(db.projects.id == id).select().last()
        if row:
            row.update_record(
                name = name,
                description = description,
                members = members
            )
            db.commit()
            response = {
                'message': 'Proyecto editado exitosamente'                
            }            
            code = 201
        else:
            response = {
                'message': 'Ha ocurrido un error'                
            }            
            code = 400
    
    return jsonify(response), code   

@project_bp.route('/project/delete/<int:id>', methods=['DELETE'])
def delete_row(id):    
    row = db(db.projects.id == id).select().last()
    if row:
        row.update_record(is_active = False)
    db.commit()
    return jsonify({'message': 'Registro eliminado'}), 200
