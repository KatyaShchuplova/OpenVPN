from datetime import datetime, timedelta

from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, models, db, mail
from flask import render_template, redirect, request, jsonify, url_for


# авторизация пользователей
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login_post', methods=['GET', 'POST'])
def login_post():
    _username = request.form['username']
    _password = request.form['password']
    if _username and _password:
        try:
            user = models.User.query.filter_by(login=_username).first()
            if user:
                if check_password_hash(user.password, _password):
                    login_user(user)
                    redirect_url = url_for('dashboard')
                    return jsonify({'success': 'success'})
        except:
            return jsonify({'error': 'incorrect data'})
    return jsonify({'error': 'incorrect data'})


# регистрация пользователей
@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/sign_up_post', methods=['POST'])
def sign_up_post():
    _username = request.form['username']
    _email = request.form['email']
    _password = request.form['password']
    if _username and _email and _password:
        try:
            hashed_password = generate_password_hash(_password, method='sha256')
            new_user = models.User(login=_username, password=hashed_password, email=_email,
                                   allowedKey=models.DEFAULT_ALLOWED_KEY, role=models.ROLE_USER)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': 'success'})
        except:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'Missing data'})


# домашняя страница dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    list_active_keys = models.Key.query.filter_by(ownerId=current_user.id, status='active').all()
    _len = len(current_user.login)
    count_allowed_key = current_user.allowedKey
    count_active_key = len(models.Key.query.filter_by(ownerId=current_user.id, status='active').all())
    if count_active_key > 0:
        nearest_key = models.Key.query.filter_by(ownerId=current_user.id,
                                                 status='active').order_by(desc(models.Key.endDate)).first()
    else:
        nearest_key = '-'
    return render_template('dashboard.html', user=current_user, allowed_key=count_allowed_key,
                           active_key=count_active_key, nearest_key=nearest_key, len=_len, keys=list_active_keys)


# отправка писем администратору на запрос ключей
@app.route('/send_emails', methods=['POST'])
@login_required
def send_emails():
    try:
        message = Message('I need more keys', sender='youropenvpn@gmail.com', recipients=['e.shchuplova@gmail.com'])
        print(message)
        mail.send(message)
        return jsonify({'success': 'email sent'})
    except:
        return jsonify({'error': 'email not sent'})


# генерация ключей
@app.route('/key-generation')
@login_required
def key_generation():
    return render_template('key-generation.html', user=current_user)


@app.route('/process', methods=['POST'])
@login_required
def process():
    unique_name = request.form['unique_name']
    days = request.form['days']
    comment = request.form['comment']
    count_allowed_key = current_user.allowedKey
    count_active_key = len(models.Key.query.filter_by(ownerId=current_user.id, status='active').all())
    if count_allowed_key > count_active_key:
        if unique_name and days:
            try:
                start_date = datetime.now()
                delta = timedelta(int(days))
                end_date = start_date + delta
                unique_name = unique_name + current_user.login
                new_key = models.Key(uniqueName=unique_name, startDate=start_date, endDate=end_date, status=models.DEFAULT_STATUS, ownerId=current_user.id, comment=comment)
                print(new_key)
                db.session.add(new_key)
                db.session.commit()
                return jsonify({'name': 'unique_name'})
            except:
                return jsonify({'error': 'Missing data'})
        else:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'More keys can not be created'})


# удаление ключей
@app.route('/key-deactivation')
@login_required
def key_deactivation():
    keys = models.Key.query.filter_by(ownerId=current_user.id, status='active').all()
    length_login = len(current_user.login)
    return render_template('key-deactivation.html', user=current_user, keys=keys, len=length_login)


@app.route('/process-delete', methods=['POST'])
@login_required
def process_delete():
    unique_name = request.form['unique_name']
    if unique_name:
        try:
            unique_name = unique_name
            models.Key.query.filter_by(uniqueName=unique_name).update({'status': 'delete'})
            db.session.commit()
            return jsonify({'success': 'unique_name'})
        except:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'Missing data'})


# список ключей пользователя
@app.route('/keys-list')
@login_required
def show_keys_list():
    keys = models.Key.query.filter_by(ownerId=current_user.id).all()
    length_login = len(current_user.login)
    return render_template('keys-list.html', user=current_user, keys=keys, len=length_login)


# управление ключами
@app.route('/key-management')
@login_required
def key_management():
    keys = models.Key.query.filter_by(ownerId=current_user.id, status='active').all()
    length_login = len(current_user.login)
    return render_template('key-management.html', user=current_user, keys=keys, len=length_login)


# log out
@app.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('login'))


# домашняя страница dashboard для администратора
@app.route('/dashboard-admin')
@login_required
def dashboard_admin():
    return render_template('dashboard-admin.html', user=current_user)