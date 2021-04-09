from flask import jsonify, make_response
from flask_login import current_user, login_required
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.posts import Post
from data.users import User


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_posts_not_found(user_id):
    session = db_session.create_session()
    posts = session.query(Post).filter(Post.user_id == user_id)
    if not posts:
        abort(404, message=f"Posts for user {user_id} not found")


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    if not post:
        abort(404, message=f"Posts {post} not found")


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        if current_user.id != post.user.id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)
        return make_response(jsonify({
            'posts': post.to_dict(only=('id', 'text', 'created_date', 'user_id'))

        }), 200)

    @login_required
    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        if current_user.id != post.user.id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)
        session.delete(post)
        session.commit()
        return make_response(jsonify({'success': 'OK'}), 200)


parser = reqparse.RequestParser()
parser.add_argument('text', required=True)


class PostListResource(Resource):
    @login_required
    def get(self, user_id):
        if current_user.id != user_id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)
        abort_if_user_posts_not_found(user_id)
        session = db_session.create_session()
        posts = session.query(Post).filter(Post.user_id == user_id)
        return make_response(jsonify({
            'user': user_id,
            'posts': [item.to_dict(only=('id', 'text', 'created_date')) for item in posts]

        }), 200)

    @login_required
    def post(self, user_id):
        if current_user.id != user_id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(
            text=args['text'],
            user_id=user_id,
        )
        session.add(post)
        session.commit()
        return make_response(jsonify({'success': 'OK',
                        'post': {'id': post.id, 'author': f'{post.user.name} {post.user.surname}'}}), 200)


class FriendsResource(Resource):
    @login_required
    def post(self, user_id, friend_id):
        if current_user.id != user_id and current_user.id != friend_id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)

        abort_if_user_not_found(user_id)
        abort_if_user_not_found(friend_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)
        friend = session.query(User).get(friend_id)

        if friend not in user.friends:
            user.become_friends(friend)
            session.commit()
            return make_response(jsonify({'success': 'OK'}), 200)
        else:
            return make_response(jsonify({'error': 'users are already friends'}), 400)

    @login_required
    def delete(self, user_id, friend_id):
        if current_user.id != user_id and current_user.id != friend_id:
            return make_response(jsonify({'error': 'method is not allowed for this account'}), 400)

        abort_if_user_not_found(user_id)
        abort_if_user_not_found(friend_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)
        friend = session.query(User).get(friend_id)

        if friend not in user.friends:
            return make_response(jsonify({'error': 'users are not friends'}), 400)
        else:
            user.delete_friend(friend)
            session.commit()
            return make_response(jsonify({'success': 'OK'}), 200)
