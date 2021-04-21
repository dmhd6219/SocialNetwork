import sqlalchemy

from data.db_session import SqlAlchemyBase

chats_to_users = sqlalchemy.Table(
    'chats_to_users',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('chats', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chats.id')),
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
)


class Chat(SqlAlchemyBase):
    __tablename__ = 'chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
