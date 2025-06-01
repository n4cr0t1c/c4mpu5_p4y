from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'campuspay'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campuspay.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    from .routes import app_routes
    app.register_blueprint(app_routes)

    return app