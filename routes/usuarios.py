from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from flask_bcrypt import Bcrypt

from config.db import get_db_connection

import os 
from dotenv import load_dotenv

#Cargamos las variables de entorno 
load_dotenv()

#Creamos el blueprint
usuarios_bp = Blueprint ('usuarios', __name__)

#Inicializamos a Bcrypt
bcrypt = Bcrypt()

@usuarios_bp.route('registrar', methods = ['POST']) # Es post porque se pasa por el body
def registar():
    #Obtener los datos desde el body
    data = request.get_json()

    nombre = data.get('nombre') 
    email = data.get('email') 
    password = data.get('password') 

    #Validacion 
    if not nombre or not email or not password:
        return jsonify({"error":"Faltan datos"}), 400

    #Obtener el cursor de la BD
    cursor = get_db_connection()

    try: 
        #Verificsr que el ususario no exista
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email, ))
        existing_user = cursor.fetchone()

        if existing_user: 
            return jsonify({"error":"Ese usuario ya existe"}), 400
        
        #Hacer el hash al password 
        hashed_passwd = bcrypt.generate_password_hash(password).decode('utf-8') #Aqui ya hace el proceso de sal y pimienta

        #Insertar el registor del nuevo usuario en la BD
        cursor.execute('''INSERT INTO usuarios (nombre, email, password) values (%s, %s, %s)''', (nombre, email, hashed_passwd))
        
        #Guardamos el nuevo registro
        cursor.connection.commit() 

        return jsonify({"mensaje":"Usuario creado"}), 201
    except Exception as e:
        return jsonify({"error":f"Error al registrar al usuario: {str(e)}"}), 500
    finally:        
        #Cerramos el cursor 
        cursor.close()

@usuarios_bp.route('/login', methods = ['POST'])
def login (): 
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    #Validar 
    if not email or not password: 
        return jsonify({"Error":"Faltan datos"}), 400
    
    cursor = get_db_connection()

    cursor.execute("SELECT password, email")