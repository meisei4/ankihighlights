from app.models.models import Lookup, Word, BookInfo


def test_request_permission_route(client):
    response = client.get('/anki/request_permission')
    assert response.status_code == 200
    assert 'success' in response.json

def test_process_highlights(client, init_database):
    word = Word(word='test')
    book_info = BookInfo(title='Test Book', authors='Author A')
    lookup = Lookup(word=word, book_info=book_info, usage='Usage example', timestamp=123456789)
    init_database.session.add_all([word, book_info, lookup])
    init_database.session.commit()

    response = client.post('/vocab_highlights/process')
    assert response.status_code == 200
    assert response.json['success'] == True
    # Further assertions can check for the side effects in Anki or the database.
