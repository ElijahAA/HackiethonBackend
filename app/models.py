from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    bio = db.Column(db.String(120), index=True, default=None)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    password_reset = db.Column(db.String(15), index=True, unique=True, default=None)
    todos = db.relation('Todo', backref='user', lazy='dynamic')

    timeline = db.relationship('Timeline', backref='user', lazy='dynamic')

    last_notification_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            self.add_timeline(f"Followed <strong>{user.get_full_name()}</strong>")
            user.add_notification(actor=self, body="{actor_name} has started following you")

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_formatted_name(self):
        return f"{self.first_name} {self.last_name[0]}"

    def get_pending_todos(self):
        return self.todos.filter_by(completed=False).all()

    def get_feed(self):
        followed = Todo.query.filter_by(completed=True).join(
            followers, (followers.c.followed_id == Todo.user_id)) \
            .filter(followers.c.follower_id == self.id)
        own = Todo.query.filter_by(user_id=self.id).filter_by(completed=True)
        return followed.union(own).order_by(Todo.completed_at.desc())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_timeline(self, body):
        timeline = Timeline(user=self, body=body)
        db.session.add(timeline)
        return timeline

    def get_notifications(self):
        return self.notifications.order_by(Notification.timestamp.desc()).limit(10).all()

    def get_timeline(self):
        return self.timeline.order_by(Timeline.timestamp.desc()).limit(10).all()

    def add_notification(self, actor, body):
        notification = Notification(actor_id=actor.id, body=body, user=self)
        db.session.add(notification)
        return notification

    def new_notifications(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Notification.query.filter_by(recipient=self).filter(
            Notification.timestamp > last_read_time).count()

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(140), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, index=True, default=False)
    completed_at = db.Column(db.DateTime, index=True, default=None, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reactions = db.relation('TodoReaction', backref='todo', lazy='dynamic')

    def get_creator(self):
        return User.query.get(self.user_id)

    def has_liked(self, user):
        return self.reactions.filter_by(user_id=user.id).count() > 0

    def __repr__(self):
        return '<Todo {}>'.format(self.title)


class TodoReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<TodoReaction {}: {}>'.format(self.todo_id, self.user_id)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    actor_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.String(120), nullable=False)

    def get_actor(self):
        return User.query.get(self.actor_id)

    def get_data(self):
        actor = self.get_actor()
        return self.body.replace("{actor_username}", actor.username) \
            .replace("{actor_name}", actor.get_formatted_name()) \
            .replace("{actor_full_name}", actor.get_full_name())

    def get_time(self):
        return str(self.timestamp)


class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<Timeline {}>'.format(self.body)
