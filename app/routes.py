from app import app, db, avatars
import os, secrets
from flask import request, redirect, url_for, render_template, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Todo, TodoReaction, Notification


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('todo'))
    return render_template('index.html')


@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


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
        return render_template('signUp.html')

    username = request.form['username']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    if username == '' or first_name == '' or last_name == '' or email == '' or password == '':
        return render_template('signUp.html', error='Missing required fields')

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


@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'GET':
        return render_template('todo.html', current_page="todos", todos=Todo.query.filter_by(completed=False).all())
    title = request.form['title']
    description = request.form['description']
    user = User.query.get(current_user.id)
    newTodo = Todo(title=title, description=description, user=user)
    db.session.add(newTodo)
    user.add_timeline(f"Created a new task <strong>{title}</strong>")
    db.session.commit()
    return redirect(url_for('todo'))


@app.route('/todo/<id>/edit', methods=['POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get(int(id))
    if todo is None:
        return jsonify(result="error", message="todo not found")
    if "title" in request.form:
        title = request.form['title']
        todo.title = title
    if "description" in request.form:
        description = request.form['description']
        todo.description = description
    db.session.commit()
    return jsonify(result="success")


@app.route('/todo/<id>/like', methods=['GET'])
@login_required
def like_todo(id):
    todo = Todo.query.get(int(id))
    if todo is None:
        return jsonify(result="error", message="Todo not found")
    if todo.has_liked(current_user):
        return jsonify(result="error", message="Already liked")
    db.session.add(TodoReaction(user_id=current_user.id, todo_id=todo.id))
    creator = User.query.get(todo.user_id)
    creator.add_notification(actor=current_user,
                             body="{actor_username} liked your completed task <strong>" + todo.title + "</strong>")
    db.session.commit()
    return jsonify(result="success")


@app.route('/todo/<id>/unlike', methods=['GET'])
@login_required
def unlike_todo(id):
    todo = Todo.query.get(int(id))
    if todo is None:
        return jsonify(result="error", message="Todo not found")
    reaction = TodoReaction.query.filter_by(user_id=current_user.user.id, todo_id=todo.id).first()
    if reaction is None:
        return jsonify(result="error", message="Not liked")
    db.session.delete(reaction)
    db.session.commit()
    return jsonify(result="success")


@app.route('/todo/<id>/delete', methods=['GET'])
@login_required
def delete_todo(id):
    todo = Todo.query.get(int(id))
    if todo.user_id != current_user.id:
        return redirect(url_for('todo'))
    current_user.add_timeline(f"Deleted task <strong>{todo.title}</strong>")
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', current_page='profile', user=user)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
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

    avatar = request.files.get('avatar', None)
    if avatar:
        if not save_avatar(avatar):
            return render_template('editProfile.html', current_page='editProfile', error='Please upload a valid image')

    current_user.bio = bio
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    current_user.username = username
    db.session.commit()

    return redirect(url_for('edit_profile'))


def save_avatar(file):
    random_hex = secrets.token_hex(10)
    _, file_ext = os.path.splitext(file.filename)
    if file_ext not in ['.jpeg', '.png', '.jpg']:
        return False
    picture_fn = random_hex + file_ext
    path = app.config['AVATARS_SAVE_PATH']
    file.save(os.path.join(path, picture_fn))
    current_user.avatar = url_for('get_avatar', filename=picture_fn)
    return True


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        return redirect(url_for('profile', username=username))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        return redirect(url_for('profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('profile', username=username))


@app.route('/feed', methods=['POST'])
@login_required
def feed():
    feed = current_user.get_feed()
    return jsonify([{
        'avatar': '',
        'name': f.get_creator().get_formatted_name() if f.get_creator() != current_user else "You",
        'liked': f.has_liked(current_user),
        'title': f.title,
    } for f in feed])


@app.route('/notifications', methods=['POST'])
@login_required
def notifications():
    new_notifications = current_user.notifications.filter(
        Notification.timestamp > current_user.last_notification_read_time).count() > 0
    notifications = current_user.notifications.order_by(Notification.timestamp.asc()).limit(10).all()
    return jsonify({
        'new': new_notifications,
        'notifications': [{
            'data': n.get_data(),
            'timestamp': n.timestamp
        } for n in notifications]
    })


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
