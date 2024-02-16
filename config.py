import os
from dotenv import load_dotenv

# Determine the environment based on an environment variable and load the corresponding .env file
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
if ENVIRONMENT == "testing":
    load_dotenv('.env.test')
elif ENVIRONMENT == "production":
    load_dotenv('.env.production')
else:
    load_dotenv('.env')  # Default to loading .env


class Config(object):
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # You can add more base config variables common to all environments


class DevelopmentConfig(Config):
    """Development specific configurations."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Additional development-specific variables


class TestingConfig(Config):
    """Testing specific configurations."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    # Ensure TEST_DATABASE_URL is set in your .env.test file
    # Additional testing-specific variables


class ProductionConfig(Config):
    """Production specific configurations."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Additional production-specific variables


# Optionally, you can add a dictionary to easily map the config based on the FLASK_ENV variable
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    production=ProductionConfig
)
