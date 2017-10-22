from . import db
from . import login_manager
from flask_login import UserMixin

ROLE_USER = 0
ROLE_ADMIN = 1
DEFAULT_ALLOWED_KEY = 15
DEFAULT_STATUS = 'active'


# test

# модель для представления таблицы users
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(50))
    allowedKey = db.Column(db.Integer, default=DEFAULT_ALLOWED_KEY)
    role = db.Column(db.Integer, default=ROLE_USER)
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
    uniqueName = db.Column(db.String(256), unique=True)
    startDate = db.Column(db.DateTime)
    endDate = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    ownerId = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.String(120))

    def __repr__(self):
        return '{}'.format(self.uniqueName)