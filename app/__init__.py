from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        from app.routes.vocab_highlights_routes import vocab_highlight_routes
        app.register_blueprint(vocab_highlight_routes)
        db.create_all()

    return app
