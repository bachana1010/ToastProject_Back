from app.extentions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.log_in import login_manager
from sqlalchemy.dialects.sqlite import *
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

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'input': self.input,
            'img': self.img,
            'user_id': self.user_id
        }

    def delete1(self):
        db.session.delete(self)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

