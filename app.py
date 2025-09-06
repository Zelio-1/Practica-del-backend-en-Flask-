from flask import Flask 
import os #Importa en el SO donde estarana las .env (variables de entorno) 
from dotenv import load_dotenv 
from routes.tareas import tareas_bp
from routes.usuarios import usuarios_bp
from config.db import init_db, mysql

#Cargar las variables de entorno 
load_dotenv()

#Funcion para crear la app 
def create_app():
    
    #Instrancia de la app
    app = Flask(__name__)

    #Configurar la BD
    init_db(app) #Arranca la basen de datos con flask

    #Registrar el blueprint
    app.register_blueprint (tareas_bp, url_prefix = '/tareas')
    app.register_blueprint(usuarios_bp, url_prefix = '/usuarios')

    return app

#Crear app 
app = create_app()

#Iniciar el programa
if __name__ == "__main__":

    #Obtenemos el puerto. Esto es por medio de las variables de entorno
    port = int(os.getenv("PORT", 8080 ))#8080 en caso de que el PORT no tenga valor

    
    '''
    Corremos la app.El primer parametro indica que acepta cualquier ip. 
    '''
    app.run(host = "0.0.0.0", port = port, debug = True)