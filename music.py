import os
import uuid
from pprint import pprint

import flask
import spotipy
from flask import session, request, redirect, render_template, abort
from flask_login import login_required

from forms.search import SearchForm

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

SCOPE = 'user-top-read user-read-playback-position user-read-private user-read-email ' \
        'playlist-read-private user-library-read user-library-modify playlist-read-collaborative ' \
        'playlist-modify-public playlist-modify-private ugc-image-upload user-follow-read ' \
        'user-follow-modify user-read-playback-state user-modify-playback-state ' \
        'user-read-currently-playing user-read-recently-played'


def session_cache_path():
    return caches_folder + session.get('uuid')


blueprint = flask.Blueprint(
    'music',
    __name__,
    template_folder='templates'
)


@blueprint.route('/music', methods=['GET', 'POST'])
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
        print(request.args.get("code"))
        return redirect('/music')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f'/music/search/{search_form.data.data}')

    return render_template('music.html', spotify=spotify, search_form=search_form)


@blueprint.route('/music/search/<data>')
@login_required
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
        return redirect(f'/music/search/{data}')

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

    return render_template('search.html', spotify=spotify, **params)


@blueprint.route('/music/artist/<id>')
@login_required
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
        return redirect(f'music/artist/{id}')

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
        params['albums'] = spotify.artist_albums(id, album_type='album', limit=7)['items']
        params['singles'] = spotify.artist_albums(id, album_type='single', limit=7)['items']
        params['appears_on'] = spotify.artist_albums(id, album_type='appears_on', limit=7)['items']
    except:
        return abort(404)

    return render_template('artist.html', spotify=spotify, **params)


@blueprint.route('/music/artist/<id>/albums')
@login_required
def artist_albums(id):
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
        return redirect(f'music/artist/{id}/albums')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    try:
        params['artist'] = spotify.artist(id)
        params['albums'] = spotify.artist_albums(id, album_type='album', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_albums.html', spotify=spotify, **params)


@blueprint.route('/music/artist/<id>/singles')
@login_required
def artist_singles(id):
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
        return redirect(f'music/artist/{id}/singles')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    try:
        params['artist'] = spotify.artist(id)
        params['singles'] = spotify.artist_albums(id, album_type='single', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_singles.html', spotify=spotify, **params)


@blueprint.route('/music/artist/<id>/appears_on')
@login_required
def artist_appears_on(id):
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
        return redirect(f'music/artist/{id}/appears_on')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {}

    try:
        params['artist'] = spotify.artist(id)
        params['appears_on'] = spotify.artist_albums(id, album_type='appears_on', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_appears_on.html', spotify=spotify, **params)


@blueprint.route('/music/playlist/<id>')
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
        return redirect(f'/music/playlist/{id}')

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
    except Exception:
        return abort(404)

    pprint(params['playlist']['tracks']['items'])

    return render_template('playlist.html', spotify=spotify, **params)


@blueprint.route('/music/track/<id>')
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
        return redirect(f'/music/track/{id}')

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


@blueprint.route('/music/album/<id>')
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
        return redirect(f'/music/album/{id}')

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


@blueprint.route('/music/new')
@login_required
def new_music():
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
        return redirect(f'/music/new')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {'new_music': spotify.new_releases('RU')}
    return render_template('new_music.html', **params)


@blueprint.route('/music/track/top')
@login_required
def top_tracks():
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
        return redirect(f'/music/track/top')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {'tracks': spotify.current_user_top_tracks(time_range='short_term')}

    return render_template('top_tracks.html', **params)


@blueprint.route('/music/artist/top')
@login_required
def top_artists():
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
        return redirect(f'/music/artist/top')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_manager.get_authorize_url())

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    params = {'artists': spotify.current_user_top_artists(time_range='short_term')}

    return render_template('top_artists.html', **params)


@blueprint.route('/spotify_sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@blueprint.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@blueprint.route('/currently_playing')
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


@blueprint.route('/current_user')
def get_current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()
