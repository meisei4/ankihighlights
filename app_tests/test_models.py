from app.models.models import Word

def test_word_creation(init_database):
    word = Word(word='test')
    init_database.session.add(word)
    init_database.session.commit()
    assert Word.query.count() == 1
    assert Word.query.first().word == 'test'

