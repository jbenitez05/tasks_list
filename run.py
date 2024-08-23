# -*- coding: utf-8 -*-

"""
Configura y ejecuta la aplicación Flask usando Waitress.

Este script crea una instancia de la aplicación Flask, inyecta variables globales en el contexto de la plantilla, 
y configura la ejecución del servidor utilizando Waitress. Permite especificar el puerto de ejecución a través de argumentos de línea de comandos.

- `inject_vars`: Función de contexto que inyecta el año actual y el menú de navegación en el contexto de las plantillas.
- `serve`: Inicia el servidor Waitress para ejecutar la aplicación Flask.

Args:
    --port (int): El puerto en el que se ejecutará la aplicación. El valor por defecto es 5000.
"""

import argparse
from waitress import serve
from app import create_app
import datetime
from config import nav_menu
from flask import request

app = create_app()

@app.context_processor
def inject_vars():
    year = datetime.datetime.now().year
    menu = nav_menu.nav_routes
    user_agent = request.headers.get('User-Agent')
    
    if 'Mobile' in user_agent:
        device_type = 'mobile'
    else:
        device_type = 'desktop' 
    return dict(year=year,menu=menu,device_type=device_type)

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--port', type=int, default=5000, help='port of execution')
    args = arguments.parse_args()

    serve(app, host="127.0.0.1", port=args.port)