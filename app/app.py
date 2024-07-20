import logging
import os

from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import create_engine

from app.models import init_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

migrate = Migrate()


def create_app():
    logger.setLevel(logging.DEBUG)
    logger.info("Starting application setup.")

    app = Flask(__name__)
    logger.info("Flask app created.")

    # Configuration logs
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'some_default_secret_value')
    logger.info("Application configurations set.")

    # Database initialization logs
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    init_model(engine)
    logger.info("Loading environment variables:")
    logger.info("Test suite configuration started.")
    logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    logger.info(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
    logger.info(f"FLASK_RUN_PORT: {os.getenv('FLASK_RUN_PORT')}")
    logger.info(f"VERSION: {os.getenv('VERSION')}")
    logger.info("Database initialized.")

    try:
        with app.app_context():
            from app.controllers.highlight_controller import highlight_routes
            app.register_blueprint(highlight_routes)
            logger.info("Database tables created and blueprints registered.")
    except Exception as e:
        logger.error(f"Error during application setup: {e}")

    logger.info("Application setup complete.")
    return app
