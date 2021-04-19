import os
import uuid
from pprint import pprint

import flask
import spotipy
from flask import session, request, redirect, render_template, abort, jsonify
from flask_login import login_required, current_user

from data import db_session
from data.users import User
from utils.spotify import spotify_login_required, session_cache_path, SCOPE, get_followed_artists

blueprint = flask.Blueprint(
    'music',
    __name__,
    template_folder='templates'
)


@blueprint.route('/music', methods=['GET', 'POST'])
@login_required
@spotify_login_required
def music(spotify: spotipy.Spotify):
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    return render_template('music.html', **params)


@blueprint.route('/music/search/<data>')
@login_required
@spotify_login_required
def search_music(data, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'artists': spotify.search(q=data, type='artist', limit=6)['artists']['items'],
        'albums': spotify.search(q=data, type='album', limit=6)['albums']['items'],
        'tracks': spotify.search(q=data, type='track', limit=6)['tracks']['items'],

        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    return render_template('search.html', **params)


@blueprint.route('/music/artist/followed')
@login_required
@spotify_login_required
def followed_artists(spotify: spotipy.Spotify):
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
        'artists': sorted(get_followed_artists(spotify), key=lambda x: x['popularity'],
                          reverse=True)
    }
    return render_template('followed_artists.html', **params)


@blueprint.route('/music/artist/<id>')
@login_required
@spotify_login_required
def artist(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()

    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    # 4K7kAAsdwnIHjgRk28OyOi

    try:
        params['artist'] = spotify.artist(id)
        params['top_tracks'] = spotify.artist_top_tracks(id)['tracks'][:6:]
        params['albums'] = spotify.artist_albums(id, album_type='album', limit=7)['items']
        params['singles'] = spotify.artist_albums(id, album_type='single', limit=7)['items']
        params['appears_on'] = spotify.artist_albums(id, album_type='appears_on', limit=7)['items']
    except:
        return abort(404)

    pprint(params['artist'])

    return render_template('artist.html', **params)


@blueprint.route('/music/artist/<id>/albums')
@login_required
@spotify_login_required
def artist_albums(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    try:
        params['artist'] = spotify.artist(id)
        params['albums'] = spotify.artist_albums(id, album_type='album', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_albums.html', **params)


@blueprint.route('/music/artist/<id>/singles')
@login_required
@spotify_login_required
def artist_singles(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    try:
        params['artist'] = spotify.artist(id)
        params['singles'] = spotify.artist_albums(id, album_type='single', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_singles.html', **params)


@blueprint.route('/music/artist/<id>/appears_on')
@login_required
@spotify_login_required
def artist_appears_on(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    try:
        params['artist'] = spotify.artist(id)
        params['appears_on'] = spotify.artist_albums(id, album_type='appears_on', limit=50)['items']
    except:
        return abort(404)

    return render_template('artist_appears_on.html', **params)


@blueprint.route('/music/playlist/<id>')
@login_required
@spotify_login_required
def playlist(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    # id = 2duj5GBXwLRdjqV9hjXy4o

    try:
        params['playlist'] = spotify.playlist(id)
        dur = 0
        for track in params['playlist']['tracks']['items']:
            dur += float(track['track']['duration_ms']) / 1000 / 60
        params['duration'] = round(dur, 2)
    except Exception:
        return abort(404)

    return render_template('playlist.html', **params)


@blueprint.route('/music/track/<id>')
@login_required
@spotify_login_required
def track(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

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

    return render_template('track.html', **params)


@blueprint.route('/music/album/<id>')
@login_required
@spotify_login_required
def album(id, spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {
        'current_user': db_sess.query(User).get(current_user.id),
        'spotify': spotify,
    }

    # id = 6WLBApYwMaajoFlzITzb6P

    try:
        params['playlist'] = spotify.album(id)
        dur = 0
        for track in params['playlist']['tracks']['items']:
            dur += float(track['duration_ms']) / 1000 / 60
        params['duration'] = round(dur, 2)
        params['artists'] = [[(artist['name'], artist['id']) for artist in track['artists']] for
                             track in params['playlist']['tracks']['items']]
        #
        #
        # сделать отображение всех артистов
        # использовать loop.first или loop.end
        #
    except:
        return abort(404)

    return render_template('album.html', **params)


@blueprint.route('/music/track/top')
@login_required
@spotify_login_required
def top_tracks(spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {'tracks': spotify.current_user_top_tracks(time_range='short_term'),
              'current_user': db_sess.query(User).get(current_user.id),
              'spotify': spotify,
              }

    return render_template('top_tracks.html', **params)


@blueprint.route('/music/artist/top')
@login_required
@spotify_login_required
def top_artists(spotify: spotipy.Spotify):
    db_sess = db_session.create_session()
    params = {'artists': spotify.current_user_top_artists(time_range='short_term'),
              'current_user': db_sess.query(User).get(current_user.id),
              'spotify': spotify,
              }

    return render_template('top_artists.html', **params)


@blueprint.route('/music/test_page')
@login_required
@spotify_login_required
def test_page(spotify: spotipy.Spotify):
    ans = ''
    pprint(spotify.new_releases('RU', limit=1))
    return jsonify(
        {
            'ans': ans
        }
    )


@blueprint.route('/spotify_sign_out')
@spotify_login_required
def sign_out(spotify: spotipy.Spotify):
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@blueprint.route('/playlists')
@spotify_login_required
def playlists(spotify: spotipy.Spotify):
    return spotify.current_user_playlists()


@blueprint.route('/currently_playing')
@spotify_login_required
def currently_playing(spotify: spotipy.Spotify):
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@blueprint.route('/spotify_current_user')
@spotify_login_required
def get_current_user(spotify: spotipy.Spotify):
    return spotify.current_user()


@blueprint.route('/music/play/<uri>', methods=['POST'])
@spotify_login_required
def play(uri, spotify: spotipy.Spotify):
    spotify.start_playback(context_uri=uri)
