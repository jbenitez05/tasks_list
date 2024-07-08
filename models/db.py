# -*- coding: utf-8 -*-

from config import parameters
from pydal import Field
from pydal.validators import IS_EMAIL
import datetime

db = parameters.db

db.define_table('auth_user',
                Field('first_name'),
                Field('last_name'),
                Field('email','string',requires=IS_EMAIL()),
                Field('created_on','datetime',default=datetime.datetime.now()),
                )