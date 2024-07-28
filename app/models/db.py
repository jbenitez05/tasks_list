# -*- coding: utf-8 -*-

from config import parameters
from pydal import Field
from pydal.validators import IS_EMAIL, IS_NOT_EMPTY, IS_DATE_IN_RANGE, IS_IN_DB
import datetime

db = parameters.db

db.define_table('auth_user',
                Field('github_id', unique=True),
                Field('google_id'),
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
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                )

minimun = datetime.date.today()
db.define_table('tasks',
                Field('project',    'reference projects'),
                Field('name',       'string',   requires=IS_NOT_EMPTY()         ),
                Field('description','text',     requires=IS_NOT_EMPTY()         ),
                Field('finish_date','date',     requires=IS_DATE_IN_RANGE(minimum=minimun)     ),
                Field('is_complete','boolean',  requires=IS_NOT_EMPTY()         ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                Field('is_active',  'boolean',  default=True                    ),
                Field('created_by', 'reference auth_user'),
                Field('assigned_to', 'list:reference auth_user')
                )