import logging


def test_request_permission_route(test_client):
    response = test_client.get('/anki/request_permission')
    response_json = response.json
    logging.info(response_json)
    assert 'success' in response_json
    # Optionally, assert the success is True
    assert response_json['success'] is True
    # To further verify the response structure, you might want to check the 'data' part
    assert 'permission' in response_json['data']
    assert response_json['data']['permission'] == 'granted'