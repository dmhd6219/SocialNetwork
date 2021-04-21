import datetime
import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase
from .users import User

chats = sqlalchemy.Table(
    'chats', SqlAlchemyBase.metadata,
    sqlalchemy.Column('user1_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'),
                      ),
    sqlalchemy.Column('user2_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.UniqueConstraint('user1_id', 'user2_id', name='unique_dialogs'))


class Chat(SqlAlchemyBase):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    users = orm.relationship('User',
                             secondary=chats,
                             primaryjoin=id == chats.c.user1_id,
                             secondaryjoin=id == chats.c.user2_id)
