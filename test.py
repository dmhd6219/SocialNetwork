import requests

from data import db_session
from data.users import User

db_session.global_init("db/database.db")

db_sess = db_session.create_session()

user1 = db_sess.query(User).get(1)
user2 = db_sess.query(User).get(2)

print(user2 in user1.friends)
user1.become_friends(user2)
print(user2 in user1.friends)
# they are friends now
print(requests.delete('http://127.0.0.1:8080/api/friends/1/2').json())
print(user2 in user1.friends)
# а после перезапуска они снова не друзья:(
