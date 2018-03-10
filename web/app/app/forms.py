from app import app, models, db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length


# форма для авторизации пользователей
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=15)])


# форма для регистрации новых пользователей
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=15)])


# форма для генерации ключей
class RegisterKeyForm(FlaskForm):
    unique_name = StringField('UniqueName', validators=[InputRequired(), Length(max=50)])
    days = RadioField('Days', choices=[('90', '90 days'), ('180', '180 days'), ('360', '360 days')], default='180')


def choice_query():
    return models.Key.query


# форма для удаления ключей
class DeactivationKeyForm(FlaskForm):
    deactivation_key = QuerySelectField(query_factory=choice_query(), allow_blank=True, get_label="uniqueName")
