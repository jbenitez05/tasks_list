# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, render_template_string, flash
from config.parameters import db
import datetime, logging

task_bp = Blueprint('task', __name__)

def get_project_name(id):
    """
    Obtiene el nombre de un proyecto por su ID.

    Esta función busca un proyecto en la base de datos por su ID. Si se encuentra el proyecto, retorna su nombre. 
    Si no se encuentra el proyecto, retorna "Desconocido".

    Args:
        id (int): El ID del proyecto a buscar.

    Returns:
        str: El nombre del proyecto o "Desconocido" si el proyecto no se encuentra.
    """

    if id:
        project = db(db.projects.id == id).select().last()
        if project:
            return project['name']
    return "Desconocido"

@task_bp.route('/task/delete/<int:id>', methods=['DELETE'])
def delete_row(id):   
    """
    Elimina una tarea marcándola como inactiva.

    Esta función maneja la solicitud DELETE para desactivar una tarea específica en la base de datos en lugar de eliminarla físicamente.
    Si la tarea con el ID especificado existe, se marca como inactiva y se guarda el cambio en la base de datos.

    Args:
        id (int): El ID de la tarea a eliminar.

    Returns:
        tuple: Una respuesta JSON con un mensaje de confirmación y el código de estado HTTP 200.
    """

    row = db(db.tasks.id == id).select().last()
    if row:
        row.update_record(is_active = False)
    db.commit()
    return jsonify({'message': 'Registro eliminado'}), 200

@task_bp.route('/update_task', methods=['POST'])
def update_task():
    """
    Actualiza el estado de completado de una tarea y retorna la fila HTML actualizada.

    Esta función maneja la solicitud POST para actualizar el estado de una tarea en la base de datos según el ID proporcionado. 
    Si la tarea existe, se actualiza su estado y se genera una nueva representación HTML para esa fila en la tabla de tareas.
    Si la tarea no se encuentra, retorna un error 404.

    Returns:
        str: La fila HTML actualizada de la tarea si la tarea existe.
        tuple: Una respuesta JSON con un error si la tarea no se encuentra, junto con el código de estado HTTP 404.
    """

    task_id = request.form.get('id')
    is_complete = request.form.get('is_complete') == 'on'
    
    task = db(db.tasks.id==task_id).select().last()
    if task:
        task.update_record(is_complete=is_complete)
        db.commit()
        task = db(db.tasks.id==task_id).select().last()
        
        row_html = render_template_string('''
            <tr id="row-{{ row['id'] }}">
                        <td>{{ row['id'] }}</td>
                        <td>{{ row['project'] }}</td>
                        <td>{{ row['name'] }}</td>
                        <td>{{ row['description'] }}</td>
                        <td><span class="is_complete">{{ row['finish_date'] }}</span></td>
                        <td>
                            <label class="checkbox">
                                <input
                                    type="checkbox"
                                    hx-post="/update_task"
                                    hx-trigger="change"
                                    hx-params="serialize"
                                    hx-target="#row-{{ row['id'] }}"
                                    hx-swap="outerHTML"
                                    name="is_complete"
                                    data-id="{{ row['id'] }}"
                                    {% if row['is_complete'] == True %} checked {% endif %}
                                />
                            </label>
                        </td>
                        <td>{{ row['created_on'].date() }}</td>

                        <td>
                            <a href="/task/edit/{{ row['id'] }}"><button class="button"><i class="fa fa-pencil-square-o" aria-hidden="true"></i>
                            </button></a>
                            <button class="button" id="delete_{{ row['id'] }}" onclick="deleteRow('{{ row['id'] }}')"><i class="fa fa-trash-o" aria-hidden="true"></i></button>
                        </td>
                    </tr>
            ''', row=task)
            
        return row_html
    
    return jsonify(success=False, error="Task not found"), 404

@task_bp.route('/tasks', defaults={'id': None})
@task_bp.route('/tasks/<id>')
def tasks(id):
    """
    Muestra la lista de tareas asociadas a un proyecto o todas las tareas del usuario.

    Esta función maneja la visualización de tareas. Si se proporciona un `id`, muestra las tareas asociadas a un proyecto específico. 
    Si no se proporciona `id`, muestra todas las tareas del usuario. Se actualiza el estado visual de cada tarea según su fecha de finalización.
    Si el usuario no está autenticado, redirige a la página de inicio de sesión.

    Args:
        id (int, optional): El ID del proyecto para filtrar las tareas. Si no se proporciona, se muestran todas las tareas del usuario.

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'task.html' con la lista de tareas y el estado de autenticación del usuario.
    """

    if not 'profile' in session:
        return redirect(url_for('auth.login'))
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    
    orderby = request.args.get('orderby') or "id"
    if orderby.startswith('~'):
        _orderby = ~db.tasks[orderby.replace('~', '')]
    else:
        _orderby = db.tasks[orderby]
    
    if id:
        create = True
        rows = db(
            (db.tasks.project == id) &
            (db.tasks.is_active == True) &
            (
                (db.tasks.created_by == user['id']) |
                (db.tasks.assigned_to == user['id'])
            ) 
            ).select(orderby=_orderby)
    else:
        create = False
        id=0
        rows = db(
            (db.tasks.is_active == True) &
            (
                (db.tasks.created_by == user['id']) |
                (db.tasks.assigned_to == user['id'])
            ) 
            ).select(orderby=_orderby)
    now = datetime.date.today()
    status = {
        "0": "Reserva",
        "1": "Preparado",
        "2": "En progreso",
        "3": "Hecho"
    }
    for row in rows:
        fecha = row['finish_date']
        cinco_dias = now + datetime.timedelta(days=5)
        row['project'] = get_project_name(row['project'])
        row['status'] = status[row['status']]
        
        if row['is_complete'] == True:
            row['span'] = "complete"
        else:
            if fecha <= now:
                row['span'] = "danger"
            elif now < fecha <= cinco_dias:
                row['span'] = "alert"
            else:
                row['span'] = "allok"
                
    user_logged_in = 'profile' in session
    return render_template('task.html', user_logged_in=user_logged_in, rows=rows, orderby=orderby, create=create, id=id)

