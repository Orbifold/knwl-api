import pytest

from faker import Faker
from fastapi.testclient import TestClient

from fastmcp import Client

fake = Faker()


@pytest.fixture(autouse=True, scope="module")
def app():
    from knwl_api import create_app
    return create_app()


@pytest.fixture(autouse=True, scope="module")
def client(app):
    client = TestClient(app)
    return client


@pytest.fixture(autouse=True, scope="module")
def mcp_client(app):
    client = Client("http://localhost:9030/mcp/")
    return client
