"""
Minimal smoke test for the SentryView Flask backend.

Validates that the app imports cleanly and that core API routes are
registered. Database/Redis access is stubbed so the suite runs without
external services.
"""
import types

import pytest


@pytest.fixture
def app():
    import backend.app as app_module

    app_module.app.config["TESTING"] = True
    # Disable rate limiting so the suite runs without a Redis backend.
    app_module.limiter.enabled = False
    # Stub external dependencies so routes can be exercised offline.
    app_module.get_db = lambda: types.SimpleNamespace(
        cursor=lambda: types.SimpleNamespace(
            execute=lambda *a, **k: None, fetchone=lambda: None, __enter__=lambda s: s, __exit__=lambda *a: False
        ),
        commit=lambda: None, rollback=lambda: None, close=lambda: None,
    )
    app_module.get_redis = lambda: types.SimpleNamespace(ping=lambda: True)
    return app_module.app


def test_app_imports():
    import backend.app  # noqa: F401
    assert backend.app.app is not None


def test_routes_registered(app):
    rules = {str(r) for r in app.url_map.iter_rules()}
    for needed in ("/api/auth/login", "/api/streams", "/api/recordings", "/health"):
        assert needed in rules, f"missing route {needed}"


def test_health_endpoint(app):
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "database" in data and "redis" in data


def test_register_validation(app):
    client = app.test_client()
    resp = client.post("/api/auth/register", json={"username": "x", "password": "short"})
    assert resp.status_code == 400
