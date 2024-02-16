from flask import Blueprint

vocab_highlight_routes = Blueprint('vocab_highlights', __name__, url_prefix='/vocab_highlights')

anki_routes = Blueprint('anki', __name__, url_prefix='/anki')