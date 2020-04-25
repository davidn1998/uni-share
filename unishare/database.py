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
    posts = db.relationship('Post', backref='user', lazy=True)

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