import pytest

from faker import Faker
from fastapi.testclient import TestClient


fake = Faker()


@pytest.fixture(autouse=True, scope="module")
def app():
    from knwl_api import create_app
    return create_app()


@pytest.fixture(autouse=True, scope="module")
def client(app):
    client = TestClient(app)
    return client
