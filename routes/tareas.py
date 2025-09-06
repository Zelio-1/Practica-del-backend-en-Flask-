from flask import Blueprint, request, jsonify
from config.db import get_db_connection

#Creando el blueprint 
tareas_bp = Blueprint('tareas', __name__)

#Creando un endpoint para obtener las tareas
@tareas_bp.route('/obtener', methods=['GET'])
def get():
    return jsonify({"mensaje": "Estas son tus tareas"})

#Endpoint para recibir datos desde el body 
@tareas_bp.route('/crear', methods=['POST'])
def crear():
    #Obtener lso datos del body. En el objeto data se recibe todo lo que sea JSON
    data = request.get_json()

    #Este GET es distinto del verbo anterior
    descripcion = data.get('descripcion')
    #apellido = data.get('apellido')

    if not descripcion: 
        return jsonify({"error":"Debes teclear una descripcion"}), 400
    #Si todo bien, obtenemos el cursor
    cursor = get_db_connection()

    #Se realiza la insercion. %s evita la SQL injection. El segundo param es lo que quiero consultar
    try: 
        cursor.execute('INSERT INTO tareas (descripcion) values (%s)', (descripcion,))
        cursor.connection.commit()
        return jsonify({"mensaje":"Tarea creada"}), 201
    except Exception as e: 
        return jsonify({"Error":f"No se logro crear la tarea: {str(e)}"}) 
    finally: 
        #Se cierra el cursor
        cursor.close() 

    #return jsonify({"saludo":f"Hola {nombre} {apellido} como estas"})

'''
Creando un endpoint usando PUT y pasando datos por el body y la URl. 
Esto recibe dps cosas: user_id y el request_json()
'''
@tareas_bp.route('/modificar/<int:user_id>', methods=['PUT'])
def modificar (user_id): 
    #Obtenemos los datos del body 
    data = request.get_json()

    nombre = data.get('nombre')
    apellido = data.get('apellido')

    mensaje = f"Usuario con id: {user_id} y nombre: {nombre} {apellido}"
    return jsonify({"saludo": mensaje})

#Creando endpoint para 
