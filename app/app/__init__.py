from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message

# Создание экземпляра приложения
app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')

# подключение базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@192.168.0.61:3306/openvpn'
db = SQLAlchemy(app)

# настройка для отправки писем
mail = Mail(app)

# email server
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['AIL_USERNAME'] = 'youropenvpn'
app.config['MAIL_PASSWORD'] = 'openvpn4you'

# administrator list
ADMINS = ['youropenvpn@gmail.com']


# авторизация пользователей
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from . import views, models
