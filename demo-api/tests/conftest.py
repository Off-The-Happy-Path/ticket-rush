import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import create_app


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Admin endpoints on, bug off, no artificial latency."""
    monkeypatch.setattr(settings, "admin_enabled", True)
    monkeypatch.setattr(settings, "oversell_bug", False)
    monkeypatch.setattr(settings, "db_latency_ms", 0)
    monkeypatch.setattr(settings, "payment_latency_ms", 0)


@pytest.fixture
def client():
    with TestClient(create_app()) as client:   # startup loads fresh seed data
        yield client
