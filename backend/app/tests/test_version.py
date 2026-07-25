from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_version_endpoint_returns_structured_payload() -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["data"]["app_name"] == "SecureWealth AI"
    assert payload["data"]["app_version"] == "0.1.0"
