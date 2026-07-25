from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint_returns_structured_payload() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["message"]
    assert payload["request_id"]
    assert payload["data"]["app_name"] == "SecureWealth AI"
