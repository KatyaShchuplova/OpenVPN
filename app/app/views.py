from app import app, models, db, login_manager, mail
from datetime import datetime, date, time, timedelta
from flask import render_template, redirect, request, jsonify, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash


# user authorization
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
                    # admin authorization
                    if user.role == 1:
                        login_user(user)
                        return jsonify({'admin': 'admin success'})
                    # user authorization
                    else:
                        login_user(user)
                        return jsonify({'success': 'success'})
        except:
            return jsonify({'error': 'incorrect data'})
    return jsonify({'error': 'incorrect data'})


# user registration
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
            new_user = models.User(login=_username, password=hashed_password, email=_email)
            db.session.add(new_user)
            db.session.commit()
            # port update
            models.User.query.filter_by(id=new_user.id).update({'port': models.DEFAULT_PORT + new_user.id})
            db.session.commit()
            return jsonify({'success': 'success'})
        except:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'Missing data'})


# dashboard for users
@app.route('/dashboard')
@login_required
def dashboard():
    list_active_keys = models.Key.query.filter_by(owner_id=current_user.id, status='active').all()
    _len = len(current_user.login)
    count_allowed_key = current_user.allowed_key
    count_active_key = len(models.Key.query.filter_by(owner_id=current_user.id, status='active').all())
    if count_active_key > 0:
        nearest_key = models.Key.query.filter_by(owner_id=current_user.id,
                                                 status='active').order_by(desc(models.Key.date_end)).first()
    else:
        nearest_key = '-'
    return render_template('dashboard.html', user=current_user, allowed_key=count_allowed_key,
                           active_key=count_active_key, nearest_key=nearest_key, len=_len, keys=list_active_keys)


# отправка запроса администратору на изменение количества ключей
@app.route('/send_request', methods=['POST'])
@login_required
def send_request():
    try:
        _wanted_key = request.form['count_active_key']
        models.User.query.filter_by(id=current_user.id).update({'wanted_key': _wanted_key})
        db.session.commit()
        return jsonify({'success': 'request sent'})
    except:
        return jsonify({'error': 'request not sent'})


# key generation
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
    count_allowed_key = current_user.allowed_key
    count_active_key = len(models.Key.query.filter_by(owner_id=current_user.id, status='active').all())
    if count_allowed_key > count_active_key:
        if unique_name and days:
            try:
                start_date = datetime.now()
                delta = timedelta(int(days))
                end_date = start_date + delta
                unique_name = unique_name + current_user.login
                new_key = models.Key(unique_name=unique_name, date_start=start_date, date_end=end_date,
                                     status=models.DEFAULT_STATUS, owner_id=current_user.id, comment=comment, key='')
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
    keys = models.Key.query.filter_by(owner_id=current_user.id, status='active').all()
    length_login = len(current_user.login)
    return render_template('key-deactivation.html', user=current_user, keys=keys, len=length_login)


@app.route('/process-delete', methods=['POST'])
@login_required
def process_delete():
    unique_name = request.form['unique_name'].strip()
    if unique_name:
        try:
            print(unique_name)
            models.Key.query.filter_by(unique_name=unique_name).update({'status': 'delete'})
            db.session.commit()
            return jsonify({'success': 'unique_name'})
        except:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'Missing data'})


@app.route('/process-download', methods=['POST'])
@login_required
def process_download():
    unique_name = request.form['unique_name'].strip()
    if unique_name:
        try:
            key = models.Key.query.filter_by(unique_name=unique_name + current_user.login).first()
            with open("conf", "w") as file:
                file.write(key.key)
            return jsonify({'success': 'unique_name'})
        except:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'Missing data'})


# список ключей пользователя
@app.route('/keys-list')
@login_required
def show_keys_list():
    keys = models.Key.query.filter_by(owner_id=current_user.id).all()
    length_login = len(current_user.login)
    return render_template('keys-list.html', user=current_user, keys=keys, len=length_login)


# управление ключами
@app.route('/key-management')
@login_required
def key_management():
    keys = models.Key.query.filter_by(owner_id=current_user.id, status='active').all()
    length_login = len(current_user.login)
    return render_template('key-management.html', user=current_user, keys=keys, len=length_login)


# log out
@app.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('login'))


# dashboard for admins
@app.route('/dashboard-admin')
@login_required
def dashboard_admin():
    keys = models.Key.query.all()
    return render_template('dashboard-admin.html', user=current_user, keys=keys)


@app.route('/user-registration-admin')
@login_required
def user_registration_admin():
    return render_template('user-registration-admin.html', user=current_user)


@app.route('/requests-admin')
@login_required
def requests_admin():
    users = models.User.query.filter(models.User.allowed_key != models.User.wanted_key).all()
    return render_template('requests-admin.html', user=current_user, users=users)


# processing of user requests (allow)
@app.route('/process-request-allow', methods=['POST'])
@login_required
def process_request_allow():
    try:
        _id = request.form['id']
        _wanted_key = request.form['wanted_key']
        models.User.query.filter_by(id=_id).update({'allowed_key': _wanted_key})
        db.session.commit()
        return jsonify({'success': 'success'})
    except:
        return jsonify({'error': 'Missing data'})


# processing of user requests (deny)
@app.route('/process-request-deny', methods=['POST'])
@login_required
def process_request_deny():
    try:
        _id = request.form['id']
        _count_key = request.form['count_key']
        models.User.query.filter_by(id=_id).update({'wanted_key': _count_key})
        db.session.commit()
        return jsonify({'success': 'success'})
    except:
        return jsonify({'error': 'Missing data'})


@app.route('/management-admin')
@login_required
def management_admin():
    return render_template('management-admin.html', user=current_user)


@app.route('/key-generation-admin')
@login_required
def key_generation_admin():
    users = models.User.query.filter_by(role=models.ROLE_USER).all()
    return render_template('key-generation-admin.html', user=current_user, users=users)


@app.route('/key-deactivation-admin')
@login_required
def key_deactivation_admin():
    keys = models.Key.query.filter_by(status='active').all()
    users = models.User.query.filter_by(role=models.ROLE_USER).all()
    return render_template('key-deactivation-admin.html', user=current_user, keys=keys, users=users)


@app.route('/key-generation-admin-process', methods=['POST'])
@login_required
def key_generation_admin_process():
    user_id = request.form['user_id']
    unique_name = request.form['unique_name']
    days = request.form['days']
    comment = request.form['comment']
    user = models.User.query.filter_by(id=user_id).first()
    count_allowed_key = user.allowed_key
    count_active_key = len(models.Key.query.filter_by(owner_id=user.id, status='active').all())
    if count_allowed_key > count_active_key:
        if user_id and unique_name and days:
            try:
                start_date = datetime.now()
                delta = timedelta(int(days))
                end_date = start_date + delta
                unique_name = unique_name + user.login
                new_key = models.Key(unique_name=unique_name, date_start=start_date, date_end=end_date,
                                     status=models.DEFAULT_STATUS, owner_id=user_id, comment=comment, key='')
                db.session.add(new_key)
                db.session.commit()
                return jsonify({'name': 'unique_name'})
            except:
                return jsonify({'error': 'Missing data'})
        else:
            return jsonify({'error': 'Missing data'})
    else:
        return jsonify({'error': 'More keys can not be created'})


def get_login_on_id(id_user):
    user = models.User.query.filter_by(id=id_user).first()
    return user.login
