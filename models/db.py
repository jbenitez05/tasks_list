# -*- coding: utf-8 -*-

from config import parameters
from pydal import Field
from pydal.validators import IS_EMAIL, IS_NOT_EMPTY
import datetime

db = parameters.db

db.define_table('auth_user',
                Field('first_name', 'string',   requires=IS_NOT_EMPTY()         ),
                Field('last_name',  'string',   requires=IS_NOT_EMPTY()         ),
                Field('email',      'string',   requires=IS_EMAIL()             ),
                Field('password',   'string',   requires=IS_NOT_EMPTY()         ),
                Field('created_on', 'datetime', default=datetime.datetime.now() ),
                )