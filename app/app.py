import logging
import os

from flask import Flask
from flask_injector import FlaskInjector
from flask_migrate import Migrate
from injector import singleton
from sqlalchemy import create_engine

from app.logger import logger
from app.models import init_model
from app.models.dto.latest_timestamp_dto import LatestTimestampDTO
from app.models.dto.lookup_dto import LookupDTO
from app.repositories.highlight_repository import HighlightRepository
from app.repositories.latest_timestamp_repository import LatestTimestampRepository
from app.services.highlight_service import HighlightService

migrate = Migrate()


def configure(binder):
    binder.bind(HighlightRepository, to=HighlightRepository, scope=singleton)
    binder.bind(LatestTimestampRepository, to=LatestTimestampRepository, scope=singleton)
    binder.bind(HighlightService, to=HighlightService, scope=singleton)
    binder.bind(LatestTimestampDTO, to=LatestTimestampDTO, scope=singleton)
    binder.bind(LookupDTO, to=LookupDTO, scope=singleton)


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

            # Integrate FlaskInjector after app context is created
            FlaskInjector(app=app, modules=[configure])
            logger.info("FlaskInjector configured.")

    except Exception as e:
        logger.error(f"Error during application setup: {e}")

    logger.info("Application setup complete.")
    return app
