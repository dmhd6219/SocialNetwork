import os
from pprint import pprint

from flask import Flask, session, request, redirect, render_template, abort
import spotipy
import uuid

from flask_uploads import configure_uploads, patch_request_class

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

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

SCOPE = 'user-top-read user-read-playback-position user-read-private user-read-email playlist-read-private user-library-read user-library-modify playlist-read-collaborative playlist-modify-public playlist-modify-private ugc-image-upload user-follow-read user-follow-modify user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played'

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


def session_cache_path():
    return caches_folder + session.get('uuid')


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


@app.route('/music', methods=['GET', 'POST'])
@login_required
def music():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/music')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f'/music/search/{search_form.data.data}')

    return render_template('music.html', spotify=spotify, search_form=search_form)


@app.route('/music/search/<data>')
def search_music(data):
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(f'/artist/{id}')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {
        'artists': spotify.search(q=data, type='artist', limit=6)['artists']['items'],
        'albums': spotify.search(q=data, type='album', limit=6)['albums']['items'],
        'tracks': spotify.search(q=data, type='track', limit=6)['tracks']['items']
    }

    pprint(params['albums'])

    return render_template('search.html', spotify=spotify, **params)


@app.route('/artist/<id>')
def artist(id):
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(f'/artist/{id}')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    try:
        params['artist'] = spotify.artist(id)
        params['top_tracks'] = spotify.artist_top_tracks(id)['tracks'][:6:]
        params['albums'] = spotify.artist_albums(id, album_type='album')['items'][:7:]
        params['singles'] = spotify.artist_albums(id, album_type='single')['items'][:7:]
        params['appears_on'] = spotify.artist_albums(id, album_type='appears_on')['items'][:7:]
    except:
        return abort(404)

    return render_template('artist.html', spotify=spotify, **params)


@app.route('/playlist/<id>')
@login_required
def playlist(id):
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(f'/artist/{id}')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    # id = 2duj5GBXwLRdjqV9hjXy4o

    try:
        params['playlist'] = spotify.playlist(id)
        dur = 0
        for track in params['playlist']['tracks']['items']:
            dur += float(track['track']['duration_ms']) / 1000 / 60
        params['duration'] = round(dur, 2)
    except:
        return abort(404)

    pprint(params['playlist']['tracks']['items'])

    return render_template('playlist.html', spotify=spotify, **params)


@app.route('/track/<id>')
@login_required
def track(id):
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(f'/track/{id}')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    # id = 77yYxfpXB64ktXPVdU9xcF

    try:
        params['music'] = spotify.track(id)
        params['playlist'] = spotify.album(params['music']['album']['id'])
        dur = 0
        for track in params['playlist']['tracks']['items']:
            dur += float(track['duration_ms']) / 1000 / 60
        params['duration'] = round(dur, 2)
    except:
        return abort(404)

    pprint(params['music'])

    return render_template('track.html', spotify=spotify, **params)


@app.route('/album/<id>')
@login_required
def album(id):
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(f'/album/{id}')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    # id = 1zpglRcWM6VnMkpsFkHIdt

    try:
        params['playlist'] = spotify.album(id)
        dur = 0
        for track in params['playlist']['tracks']['items']:
            dur += float(track['duration_ms']) / 1000 / 60
        params['duration'] = round(dur, 2)
    except:
        return abort(404)

    return render_template('album.html', spotify=spotify, **params)


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


@app.route('/spotify_sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def get_current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect('/login')


if __name__ == '__main__':
    db_session.global_init("db/database.db")
    app.run(threaded=True, port=8080, debug=True)
