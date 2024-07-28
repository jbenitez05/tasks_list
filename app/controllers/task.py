# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, render_template_string
from config.parameters import db
import datetime, logging

task_bp = Blueprint('task', __name__)

def get_project_name(id):
    if id:
        project = db(db.projects.id == id).select().last()
        if project:
            return project['name']
    return "Desconocido"

@task_bp.route('/task/delete/<int:id>', methods=['DELETE'])
def delete_row(id):    
    row = db(db.tasks.id == id).select().last()
    if row:
        row.update_record(is_active = False)
    db.commit()
    return jsonify({'message': 'Registro eliminado'}), 200

@task_bp.route('/update_task', methods=['POST'])
def update_task():
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
    
    for row in rows:
        fecha = row['finish_date']
        cinco_dias = now + datetime.timedelta(days=5)
        row['project'] = get_project_name(row['project'])
        
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
    
    if not 'profile' in session:
        return redirect(url_for('auth.login'))
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    
    projects = db(
        (db.projects.members.contains(user['id'])) &
        (db.projects.is_active == True)
        ).select()
    
    if id:
        project = db(
            (db.projects.id == id)
            ).select().last()
    else:
        project = None
    
    now = datetime.date.today()
    if arg == "new":
        name = ""
        description = ""
        finish_date = now
        is_complete = False
        id = id if id else None
    elif arg == "edit":
        row = db(
            (db.tasks.id == id) &
            (db.tasks.created_by == user['id'])
            ).select().last()
        if row:            
            name = row['name']
            description = row['description']
            finish_date = row['finish_date']
            is_complete = row['is_complete']
            id = row['id']            
        else:
            return redirect(url_for('main.home'))
    
    return render_template('task_form.html', finish_date=finish_date, arg=arg, name=name, description=description, is_complete=is_complete, id=id, now=now, projects=projects, project=project)

@task_bp.route('/api/task', methods=['POST'])
def api_task():
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
    
    if arg == "new":
        insert = db.tasks.validate_and_insert(
            name = name,
            project = id,
            description = description,
            finish_date = finish_date,
            is_complete = False,
            created_by = user['id']
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
                is_complete = is_complete
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
