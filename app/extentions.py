from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from flask_migrate import Migrate

migrate = Migrate()

jwt = JWTManager()


db = SQLAlchemy()


