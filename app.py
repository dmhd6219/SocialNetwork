import os
from pprint import pprint

from flask import Flask, session, request, redirect, render_template, abort
import spotipy
import uuid

from flask_uploads import configure_uploads, patch_request_class

import music
from data import db_session

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.users import User
from forms.privacy_settings import PrivacySettingsForm
from forms.profile_settings import AccountSetting, SocialMedia, ChangePassword
from forms.search import SearchForm
from forms.upload import photos, UploadPhoto
from forms.user import RegisterUser, LoginUser

from PIL import Image

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'spotify_project_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/uploaded_photos')

login_manager = LoginManager()
login_manager.init_app(app)

configure_uploads(app, photos)
patch_request_class(app)


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
@login_required
def index():
    return redirect('/profile')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUser()

    if form.validate_on_submit():
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')
    form = LoginUser()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/id<id>')
@login_required
def user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()

    return render_template('user.html', user=user)


@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    account_setting = AccountSetting()

    social_media = SocialMedia()

    change_password = ChangePassword()

    upload_avatar = UploadPhoto()

    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if account_setting.validate_on_submit():
        if account_setting.name.data:
            user.name = account_setting.name.data

        if account_setting.surname.data:
            user.surname = account_setting.surname.data

        if account_setting.email.data == account_setting.email_again != '':
            user.email = account_setting.email.data

    if social_media.validate_on_submit():
        if social_media.vk.data:
            user.vk = social_media.vk.data
        user.show_vk = social_media.show_vk.data

        if social_media.facebook.data:
            user.facebook = social_media.facebook.data
        user.show_facebook = social_media.show_facebook.data

        if social_media.twitter.data:
            user.twitter = social_media.twitter.data
        user.show_twitter = social_media.show_twitter.data

        if social_media.instagram.data:
            user.instagram = social_media.instagram.data
        user.show_instagram = social_media.show_instagram.data

        if social_media.youtube.data:
            user.youtube = social_media.youtube.data
        user.show_youtube = social_media.show_youtube.data

    if change_password.validate_on_submit():
        if user.check_password(
                change_password.old_pass.data) and change_password.new_pass.data == change_password.new_pass_again.data:
            user.set_password(change_password.new_pass.data)
            db_sess.commit()
            return redirect('/logout')

    if upload_avatar.validate_on_submit():
        filename = photos.save(upload_avatar.photo.data)
        file_url = photos.url(filename)

        os.chdir('static')
        os.chdir('uploaded_photos')

        fname = f'{current_user.name.lower()}_{current_user.surname.lower()}_avatar.jpg'

        if os.path.exists(fname):
            os.remove(fname)
        os.rename(filename, fname)

        crop_max_square(Image.open(fname)).save(fname)

        os.chdir('..')
        os.chdir('..')

        user.avatar = f'/static/uploaded_photos/{fname}'

    db_sess.commit()

    return render_template('profile_settings.html', account_setting=account_setting,
                           social_media=social_media, change_password=change_password,
                           upload_avatar=upload_avatar)


@app.route('/profile/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    return render_template('comingsoon.html')

    privacy_settings = PrivacySettingsForm()
    if privacy_settings.validate_on_submit():
        # do magic and update db
        pass

    return render_template('privacy_settings.html', privacy_settings=privacy_settings)


@app.route('/weather')
@login_required
def weather():
    return render_template('weather.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect('/login')


if __name__ == '__main__':
    db_session.global_init("db/database.db")

    app.register_blueprint(music.blueprint)

    app.run(threaded=True, port=8080, debug=True)
