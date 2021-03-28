import requests

from data import db_session
from data.users import User

print(requests.post('http://127.0.0.1:8080/api/friends/1/2').json())
db_sess = db_session.create_session()
print(len(db_sess.query(User).get(1).friends))