def test_auth_register_login_refresh_profile_and_logout(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Ava Morgan",
            "email": "ava@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 200
    register_payload = register_response.json()
    assert register_payload["status"] == "success"
    assert register_payload["access_token"]
    assert register_payload["refresh_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ava@example.com",
            "password": "StrongPass123!",
        },
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    access_token = login_payload["access_token"]
    refresh_token = login_payload["refresh_token"]

    profile_response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "ava@example.com"

    update_response = client.put(
        "/api/v1/auth/profile",
        json={"full_name": "Ava Updated"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Ava Updated"

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["status"] == "success"

    revoked_response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert revoked_response.status_code == 401
