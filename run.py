# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session, render_template_string
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from models.db import db
from config import parameters, nav_menu
import datetime

app = Flask(__name__)

# Configuración
app.config['JWT_SECRET_KEY'] = parameters.secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
jwt = JWTManager(app)

@app.context_processor
def inject_vars():
    year = datetime.datetime.now().year
    menu = nav_menu.nav_routes    
    return dict(year=year,menu=menu)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_row(id):    
    row = db(db.tasks.id == id).select().last()
    if row:
        row.update_record(is_active = False)
    db.commit()
    return jsonify({'message': 'Registro eliminado'}), 200

@app.route('/update_task', methods=['POST'])
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
                        <td>{{ row['name'] }}</td>
                        <td>{{ row['description'] }}</td>
                        <td style="{{ row['style'] }}" >{{ row['finish_date'] }}</td>
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
    
@app.route('/home')
def home():
    
    orderby = request.args.get('orderby') or "id"
    if orderby.startswith('~'):
        _orderby = ~db.tasks[orderby.replace('~', '')]
    else:
        _orderby = db.tasks[orderby]

    rows = db(db.tasks.is_active == True).select(orderby=_orderby)
    now = datetime.date.today()
    
    for row in rows:
        fecha = row['finish_date']
        cinco_dias = now + datetime.timedelta(days=5)
        
        if row['is_complete'] == True:
            row['style'] = "color:black"
        else:
            if fecha <= now:
                row['style'] = "color:red"
            elif now < fecha <= cinco_dias:
                row['style'] = "color:blue"
            else:
                row['style'] = "color:green"
    return render_template('index.html', rows=rows, orderby=orderby)

@app.route('/task/<arg>', defaults={'id': None})
@app.route('/task/<arg>/<id>')
def task(arg,id):
    
    now = datetime.date.today()
    if arg == "new":
        name = ""
        description = ""
        finish_date = now
        is_complete = False
        id = 0
    elif arg == "edit":
        row = db(db.tasks.id == id).select().last()
        name = row['name']
        description = row['description']
        finish_date = row['finish_date']
        is_complete = row['is_complete']
        id = row['id']
    
    return render_template('task.html', finish_date=finish_date, arg=arg, name=name, description=description, is_complete=is_complete, id=id, now=now)

@app.route('/api/task', methods=['POST'])
def api_task():
    data = request.get_json()
    
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
            description = description,
            finish_date = finish_date,
            is_complete = False
        )
        db.commit()        
        
        if insert['id'] != None :
    
            response = {
                'message': 'Tarea creada exitosamente'
            }            
            code = 201
            
        else:
            response = {
                'message': 'Ha ocurrido un error'
            }
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    
    if not first_name or not last_name or not email or not password :
        return jsonify({"msg": "Faltan datos"}), 400

    if db(db.auth_user.email == email).select().first():
        return jsonify({"msg": "Ya existe un usuario con este correo"}), 400

    hashed_password = generate_password_hash(password)
    db.auth_user.validate_and_insert(
        first_name=first_name,
        last_name=last_name,
        email=email, 
        password=hashed_password
        )
    db.commit()
    
    return jsonify({"msg": "Usuario registrado exitosamente"}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = db(db.auth_user.email == email).select().first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Credenciales inválidas"}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout exitoso"}), 200

@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)