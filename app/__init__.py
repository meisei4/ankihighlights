from flask import Flask
from app.models import db
from app.routes.vocab_highlights_routes import vocab_highlight_routes


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        app.register_blueprint(vocab_highlight_routes)
        db.create_all()
        return app
