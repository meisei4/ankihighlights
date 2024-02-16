# /app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()


def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    # Configure the Flask app based on environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'you-should-change-this')

    db.init_app(app)

    with app.app_context():
        # Import routes and models here to avoid circular imports
        from .routes import api as api_blueprint
        app.register_blueprint(api_blueprint)

        # Create the database tables for all models
        db.create_all()

    return app
