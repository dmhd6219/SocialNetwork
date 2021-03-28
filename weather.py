import flask
import pyowm
import spotipy
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from pyowm import OWM
from pyowm.utils import timestamps

from data import db_session
from data.users import User
from forms.weather import WeatherForm
from utils.spotify import spotify_login_required

blueprint = flask.Blueprint(
    'weather',
    __name__,
    template_folder='templates'
)

owm = OWM('4b0bae7206bce8cd3baa0ac1b17cf10a')
mgr = owm.weather_manager()


@blueprint.route('/weather', methods=['GET', 'POST'])
@login_required
@spotify_login_required
def weather(spotify:spotipy.Spotify):
    if current_user.city:
        return redirect(f'/weather/{current_user.city}')
    db_sess = db_session.create_session()

    form = WeatherForm()
    if form.validate_on_submit():
        return redirect(f'/weather/{form.city.data}')

    return render_template('weather.html', form=form, spotify=spotify, current_user=db_sess.query(User).get(current_user.id))


@blueprint.route('/weather/<city>', methods=['GET', 'POST'])
@login_required
@spotify_login_required
def weather_show(city, spotify:spotipy.Spotify):
    form = WeatherForm()
    if form.validate_on_submit():
        return redirect(f'/weather/{form.city.data}')

    try:
        observation = mgr.weather_at_place(city)
    except pyowm.commons.exceptions.NotFoundError:
        return abort(404)
    db_sess = db_session.create_session()

    w = observation.weather

    three_h_forecaster = mgr.forecast_at_place(city, '3h')
    tomorrow = timestamps.tomorrow()  # datetime object for tomorrow
    wea_tomorrow = three_h_forecaster.get_weather_at(tomorrow)
    print(wea_tomorrow.status.lower(), wea_tomorrow.temperature('celsius'))

    days_two = timestamps._timedelta_days(2)
    wea_two = three_h_forecaster.get_weather_at(days_two)
    print(wea_two.status.lower(), wea_two.temperature('celsius'))

    days_three = timestamps._timedelta_days(3)
    wea_three = three_h_forecaster.get_weather_at(days_three)
    print(wea_three.status.lower(), wea_three.temperature('celsius'))

    days_four = timestamps._timedelta_days(4)
    wea_four = three_h_forecaster.get_weather_at(days_four)
    print(wea_four.status.lower(), wea_four.temperature('celsius'))


    params = {'city': observation.location.name,
              'w': w,
              'wea_tomorrow': wea_tomorrow,
              'wea_two': wea_two,
              'wea_three': wea_three,
              'wea_four': wea_four,

              }

    return render_template('weather_show.html', form=form, **params, spotify=spotify, current_user=db_sess.query(User).get(current_user.id))
