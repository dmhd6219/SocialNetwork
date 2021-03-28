from flask import jsonify
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
        return jsonify({
            'posts': post.to_dict(only=('id', 'text', 'created_date', 'user_id'))

        })

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('text', required=True)


class PostListResource(Resource):
    def get(self, user_id):
        abort_if_user_posts_not_found(user_id)
        session = db_session.create_session()
        posts = session.query(Post).filter(Post.user_id == user_id)
        return jsonify({
            'user': user_id,
            'posts': [item.to_dict(only=('id', 'text', 'created_date')) for item in posts]

        })

    def post(self, user_id):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(
            text=args['text'],
            user_id=user_id,
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})


class FriendsResource(Resource):
    def post(self, user_id, friend_id):
        abort_if_user_not_found(user_id)
        abort_if_user_not_found(friend_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)
        friend = session.query(User).get(friend_id)

        if friend not in user.friends:
            user.become_friends(friend)
            session.commit()
            return jsonify({'success': 'OK'})
        else:
            return jsonify({'error': 'users are already friends'})

    def delete(self, user_id, friend_id):
        abort_if_user_not_found(user_id)
        abort_if_user_not_found(friend_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)
        friend = session.query(User).get(friend_id)

        if friend not in user.friends:
            return jsonify({'error': 'users are not friends'})
        else:
            user.delete_friend(friend)
            session.commit()
            return jsonify({'success': 'OK'})