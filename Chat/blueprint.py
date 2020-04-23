from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from flask_whooshee import Whooshee
db = SQLAlchemy()
faker = Faker('zh-cn')
whooshee = Whooshee()