import datetime
import os
from pprint import pprint

from flask import Flask, session, request, redirect, render_template, abort
import spotipy
import uuid

from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class

import music
import rest_api
import weather
from data import db_session

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session

from data.posts import Post
from data.users import User
from forms.contacts import ContactInformation
from forms.personal_info import PersonalInformation
from forms.post import CreatePost
from forms.privacy_settings import PrivacySettingsForm
from forms.profile_settings import AccountSetting, SocialMedia, ChangePassword
from forms.search import SearchForm
from forms.upload import photos, UploadPhoto
from forms.user import RegisterUser, LoginUser

from PIL import Image

from flask_jwt_simple import JWTManager

from utils.spotify import spotify_login_required, SCOPE, get_followed_artists, get_all_artist_tracks

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SECRET_KEY'] = 'spotify_project_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/uploaded_photos')
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)

configure_uploads(app, photos)
patch_request_class(app)

api = Api(app)
post_resource = rest_api.PostResource()
post_list_resource = rest_api.PostListResource()


def crop_center(pil_img, crop_width: int, crop_height: int) -> Image:
    """
    Функция для обрезки изображения по центру.
    """
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
@app.route('/news')
@login_required
@spotify_login_required
def index(spotify: spotipy.Spotify):
    db_sess = db_session.create_session()

    # return redirect('/profile')

    params = {
        'spotify': spotify,
        'current_user': db_sess.query(User).get(current_user.id),
        'new_releases': []
    }

    artists = sorted(get_followed_artists(spotify), key=lambda x: x['popularity'], reverse=True)

    params['followed_artists'] = artists[:4]
    for artist in artists:
        tracks = get_all_artist_tracks(artist['id'], spotify)


        albums = list(filter(
            lambda x: x['release_date'] == datetime.datetime.today().strftime('%Y-%m-%d'),
            tracks['albums']))
        singles = list(filter(
            lambda x: x['release_date'] == datetime.datetime.today().strftime('%Y-%m-%d'),
            tracks['singles']))

        for i in albums:
            i['artist_image'] = artist['images'][0]['url']
        for i in singles:
            i['artist_image'] = artist['images'][0]['url']

        params['new_releases'] += albums
        params['new_releases'] += singles


    return render_template('newsfeed.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/profile')
    db_sess = db_session.create_session()

    form = RegisterUser()

    if form.validate_on_submit():
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    params = {
        'current_user': db_sess.query(User).get(current_user.id)
    }

    return render_template('register.html', form=form, **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')
    db_sess = db_session.create_session()
    form = LoginUser()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    params = {
        'current_user': db_sess.query(User).get(current_user.id)
    }

    return render_template('login.html', form=form, **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)

    posts = list(db_sess.query(Post).filter(Post.user_id == user.id))

    params = {
        'current_user': user,
    }

    return render_template('profile.html', posts=posts, **params)


@app.route('/id<id>')
@login_required
def user(id, ):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    posts = db_sess.query(Post).filter(Post.user_id == user.id)

    curr_user = db_sess.query(User).get(current_user.id)

    params = {
        'current_user': curr_user,
    }

    return render_template('user.html', user=user, posts=list(posts), **params)


@app.route('/friends')
@login_required
def friends():
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
    }

    return render_template('friends.html', **params)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    db_sess = db_session.create_session()

    params = {'current_user': db_sess.query(User).get(current_user.id),
              'messages': {}}

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    personal_info = PersonalInformation()
    params['form'] = personal_info

    if personal_info.validate_on_submit():

        user.name = personal_info.name.data
        user.surname = personal_info.surname.data
        user.gender = personal_info.gender.data
        user.age = personal_info.age.data
        user.marital_status = personal_info.marital_status.data
        user.city = personal_info.city.data
        user.address = personal_info.address.data

        if personal_info.photo.data:
            filename = photos.save(personal_info.photo.data)
            file_url = photos.url(filename)

            os.chdir('static')
            os.chdir('uploaded_photos')

            fname = f'id{current_user.id}_avatar.jpg'

            if os.path.exists(fname):
                os.remove(fname)
            os.rename(filename, fname)

            crop_max_square(Image.open(fname)).save(fname)

            os.chdir('..')
            os.chdir('..')

            user.avatar = f'/static/uploaded_photos/{fname}'

    change_password = ChangePassword()
    params['change_password'] = change_password

    if change_password.validate_on_submit():
        if user.check_password(
                change_password.old_pass.data) and change_password.new_pass.data == change_password.new_pass_again.data:
            user.set_password(change_password.new_pass.data)
            db_sess.commit()
            return redirect('/logout')
        if not user.check_password(change_password.old_pass.data):
            params['messages']['old_pass'] = 'Wrong old password'
        if not change_password.new_pass.data == change_password.new_pass_again.data:
            params['messages']['new_pass_again'] = 'New passwords do not match'

    contact_info = ContactInformation()
    params['contact_info'] = contact_info
    if contact_info.validate_on_submit():
        if contact_info.email.data == current_user.email and contact_info.new_email.data == contact_info.new_email_again.data:
            if contact_info.new_email.data:
                user.email = contact_info.new_email_again.data
        if contact_info.email.data != current_user.email:
            params['messages']['email'] = 'Wrong old Email'
        if contact_info.new_email.data != contact_info.new_email_again.data:
            params['messages']['new_email_again'] = 'New Emails do not match'

        if contact_info.phone.data:
            user.phone = contact_info.phone.data
        if contact_info.url:
            user.url = contact_info.url.data

        if contact_info.vk.data:
            user.vk = contact_info.vk.data
        user.show_vk = contact_info.show_vk.data

        if contact_info.facebook.data:
            user.facebook = contact_info.facebook.data
        user.show_facebook = contact_info.show_facebook.data

        if contact_info.twitter.data:
            user.twitter = contact_info.twitter.data
        user.show_twitter = contact_info.show_twitter.data

        if contact_info.instagram.data:
            user.instagram = contact_info.instagram.data
        user.show_instagram = contact_info.show_instagram.data

        if contact_info.youtube.data:
            user.youtube = contact_info.youtube.data
        user.show_youtube = contact_info.show_youtube.data

    db_sess.commit()

    return render_template('edit_profile.html', **params)


@app.route('/profile/privacy')
@login_required
def privacy_settings():
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
    }

    return render_template('comingsoon.html', **params)


@app.route('/messages')
@login_required
def messages():
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id)
    }

    return render_template('chat.html', **params)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect('/login')


@app.route('/test')
@login_required
def test():
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
    }

    return render_template('test_page.html', **params)


if __name__ == '__main__':
    db_session.global_init("db/database.db")

    app.register_blueprint(music.blueprint)
    app.register_blueprint(weather.blueprint)

    api.add_resource(rest_api.PostListResource, '/api/posts/<int:user_id>')
    api.add_resource(rest_api.PostResource, '/api/post/<int:post_id>')
    api.add_resource(rest_api.FriendsResource, '/api/friends/<int:user_id>/<int:friend_id>')

    app.run(threaded=True, port=8080, debug=True)
