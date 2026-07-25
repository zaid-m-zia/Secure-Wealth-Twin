def test_api_health_and_version(client) -> None:
    health_response = client.get("/api/v1/health")
    version_response = client.get("/api/v1/version")

    assert health_response.status_code == 200
    assert version_response.status_code == 200
    assert health_response.json()["status"] == "success"
    assert version_response.json()["data"]["app_name"] == "SecureWealth AI"
