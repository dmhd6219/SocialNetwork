from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired



class CreatePost(FlaskForm):
    text = TextAreaField('Write something here...', validators=[DataRequired()])