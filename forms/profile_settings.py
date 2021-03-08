from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AccountSetting(FlaskForm):
    name = StringField('User\'s name', )
    surname = StringField('User\'s surname', )

    email = EmailField('Email address', )
    email_again = EmailField('New Email address', )

    submit = SubmitField('Submit')


class SocialMedia(FlaskForm):
    vk = StringField('VK', )
    show_vk = BooleanField('Other Users can see Your VK', )

    facebook = StringField('Facebook', )
    show_facebook = BooleanField('Other Users can see Your Facebook', )

    twitter = StringField('Twitter', )
    show_twitter = BooleanField('Other Users can see Your Twitter', )

    instagram = StringField('Instagram', )
    show_instagram = BooleanField('Other Users can see Your Instagram', )

    youtube = StringField('Youtube', )
    show_youtube = BooleanField('Other Users can see Your YouTube', )

    submit = SubmitField('Submit')


class ChangePassword(FlaskForm):
    old_pass = PasswordField('Old Password', validators=[DataRequired()])
    new_pass = PasswordField('New Password', validators=[DataRequired()])
    new_pass_again = PasswordField('New Password Again', validators=[DataRequired()])

    submit = SubmitField('Submit')