from unittest.mock import patch

def test_process_highlights_route(client):
    with patch('app.services.vocab_highlight_service.VocabHighlightService.process_new_vocab_highlights') as mock_process:
        mock_process.return_value = True  # Adjust based on actual return value or side effect
        response = client.post('/vocab_highlights/process')
        assert response.status_code == 200
        assert response.json['success'] == True
