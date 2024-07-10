# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session
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

@app.route('/home')
def home():
    return render_template('index.html')

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