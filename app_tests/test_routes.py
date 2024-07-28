import logging


def test_process_highlights_route(test_client, add_lookup_data, reset_anki):
    # Reset Anki and database state
    reset_anki()

    # Add some lookup data to process
    add_lookup_data(word="日本語", usage="日本語の文")
    add_lookup_data(word="和文", usage="また別の和文")

    # Make the POST request to process highlights
    response = test_client.post('/highlight/process')
    response_json = response.get_json()
    logging.info(response_json)

    # Check the response status code
    assert response.status_code == 200
    assert response_json.get('success') is True

    # Verify that the highlights have been processed
    assert 'data' in response_json
    highlights = response_json['data'].get('highlight')
    assert highlights is not None
    assert isinstance(highlights, list)
    assert len(highlights) > 0  # Ensure highlights were actually processed

    # Additional checks for highlight DTO structure
    for highlight in highlights:
        assert 'id' in highlight
        assert 'word_id' in highlight
        assert 'book_id' in highlight
        assert 'usage' in highlight
        assert 'timestamp' in highlight
