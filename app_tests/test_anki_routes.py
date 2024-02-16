from unittest.mock import patch

def test_get_decks_route(client):
    with patch('app.services.anki_service.AnkiService.get_all_deck_names') as mock_get_decks:
        mock_get_decks.return_value = {"result": ["Default"], "error": None}
        response = client.get('/anki/decks')
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "Default" in response.json['data']['result']
