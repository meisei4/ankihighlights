from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy without any arguments
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Assuming environment variables are already loaded via config.py in run.py
    # Directly assign configurations to the Flask app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'some_default_secret_value')

    # Initialize the database with the Flask app
    db.init_app(app)

    with app.app_context():
        from app.routes import anki_routes, vocab_highlight_routes
        app.register_blueprint(anki_routes)
        app.register_blueprint(vocab_highlight_routes)

        # Create the database tables for all models, if they don't already exist
        db.create_all()

    return app
