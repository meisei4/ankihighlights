from app.app import db

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False, unique=True)
    lookups = db.relationship('Lookup', backref='word', lazy=True)

class BookInfo(db.Model):
    __tablename__ = 'book_info'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    lookups = db.relationship('Lookup', backref='book_info', lazy=True)

class Lookup(db.Model):
    __tablename__ = 'lookups'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    book_info_id = db.Column(db.Integer, db.ForeignKey('book_info.id'), nullable=False)
    usage = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)
