from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import Bcrypt
import datetime 

from config.db import get_db_connection

import os 
from dotenv import load_dotenv

'''
El JWT calcula el hash de la contraseña del usuario. Es una llave para acceder a algun recurso o sitio.

En el token ya está el ID del usuario 
'''

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

    #Validar de que si no tenogo email o psswd que faltan datos
    if not email or not password: 
        return jsonify({"Error":"Faltan datos"}), 400
    
    cursor = get_db_connection()

    query = "SELECT password, email, id_usuario FROM usuarios WHERE email = %s"
    cursor.execute(query, (email, ))

    usuario = cursor.fetchone() #Esto guardara los datos del usuario que se encontro 

    #bcrypt.check_password_hash: Compara el passwd en la BD contra mi passswd. Es 0 porque es el primer param de la consulta
    if usuario and bcrypt.check_password_hash(usuario [0], password):

        #Generamos el JWT, con su respectiva caducidad
        expires = datetime.timedelta(minutes = 60)

        '''
        El primer parametro es la identidad del usuario (Subject (sub)) o ID, iat (issue at) que se refiere a la 
        fecha
        '''
        access_token = create_access_token(identity=str(usuario[2]), expires_delta = expires) #[1] es la passwd del usuario

        cursor.close()

        return jsonify({"Token":access_token}), 200
    else:
        return jsonify({"Error":"Credenciales incorrectas"}), 401

#Pedirle datos del usuario 
@usuarios_bp.route('/datos', methods = ['GET'])
@jwt_required() #Este decorador asegura este endpoint 
def datos ():

    #Obtenemos el token
    current_user = get_jwt_identity() #Este es el subject (sub), id del usuario

    #Nos conectamos a la BD
    cursor = get_db_connection()

    query = "SELECT id_usuario, nombre, email FROM usuarios WHERE id_usuario = %s"
    cursor.execute(query, (current_user, ))
    usuario = cursor.fetchone()

    cursor.close()

    if usuario: 
        user_info = {
            "id_usuario":usuario[0],
            "nombre":usuario[1], 
            "email":usuario[2] 
        }
        return jsonify({"Datos":user_info}), 200
    else: 
        return jsonify({"Error":"Usuario no encontrado"}), 404