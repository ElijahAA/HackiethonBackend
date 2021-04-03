from app import app, db
from datetime import datetime
from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Todo


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    if username == '' or password == '':
        return render_template('login.html', error='Please enter both a username and a password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return render_template('login.html', error='Invalid username or password')

    login_user(user)
    return redirect(url_for('todo'))


@app.route('/sign-up')
def signup():
    render_template('signUp.html')


@app.route('/todo')
def todo():
    pass


@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    pass


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    pass
