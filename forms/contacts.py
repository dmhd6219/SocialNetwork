from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField, FileField, IntegerField
from wtforms.fields.html5 import TelField, URLField, EmailField

photos = UploadSet('photos', IMAGES)


class ContactInformation(FlaskForm):
    phone = TelField('Contact Number')
    email = EmailField('Old Email address', )
    new_email = EmailField('New Email Address')
    new_email_again = EmailField('New Email address again', )
    url = URLField('Url')

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
