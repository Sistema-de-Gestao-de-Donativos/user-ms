import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app import create_app
from app.settings import Settings


@pytest.fixture(scope="session")
def app():
    """
    Initialize the FastAPI app which will be used to
    create a sync and an async client to test the API.

    The "session" scope signals pytest to instantiate
    this app once and reuse it for all tests.
    """

    app = create_app()
    return app


@pytest.fixture(scope="session")
def client(app):
    """
    Initialize a test client for the FastAPI app.

    This wrapper will route the requests from the tests
    to the endpoints of your application.

    The "session" scope signals pytest to instantiate
    this client once and reuse it for all tests.
    """

    return TestClient(app)


@pytest.fixture(scope="function")
def async_client(app):
    """
    Initialize a test client for the FastAPI app.

    This wrapper will route the requests from the tests
    to the endpoints of your application.

    The "function" scope signals pytest to instantiate
    this client once for each test function.
    """

    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture(scope="session")
def headers():
    sets = Settings()  # type: ignore
    return {"X-Access-Token": sets.API_SECRET}
