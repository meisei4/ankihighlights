from unittest.mock import Mock
from flask_app import create_app


def test_create_app():
    connection_injection = Mock()
    ankikindle_injection = Mock()
    ankiconnect_wrapper_injection = Mock()

    app = create_app(connection_injection, ankikindle_injection, ankiconnect_wrapper_injection)

    assert app is not None
    # Add more assertions to check if the app has the correct configuration or routes, if necessary
