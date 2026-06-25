"""
Pytest configuration and shared fixtures.

Fixtures here are available to every test in the suite without importing.
Add feature-specific fixtures in tests/unit/ and tests/integration/ conftest files.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import create_app


@pytest.fixture(scope="session")
def app():
    """A fresh FastAPI app instance for the entire test session."""
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """Synchronous test client — use for simple endpoint smoke tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client(app):
    """
    Async test client — use for tests that await responses or
    need to interact with async application state.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c
