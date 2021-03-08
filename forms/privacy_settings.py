from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class PrivacySettingsForm(FlaskForm):
    profile = SelectField('Choose :', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    friends = SelectField('Choose :', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    music = SelectField('Choose :', choices=['All', 'Only Friends', 'No one'],
                        validators=[DataRequired()])
    messages = SelectField('Choose :', choices=['All', 'Only Friends'],
                           validators=[DataRequired()])

    submit = SubmitField("Submit")
