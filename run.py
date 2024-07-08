# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db
from config import parameters, nav_menu
import datetime

app = Flask(__name__)

# Configuración
app.config['JWT_SECRET_KEY'] = parameters.secret_key
jwt = JWTManager(app)

@app.context_processor
def inject_vars():
    year = datetime.datetime.now().year
    menu = nav_menu.nav_routes
    return dict(year=year,menu=menu)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400
    
    #if User.query.filter_by(username=username).first():
    #    return jsonify({"msg": "Username already exists"}), 400
    
    new_user = "" #User(username=username, password=generate_password_hash(password))
    #db.session.add(new_user)
    #db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    user = "" #User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)