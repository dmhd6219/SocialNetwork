from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField, FileField, IntegerField

photos = UploadSet('photos', IMAGES)


class PersonalInformation(FlaskForm):
    photo = FileField(
        validators=[FileAllowed(photos, 'Image only!')])

    name = StringField('First name', )
    surname = StringField('Last name', )

    gender = StringField('Gender')
    age = IntegerField('Age')

    marital_status = SelectField('Marital Status',
                                 choices=['Single', 'Married', 'Widowed', 'Divorced', 'Separated'])
    city = StringField('City')

    address = TextAreaField('Address')

    submit = SubmitField('Submit')
