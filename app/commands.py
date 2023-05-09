import click
from flask.cli import with_appcontext
from app.extentions import db, migrate
from app.models import User

# The init_db function is removed as Flask-Migrate will handle migrations


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


