import logging
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    logger.setLevel(logging.DEBUG)  # Ensure logger captures debug messages
    logger.info("Starting application setup.")

    app = Flask(__name__)
    logger.info("Flask app created.")

    # Configuration logs
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'some_default_secret_value')
    logger.info("Application configurations set.")

    # Database initialization logs
    db.init_app(app)
    migrate.init_app(app, db)
    logger.info("Loading environment variables:")
    logger.info("Test suite configuration started.")
    logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    logger.info(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
    logger.info(f"FLASK_RUN_PORT: {os.getenv('FLASK_RUN_PORT')}")
    logger.info(f"VERSION: {os.getenv('VERSION')}")
    logger.info("Database and migrations initialized.")

    # logger.info(f"ANKI_API_URL: {os.getenv('ANKI_API_URL')}")


    try:
        with app.app_context():
            from app.routes.anki_route_controller import anki_routes
            from app.routes.vocab_highlights_route_controller import vocab_highlight_routes
            app.register_blueprint(anki_routes)
            app.register_blueprint(vocab_highlight_routes)

            db.create_all()
            logger.info("Database tables created and blueprints registered.")
    except Exception as e:
        logger.error(f"Error during application setup: {e}")

    logger.info("Application setup complete.")
    return app
