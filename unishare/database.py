from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This object will be linked to the postgres/unishare database
db = SQLAlchemy()

# Create users table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    received_messages = db.relationship('Message', backref='received', lazy='dynamic', foreign_keys='Message.recipient_id')
    sent_messages = db.relationship('Message', backref='sent', lazy='dynamic', foreign_keys='Message.sender_id')

    def add_post(self, title, body):
        post = Post(author_id=self.id, title=title, body=body)
        db.session.add(post)
        db.session.commit()

# Create posts table
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    author = db.relationship("User", foreign_keys=[author_id])

# Create messages table
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    subject = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])