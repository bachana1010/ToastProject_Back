from app.extentions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.log_in import login_manager
from sqlalchemy.dialects.sqlite import *
from datetime import datetime
from flask import session
import base64



from sqlalchemy import create_engine

# DB Model

class BaseModel():
    id = db.Column(db.Integer, primary_key=True)

def create(self, **kwargs):
    for key,value in kwargs.items():
        setattr(self, key, value)
        self.save()


@classmethod
def read_all(cls):
    return cls.query.all()


@classmethod
def read(cls, name):
    return cls.query.filter_by(name=name).first()


def update(self, **kwargs):
    for key, value in kwargs.items():
        setattr(self, key, value)
        self.save()


def delete(self):
    db.session.delete(self)
    db.session.commit()


def save(self):
    db.session.add(self)
    db.session.commit()


def __repr__(self):
    return f"players name {self.name}"



class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(225))
    toasts = db.relationship('Toast', backref='user', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, temp_email):
        email = cls.query.filter_by(email=temp_email).first()
        if email:
            return email

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            self.save()




class Toast(db.Model, BaseModel):
    __tablename__ = "Toast"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.String(512))
    input = db.Column(JSON)  # An array of strings
    img = db.Column(db.LargeBinary())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='toast', lazy=True)
    views = db.Column(db.Integer, default=0)

    def to_dict(self):
        img_base64 = base64.b64encode(self.img).decode('utf-8') if self.img else None
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'input': self.input,
            'img': img_base64,  # Convert the image to a base64 encoded string
            'user_id': self.user_id,
            'views': self.views
        }

    def delete1(self):
        db.session.delete(self)
        db.session.commit()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    toast_id = db.Column(db.Integer, db.ForeignKey("Toast.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "toast_id": self.toast_id,
            "user_id": self.user_id,
            'user_name': self.user.username if self.user else 'User'
        }
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
