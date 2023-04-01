from flask import Flask
from flask_cors import CORS
from app.log_in import login_manager

from app.extentions import db, jwt
from flask_jwt_extended import JWTManager


def create_app(config_file='config.py'):
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile(config_file)
    app.config['UPLOAD_FOLDER'] = 'static/files'
    register_extension(app)
    register_blouprint(app)
    login_manager.init_app(app)
    jwt.init_app(app)  # Initialize flask_jwt_extended

    return app

login_manager.login_view = "user.login"

def register_extension(app):
    db.init_app(app)


def register_blouprint(app):

    from app.blog_view.views import toast_blueprint
    app.register_blueprint(toast_blueprint)

    from app.registration.views_login import user_blueprint
    app.register_blueprint(user_blueprint)


