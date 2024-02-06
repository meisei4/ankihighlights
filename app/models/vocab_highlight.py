from app import db

class VocabHighlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    usage = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)
    book_title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    anki_card_id = db.Column(db.Integer, db.ForeignKey('anki_card.id'))
    anki_card = db.relationship('AnkiCard', back_populates='vocab_highlights')
