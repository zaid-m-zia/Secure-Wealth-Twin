def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Runtime State User",
            "email": "runtime-state@example.com",
            "password": "StrongPass123!",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "runtime-state@example.com", "password": "StrongPass123!"},
    )
    return login_response.json(), {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def test_dashboard_and_analytics_read_persisted_runtime_state(client) -> None:
    login_payload, headers = _auth_headers(client)
    customer_id = "CUST-RUNTIME-SYNC"
    client.post(
        "/api/v1/customers",
        json={
            "customer_id": customer_id,
            "dob": "1990-04-04",
            "gender": "F",
            "location": "PUNE",
            "account_balance": 50000,
        },
        headers=headers,
    )
    transaction_response = client.post(
        "/api/v1/transactions",
        json={
            "transaction_id": "TX-RUNTIME-SYNC",
            "customer_id": customer_id,
            "transaction_date": "2026-07-28",
            "transaction_time": "09:30:00",
            "transaction_amount": 5000,
        },
        headers=headers,
    )
    assert transaction_response.status_code == 201

    dashboard_response = client.get(f"/api/v1/dashboard/{customer_id}", headers=headers)
    analytics_response = client.get(f"/api/v1/analytics/transactions?customer_id={customer_id}", headers=headers)
    fraud_response = client.get(f"/api/v1/analytics/fraud?customer_id={customer_id}", headers=headers)
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["data"]["cards"]["total_transactions"] == 1
    assert analytics_response.json()["data"]["transactions"] == 1
    assert analytics_response.json()["data"]["total_transaction_amount"] == 5000
    assert fraud_response.json()["data"]["transactions_analyzed"] == 1

    update_response = client.put(
        "/api/v1/transactions/TX-RUNTIME-SYNC",
        json={"transaction_amount": 7500},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert client.get(f"/api/v1/analytics/transactions?customer_id={customer_id}", headers=headers).json()["data"]["total_transaction_amount"] == 7500

    client.post("/api/v1/auth/logout", headers=headers)
    restored_login = client.post(
        "/api/v1/auth/login",
        json={"email": "runtime-state@example.com", "password": "StrongPass123!"},
    )
    restored_headers = {"Authorization": f"Bearer {restored_login.json()['access_token']}"}
    restored_dashboard = client.get(f"/api/v1/dashboard/{customer_id}", headers=restored_headers)
    assert restored_dashboard.status_code == 200
    assert restored_dashboard.json()["data"]["cards"]["total_transactions"] == 1
    assert restored_dashboard.json()["data"]["cards"]["account_balance"] == 50000
