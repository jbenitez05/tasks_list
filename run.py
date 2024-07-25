# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, url_for, redirect, session, render_template_string
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6749.errors import OAuth2Error

from models.db import db
from config import parameters, nav_menu
import datetime, argparse, logging
from waitress import serve

app = Flask(__name__)
app.secret_key = parameters.secret_key

logging.basicConfig(
                    level=logging.INFO,
                    format='%(levelname)s - %(asctime)s - %(message)s',
                    filename= parameters.logging_file,
                    filemode='a'
                    )

app.config['GITHUB_CLIENT_ID'] = parameters.github_client_id
app.config['GITHUB_CLIENT_SECRET'] = parameters.github_client_secret
app.config['GOOGLE_CLIENT_ID'] = parameters.google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = parameters.google_client_secret

oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/callback/github',
    client_kwargs={'scope': 'user:email'},
    api_base_url='https://api.github.com/'  # URL base de la API de GitHub
)

google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/callback/google',
    client_kwargs={'scope': 'profile email'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)

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
    
    if not 'profile' in session:
        return redirect(url_for('login'))
    
    email = session['profile']['email']
    user = db(db.auth_user.email == email).select().last()
    
    orderby = request.args.get('orderby') or "id"
    if orderby.startswith('~'):
        _orderby = ~db.tasks[orderby.replace('~', '')]
    else:
        _orderby = db.tasks[orderby]

    rows = db(
        (db.tasks.is_active == True) &
        (db.tasks.created_by == user['id'])
        ).select(orderby=_orderby)
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
                
    user_logged_in = 'profile' in session
    return render_template('index.html', user_logged_in=user_logged_in, rows=rows, orderby=orderby)

@app.route('/task/<arg>', defaults={'id': None})
@app.route('/task/<arg>/<id>')
def task(arg,id):
    
    if not 'profile' in session:
        return redirect(url_for('login'))
    
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
            description = description,
            finish_date = finish_date,
            is_complete = False,
            created_by = user['id']
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

@app.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('profile'))
    return render_template('login.html', user_logged_in=False)

@app.route('/login/github')
def login_github():
    if 'profile' in session:
        return redirect(url_for('home'))
    redirect_uri = url_for('authorize_github', _external=True)
    return github.authorize_redirect(redirect_uri)    

@app.route('/login/google')
def login_google():
    if 'profile' in session:
        return redirect(url_for('home'))
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/callback/github')
def authorize_github():
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
    return redirect(url_for('home'))

@app.route('/callback/google')
def authorize_google():
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
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if not 'profile' in session:
        return redirect(url_for('home'))
    profile = session.get('profile')
    user_logged_in = 'profile' in session
    return render_template('profile.html', profile=profile, user_logged_in=user_logged_in)

@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('index.html')

if __name__ == "__main__":

    arguments = argparse.ArgumentParser()
    arguments.add_argument('--port', type=int, default=5000, help='port of execution')
    args = arguments.parse_args()

    serve(
            app, 
            host="127.0.0.1", 
            port=args.port
        )