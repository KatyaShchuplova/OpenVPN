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

# настройка для сохранения конфигурационных файлов ключей


# авторизация пользователей
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from . import views, models
