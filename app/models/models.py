from app.app import db


class LatestTimestamp(db.Model):
    __tablename__ = 'latest_timestamp'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.BigInteger, nullable=False)


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False, unique=True)
    lookups = db.relationship('Lookup', backref='word', lazy=True, cascade="all, delete-orphan")
    anki_cards = db.relationship('AnkiCard', backref='word', lazy=True, cascade="all, delete-orphan")


class BookInfo(db.Model):
    __tablename__ = 'book_info'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    lookups = db.relationship('Lookup', backref='book', lazy=True, cascade="all, delete-orphan")


class Lookup(db.Model):
    __tablename__ = 'lookups'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book_info.id'), nullable=False)
    usage = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)


class AnkiCard(db.Model):
    __tablename__ = 'anki_cards'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    deck_name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    front = db.Column(db.String(255), nullable=False)
    back = db.Column(db.String(255), nullable=False)
    anki_card_id = db.Column(db.String(255), nullable=False, unique=True)
    usage = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.BigInteger, nullable=False)
