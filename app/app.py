from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import logging

from app.routes.anki_routes import anki_routes
from app.routes.vocab_highlights_routes import vocab_highlight_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'some_default_secret_value')
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        app.register_blueprint(anki_routes)
        app.register_blueprint(vocab_highlight_routes)

        db.create_all()

    return app
