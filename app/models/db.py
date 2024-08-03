# -*- coding: utf-8 -*-

"""
Define las tablas de la base de datos para la aplicación.

Esta sección define las tablas necesarias para la aplicación usando `pydal`. Se crean las tablas `auth_user`, `projects` y `tasks`, 
con los campos y validaciones correspondientes. 

- `auth_user`: Almacena la información del usuario con campos para IDs de OAuth, nombre, email y fecha de creación.
- `projects`: Almacena información sobre proyectos, incluyendo nombre, descripción, miembros, y el usuario que creó el proyecto.
- `tasks`: Almacena información sobre tareas, incluyendo referencia al proyecto, nombre, descripción, fecha de finalización, estado de completado, y usuarios asignados.

Cada tabla incluye campos para la fecha de creación y un campo booleano `is_active` para gestionar la activación o desactivación lógica de los registros.
"""

from config import parameters
from pydal import Field
from pydal.validators import IS_EMAIL, IS_NOT_EMPTY, IS_DATE_IN_RANGE, IS_IN_DB, IS_IN_SET
import datetime

db = parameters.db

db.define_table('auth_user',
                Field('github_id',  'string'                                    ),
                Field('google_id'   'string'                                    ),
                Field('username',   'string',   requires=IS_NOT_EMPTY()         ),
                Field('name',       'string',   requires=IS_NOT_EMPTY()         ),
                Field('email',      'string',   requires=IS_EMAIL()             ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
            )

db.define_table('projects',
                Field('name',           'string',unique=True,       requires=IS_NOT_EMPTY() ),
                Field('description',    'text',                     requires=IS_NOT_EMPTY() ),
                Field('members',        'list:reference auth_user'                          ),
                Field('is_active',      'boolean',                  default=True            ),
                Field('created_by',     'reference auth_user'                               ),
                Field('created_on', 'datetime', default=datetime.datetime.now()             ),
                )

minimun = datetime.date.today()
status = {
        "0": "Reserva",
        "1": "Preparado",
        "2": "En progreso",
        "3": "Hecho"
    }
db.define_table('tasks',
                Field('project',    'reference projects'),
                Field('name',       'string',   requires=IS_NOT_EMPTY()         ),
                Field('color',      'string',   default="#F0B518"               ),
                Field('status',     'string',   requires=IS_IN_SET(status)      ),
                Field('description','text',     requires=IS_NOT_EMPTY()         ),
                Field('finish_date','date',     requires=IS_DATE_IN_RANGE(minimum=minimun)     ),
                Field('is_complete','boolean',  requires=IS_NOT_EMPTY()         ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                Field('is_active',  'boolean',  default=True                    ),
                Field('created_by', 'reference auth_user'                       ),
                Field('assigned_to','list:reference auth_user'                  )
                )

db.define_table('colors',
                Field('task','reference tasks'),
                Field('color'),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                )