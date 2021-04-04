from app import app, db, avatars
from datetime import datetime
import os, secrets
from flask import request, redirect, url_for, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_avatars import Avatars
from app.models import User, Todo


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', current_page="home")


@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', current_page="login")

    username = request.form['username']
    password = request.form['password']

    if username == '' or password == '':
        return render_template('login.html', current_page="login", error='Please enter both a username and a password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return render_template('login.html', current_page="login", error='Invalid username or password')

    login_user(user)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('signUp.html', current_page="signup")

    username = request.form['username']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    if username == '' or first_name == '' or last_name == '' or email == '' or password == '':
        return render_template('signUp.html', current_page="signup", error='Missing required fields')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user is not None:
        return render_template('signUp.html', current_page="signup", error="Username is already in use")

    existing_user = User.query.filter_by(email=email).first()
    if existing_user is not None:
        return render_template('signUp.html', current_page="signup", error="Email is already in use")

    user = User(username=username, first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('index'))


@app.route('/todo')
def todo():
    if request.method == 'GET':
        return render_template('todo.html', current_page="todos", todos=Todo.query.all(), )
    title = request.form['title']
    description = request.form['description']
    user = User.query.get(current_user.id)
    newTodo = Todo(title=title, description=description, user=user)
    db.session.add(newTodo)
    db.session.commit()
    return redirect(url_for('todo'))


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', current_page='profile', user=user)


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'GET':
        return render_template('editProfile.html', current_page='editProfile')
    bio = request.form['bio']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    username = request.form['username']

    existing_user = User.query.filter_by(username=username).first()
    if existing_user is not None and existing_user != current_user:
        return render_template('editProfile.html', current_page='editProfile', error='That username is already in use')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user is not None and existing_user != current_user:
        return render_template('editProfile.html', current_page='editProfile', error='That email is already in use')

    avatar = request.files.get('file', None)
    if avatar:
        save_avatar(avatar)

    current_user.bio = bio
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    current_user.username = username
    db.session.commit()

    return redirect(url_for('editProfile'))


def save_avatar(file):
    random_hex = secrets.token_hex(10)
    _, file_ext = os.path.splitext(file.filename)
    if file_ext not in ['.jpeg', '.png', '.jpg']:
        return False
    picture_fn = random_hex + file_ext
    path = app.config['AVATARS_SAVE_PATH']
    file.save(os.path.join(path, picture_fn))
    current_user.avatar = url_for('get_avatar', filename=picture_fn)
    db.session.commit()
    return True


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    pass


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    pass


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
