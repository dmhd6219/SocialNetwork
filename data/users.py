import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase



class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    closed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    show_email = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                               default='https://s.tcdn.co/bbb/f33/bbbf335b-46cd-4fc4-8bdd-12fc70e94089/10.png')

    bg = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                           default='/static/images/page-img/colors-bg.jpg')

    vk = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='https://vk.com/')
    show_vk = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    facebook = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='https://facebook.com/')
    show_facebook = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    twitter = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='https://twitter.com/')
    show_twitter = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    instagram = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                                  default='https://instagram.com/')
    show_instagram = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    youtube = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='https://youtube.com/')
    show_youtube = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    mobile_phone = sqlalchemy.Column(sqlalchemy.String, default='')
    show_mobile_phone = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    address = sqlalchemy.Column(sqlalchemy.String, default='')
    show_address = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    age = sqlalchemy.Column(sqlalchemy.String, default='')
    show_age = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    gender = sqlalchemy.Column(sqlalchemy.String, default='')
    show_gender = sqlalchemy.Column(sqlalchemy.Boolean, default=True)






    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
