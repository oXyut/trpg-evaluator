import logging

from fastapi.testclient import TestClient

from app.main import app
from app.utils import auth


def test_auth_middleware_blocks_request_without_token(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("FIREBASE_AUTH_DISABLED", "0")

    response = client.get("/v1/scenarios")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_auth_middleware_accepts_valid_token(monkeypatch, caplog):
    client = TestClient(app)
    monkeypatch.setenv("FIREBASE_AUTH_DISABLED", "0")

    def fake_verify(token: str):
        assert token == "valid-token"
        return auth.FirebaseUser(uid="user-123", email="demo@example.com", email_verified=True)

    monkeypatch.setattr(auth, "verify_firebase_token", fake_verify)
    import app.main as main_module  # local import to avoid cycle
    monkeypatch.setattr(main_module, "verify_firebase_token", fake_verify)
    with caplog.at_level(logging.INFO, logger="trpg_evaluator"):
        response = client.get("/v1/scenarios", headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 200
    assert response.json() == []
    assert any(record for record in caplog.records if getattr(record, "structured", {}).get("event") == "auth.token.verified")


def test_auth_disabled_allows_requests(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("FIREBASE_AUTH_DISABLED", "1")
    response = client.get("/v1/scenarios")
    assert response.status_code == 200
