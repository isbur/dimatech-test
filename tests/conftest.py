import pytest
from sanic import Sanic

from dimatech.main import create_app


@pytest.fixture
def app() -> Sanic:
    Sanic.test_mode = True
    return create_app()
