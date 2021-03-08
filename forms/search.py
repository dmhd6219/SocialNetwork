from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    data = EmailField('Email address', validators=[DataRequired()])

    submit = SubmitField()
