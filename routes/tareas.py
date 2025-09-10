from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
#Creando el blueprint 
tareas_bp = Blueprint('tareas', __name__)

#Creando un endpoint para obtener las tareas
@tareas_bp.route('/obtener', methods=['GET'])
@jwt_required() 
def get():

    #Obtenemos la identidad del dueño del token  
    current_user = get_jwt_identity()

    #Conectarse a la DB
    cursor = get_db_connection()

    #Ejecutar la funcion 
    query = '''SELECT a.id_usuario, a.descripcion, b.nombre, b.email, a.creado_en 
    FROM tareas as a
    INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
    WHERE a.id_usuario = %s
    '''
    cursor.execute(query, (current_user, ))
    lista = cursor.fetchall()

    cursor.close()
    if not lista: 
        return jsonify({"Error":"El usuario no tiene tareas"}), 404
    else: 
        return jsonify({"lista":lista}), 200

#Endpoint para recibir datos desde el body 
@tareas_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear():

    #Obtener la identidad del dueño del token 
    current_user = get_jwt_identity()

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
        cursor.execute('INSERT INTO tareas (descripcion, id_usuario) values (%s, %s)', (descripcion, current_user))
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
@tareas_bp.route('/modificar/<int:id_tarea>', methods=['PUT'])
@jwt_required()
def modificar (id_tarea): 

    #Obtener la identidsad del dueño de la tarea 
    current_user = get_jwt_identity()

    #Obtenemos los datos del body 
    data = request.get_json()

    descripcion = data.get('descripcion')

    cursor = get_db_connection()

    #Verificmos que la tarea existe 
    query = "SELECT*FROM tareas WHERE id_tarea = %s"
    cursor.execute (query, (id_tarea, ))

    tarea = cursor.fetchone()

    if not tarea: 
        cursor.close()
        return jsonify({"Error":"Tarea no encontrada"}), 404
    
    #Verificamos que la tarea pertenece al usuario logeado
    if not tarea[1] == int(current_user): 
        cursor.close()
        return jsonify({"Error":"Credenciales incorrectas"}), 401
    
    #Actualizar los datos 
    try: 
        cursor.execute("UPDATE tareas SET descripcion = %s WHERE id_tarea = %s", (descripcion, id_tarea))
        cursor.connection.commit() #Para guardar los cambios
        return jsonify({"mensaje":"Datos actualizados correctamente"}), 200
    except Exception as e: 
        return jsonify({"Error":f"Error al actualizar los datos: {str(e)}"})
    finally: 
        cursor.close()



#Creando endpoint para 
