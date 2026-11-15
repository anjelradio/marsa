from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoints_return_ok() -> None:
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["database"]["status"] == "connected"
