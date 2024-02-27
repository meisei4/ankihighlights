from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'some_default_secret_value')

    db.init_app(app)

    with app.app_context():
        from .routes import anki_routes, vocab_highlight_routes
        app.register_blueprint(anki_routes)
        app.register_blueprint(vocab_highlight_routes)

        db.create_all()

    return app
