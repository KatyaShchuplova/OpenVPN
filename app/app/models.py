from . import db
from . import login_manager
from flask_login import UserMixin

ROLE_USER = 0
ROLE_ADMIN = 1
DEFAULT_ALLOWED_KEY = 15
DEFAULT_STATUS = 'active'
DEFAULT_PORT = 30000


# test

# модель для представления таблицы users
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(50))
    allowed_key = db.Column(db.Integer, default=DEFAULT_ALLOWED_KEY)
    wanted_key = db.Column(db.Integer, default=DEFAULT_ALLOWED_KEY)
    role = db.Column(db.Integer, default=ROLE_USER)
    port = db.Column(db.Integer, default=DEFAULT_PORT)
    vpnCreated = db.Column(db.Boolean, default=False)
    keys = db.relationship('Key', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.login)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# модель для представления таблицы keys
class Key(db.Model):
    __tablename__ = 'keys'
    id = db.Column(db.Integer, primary_key=True)
    unique_name = db.Column(db.String(256), unique=True)
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    status = db .Column(db.String(20))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.String(120))
    isCreated = db.Column(db.Boolean, default=False)
    key = db.Column(db.String)

    def __repr__(self):
        return '{}'.format(self.unique_name)