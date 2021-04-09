import os
import uuid

import spotipy
from flask import session, request, redirect
from flask_login import current_user

from data import db_session
from data.users import User

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

SCOPE = 'user-top-read user-read-playback-position user-read-private user-read-email ' \
        'playlist-read-private user-library-read user-library-modify playlist-read-collaborative ' \
        'playlist-modify-public playlist-modify-private ugc-image-upload user-follow-read ' \
        'user-follow-modify user-read-playback-state user-modify-playback-state ' \
        'user-read-currently-playing user-read-recently-played streaming'


def session_cache_path():
    return caches_folder + session.get('uuid')


def spotify_login_required(func):
    def wrapper(**kwargs):
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(
            scope=SCOPE,
            cache_handler=cache_handler,
            show_dialog=True)

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)

        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            token = request.args.get("code")
            auth_manager.get_access_token(token)
            return redirect('/music')

        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            return redirect(auth_url)

        # Step 4. Signed in, display data
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        if not user.spotify_id or user.spotify_id != spotify.current_user()['id']:
            user.spotify_id = spotify.current_user()['id']
            db_sess.commit()

        return func(**kwargs, spotify=spotify)

    wrapper.__name__ = func.__name__
    return wrapper


def get_followed_artists(spotify: spotipy.Spotify):
    artists = spotify.current_user_followed_artists(limit=50)['artists']['items']
    all_artists = artists
    while artists:
        artists = \
            spotify.current_user_followed_artists(limit=50, after=all_artists[-1]['id'])['artists'][
                'items']
        all_artists += artists

    return all_artists


def get_all_artist_tracks(artist_id: str, spotify: spotipy.Spotify):
    loop = 0
    albums = spotify.artist_albums(artist_id, limit=50, album_type='album')['items']
    all_albums = albums

    while albums:
        loop += 1
        albums = spotify.artist_albums(artist_id, limit=50, offset=50, album_type='album')['items']
        all_albums += albums

    loop = 0
    singles = spotify.artist_albums(artist_id, limit=50, album_type='single')['items']
    all_singles = singles

    while singles:
        loop += 1
        singles = spotify.artist_albums(artist_id, limit=50, offset=50, album_type='single')['items']
        all_singles += albums

    return {'albums': all_albums, 'singles': all_singles}
