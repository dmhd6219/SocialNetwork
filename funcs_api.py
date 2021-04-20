import flask
from flask_login import login_required, current_user
from data import db_session
import random
import utils
from data.users import User
from flask import jsonify, make_response

blueprint = flask.Blueprint(
    'funcs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/anecs/get')
@login_required
def get_anec():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)

    name, surname = user.name, user.surname
    city = 'Москва'
    if user.city:
        city = user.city

    anec = random.choice(utils.some.anecs)

    return jsonify({'anecdote': anec.replace('{city}', city).replace('{name}', name).replace('{surname}', surname)})
