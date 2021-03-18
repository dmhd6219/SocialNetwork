from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class PrivacySettingsForm(FlaskForm):
    profile = SelectField('Who can see Your Profile', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    friends = SelectField('Who can see Your Friends', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    music = SelectField('Who can see Your Music', choices=['All', 'Only Friends', 'No one'],
                        validators=[DataRequired()])
    messages = SelectField('Who can write You', choices=['All', 'Only Friends'],
                           validators=[DataRequired()])

    submit = SubmitField("Submit")


class PrivacySettingsForm2(FlaskForm):
    profile = SelectField('Others can see Your Email', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    friends = SelectField('Others can see Your Friends', choices=['All', 'Only Friends', 'No one'],
                          validators=[DataRequired()])
    music = SelectField('Who can see Your Music', choices=['All', 'Only Friends', 'No one'],
                        validators=[DataRequired()])
    messages = SelectField('Who can write You', choices=['All', 'Only Friends'],
                           validators=[DataRequired()])

    submit = SubmitField("Submit")
