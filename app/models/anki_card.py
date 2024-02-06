from app import db

class AnkiCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(255), nullable=False)
    back = db.Column(db.String(255), nullable=False)
    vocab_highlights = db.relationship('VocabHighlight', back_populates='anki_card')
