import os
import uuid

import spotipy
from flask import session, request, redirect

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

def spotify_login_required(func):
    def wrapper():
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
            return redirect(auth_url)

        # Step 4. Signed in, display data
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        return func(spotify)

    wrapper.__name__ = func.__name__
    return wrapper