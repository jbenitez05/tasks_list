# -*- coding: utf-8 -*-

import datetime
import random
import string
from ..models.db import db

class Populate:
    
    def __init__(self) -> None:
        pass

    def generate_random_string(self,length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def populate_auth_user_table(self, num_records=20):
        for _ in range(num_records):
            db.auth_user.validate_and_insert(
                github_id=self.generate_random_string(10),
                google_id=self.generate_random_string(10),
                username=self.generate_random_string(8),
                name=self.generate_random_string(12),
                email=f'{self.generate_random_string(5)}@example.com',
                created_on=datetime.datetime.now()
            )
        db.commit()
