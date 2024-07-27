# -*- coding: utf-8 -*-
    
import argparse
from waitress import serve
from app import create_app
import datetime
from config import nav_menu

app = create_app()

@app.context_processor
def inject_vars():
    year = datetime.datetime.now().year
    menu = nav_menu.nav_routes    
    return dict(year=year,menu=menu)

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--port', type=int, default=5000, help='port of execution')
    args = arguments.parse_args()

    serve(app, host="127.0.0.1", port=args.port)