from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterUser(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    name = StringField('User\'s name', validators=[DataRequired()])
    surname = StringField('User\'s surname', validators=[DataRequired()])

    remember_me = BooleanField('Remeber me')

    submit = SubmitField('Join')


class LoginUser(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    remember_me = BooleanField('Remeber me')

    submit = SubmitField('Enter')
