# -*- coding: utf-8 -*-

from config import parameters
from pydal import Field
from pydal.validators import IS_EMAIL, IS_NOT_EMPTY, IS_DATE_IN_RANGE
import datetime

db = parameters.db

db.define_table('auth_user',
                Field('github_id', unique=True),
                Field('username',   'string',   requires=IS_NOT_EMPTY()         ),
                Field('name',       'string',   requires=IS_NOT_EMPTY()         ),
                Field('email',      'string',   requires=IS_EMAIL()             ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
            )

minimun = datetime.date.today()

db.define_table('tasks',
                Field('name',       'string',   requires=IS_NOT_EMPTY()         ),
                Field('description','text',     requires=IS_NOT_EMPTY()         ),
                Field('finish_date','date',     requires=IS_DATE_IN_RANGE(minimum=minimun)     ),
                Field('is_complete','boolean',  requires=IS_NOT_EMPTY()         ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                Field('is_active',  'boolean',  default=True                    ),
                Field('created_by', 'reference auth_user')
                )