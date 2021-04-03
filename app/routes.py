from app import app, db
from datetime import datetime
from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Todo


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', current_page="home")


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
    return redirect('/todo')


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', current_page='profile', user=user)


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    pass


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    pass