@task_bp.route('/task/<arg>', defaults={'id': None})
@task_bp.route('/task/<arg>/<id>')
def task(arg,id):
    """
    Muestra el formulario para crear o editar una tarea.

    Esta función maneja la visualización de un formulario para la creación o edición de tareas. Si `arg` es "new", 
    se muestra un formulario para crear una nueva tarea. Si `arg` es "edit", se carga la información de una tarea existente 
    para su edición, siempre que el usuario autenticado sea el creador de la tarea. 
    Si el usuario no está autenticado, redirige a la página de inicio de sesión.

    Args:
        arg (str): Determina la acción a realizar; "new" para crear una nueva tarea, "edit" para editar una tarea existente.
        id (int, optional): El ID de la tarea a editar. Solo se usa cuando `arg` es "edit".

    Returns:
        werkzeug.wrappers.Response: La renderización de la plantilla 'task_form.html' con la información de la tarea y del formulario.
    """

    if not 'profile' in session:
        return redirect(url_for('auth.login'))
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    
    users = []  
    
    projects = db(
        (db.projects.members.contains(user['id'])) &
        (db.projects.is_active == True)
        ).select()
    
    if id:
        project = db(
            (db.projects.id == id)
            ).select().last()
        if project and project['members'] != None:
            users = db(db.auth_user.id.belongs(project['members'])).select()
        else:
            users = []
    else:
        project = None
    
    long_members = len(users)
    if long_members > 4:
        long_members = long_members / 2
        
    now = datetime.date.today()
    if arg == "new":
        flash('Crea una nueva tarea')
        name = ""
        description = ""
        finish_date = now
        is_complete = False
        id = id if id else None
        members = project['members']
        status = "0"
    elif arg == "edit":
        
        row = db(
            (db.tasks.id == id) &
            (db.tasks.created_by == user['id'])
            ).select().last()
        if row:
            project = db(db.projects.id == row['project']).select().last()
            if project and project['members'] != None:
                users = db(db.auth_user.id.belongs(project['members'])).select()
            flash('Edita la tarea')    
            name = row['name']
            description = row['description']
            finish_date = row['finish_date']
            is_complete = row['is_complete']
            id = row['id']    
            members = row['assigned_to']
            status = row['status']        
        else:
            return redirect(url_for('main.home'))
    
    return render_template('task_form.html', finish_date=finish_date, arg=arg, name=name, description=description, is_complete=is_complete, id=id, now=now, projects=projects, project=project, long_members=long_members, members=members, users=users,status=status)

@task_bp.route('/api/task', methods=['POST'])
def api_task():
    """
    Maneja la creación y edición de tareas a través de una API.

    Esta función recibe una solicitud POST con datos en formato JSON para crear o editar una tarea. 
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
    finish_date = data.get('finish_date')
    arg = data.get('arg')
    is_complete = data.get('is_complete', False)
    id = data.get('id')
    assigned_to = data.get('members')
    status = data.get('status')
    
    if arg == "new":
        insert = db.tasks.validate_and_insert(
            name = name,
            project = id,
            description = description,
            finish_date = finish_date,
            is_complete = False,
            created_by = user['id'],
            assigned_to = assigned_to,
            status = status
        )
        db.commit()       
        if insert['id'] != None :
    
            response = {'message': 'Tarea creada exitosamente'}            
            code = 201
            
        else:
            data = insert['errors']
            first_key = next(iter(data))  
            first_value = data[first_key]  
            error = f"{first_key}: {first_value}"

            response = {'message': error}
            code = 400
            
    elif arg == "edit":
        row = db(db.tasks.id == id).select().last()
        if row:
            row.update_record(
                name = name,
                description = description,
                finish_date = finish_date,
                is_complete = is_complete,
                assigned_to = assigned_to,
                status = status
            )
            db.commit()
            response = {
                'message': 'Tarea editada exitosamente'                
            }            
            code = 201
        else:
            response = {
                'message': 'Ha ocurrido un error'                
            }            
            code = 400
            
    return jsonify(response), code
