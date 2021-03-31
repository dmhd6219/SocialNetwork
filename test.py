import spotipy


def get_followed_artists(spotify: spotipy.Spotify):
    artists = spotify.current_user_followed_artists(limit=50)['artists']['items']
    all_artists = artists
    while artists:
        artists = spotify.current_user_followed_artists(limit=50, after=all_artists[-1]['id'])['artists']['items']
        all_artists += artists

    return all_artists

