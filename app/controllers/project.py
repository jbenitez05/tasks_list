# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from ..models.db import db

project_bp = Blueprint('project', __name__)

@project_bp.route('/project/<arg>', defaults={'id': None})
@project_bp.route('/project/<arg>/<id>')
def project(arg,id):
    """
    Muestra el formulario para crear o editar un proyecto.

    Esta función maneja la creación y edición de proyectos basándose en el valor de `arg`. Si `arg` es "new", 
    muestra un formulario para crear un nuevo proyecto con campos vacíos. Si `arg` es "edit", carga la información 
    de un proyecto existente para su edición, siempre que el usuario autenticado sea el creador del proyecto.
    Si el usuario no está autenticado, redirige a la página de inicio de sesión.

    Args:
        arg (str): Determina la acción a realizar; "new" para crear un nuevo proyecto, "edit" para editar un proyecto existente.
        id (int, optional): El ID del proyecto a editar. Solo se usa cuando `arg` es "edit".

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'project_form.html' con la información del proyecto y del formulario.
    """

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
    """
    Maneja la creación y edición de proyectos a través de una API.

    Esta función recibe una solicitud POST con datos en formato JSON para crear o editar un proyecto. 
    Dependiendo del valor de `arg`, se realiza una inserción o actualización en la base de datos. 
    Si la operación es exitosa, retorna un mensaje de éxito; en caso contrario, retorna un mensaje de error.

    Returns:
        tuple: Una respuesta JSON con un mensaje de éxito o error y el código de estado HTTP correspondiente.
    """

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
                'message': 'Proyecto creado exitosamente'
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
    """
    Elimina un proyecto marcándolo como inactivo.

    Esta función maneja la solicitud DELETE para desactivar un proyecto específico en la base de datos en lugar de eliminarlo físicamente.
    Si el proyecto con el ID especificado existe, se marca como inactivo y se guarda el cambio en la base de datos.

    Args:
        id (int): El ID del proyecto a eliminar.

    Returns:
        tuple: Una respuesta JSON con un mensaje de confirmación y el código de estado HTTP 200.
    """

    row = db(db.projects.id == id).select().last()
    if row:
        row.update_record(is_active = False)
    db.commit()
    flash('El proyecto ha sido eliminado')
    return jsonify({'message': 'Registro eliminado'}), 200
