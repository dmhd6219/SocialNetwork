from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField, FileField


photos = UploadSet('photos', IMAGES)


class UploadPhoto(FlaskForm):
    photo = FileField(
        validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    submit = SubmitField('Upload')
