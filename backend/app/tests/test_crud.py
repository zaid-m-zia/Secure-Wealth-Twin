from datetime import date, time


def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Crud User",
            "email": "crud@example.com",
            "password": "StrongPass123!",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "crud@example.com", "password": "StrongPass123!"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_customer_and_transaction_crud(client) -> None:
    headers = _auth_headers(client)

    user_response = client.post(
        "/api/v1/users",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "password": "StrongPass123!"},
        headers=headers,
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["data"]["id"]

    customer_response = client.post(
        "/api/v1/customers",
        json={
            "customer_id": "CUST-100",
            "dob": "1990-04-04",
            "gender": "F",
            "location": "PUNE",
            "account_balance": 50000,
        },
        headers=headers,
    )
    assert customer_response.status_code == 201

    transaction_response = client.post(
        "/api/v1/transactions",
        json={
            "transaction_id": "TX-100",
            "customer_id": "CUST-100",
            "transaction_date": "2026-07-18",
            "transaction_time": "14:30:10",
            "transaction_amount": 1500,
        },
        headers=headers,
    )
    assert transaction_response.status_code == 201

    list_transactions = client.get("/api/v1/transactions?page=1&page_size=5", headers=headers)
    assert list_transactions.status_code == 200
    assert list_transactions.json()["data"]["meta"]["total"] >= 1

    update_customer = client.put(
        "/api/v1/customers/CUST-100",
        json={"location": "MUMBAI"},
        headers=headers,
    )
    assert update_customer.status_code == 200
    assert update_customer.json()["data"]["location"] == "MUMBAI"

    delete_transaction = client.delete("/api/v1/transactions/TX-100", headers=headers)
    assert delete_transaction.status_code == 200

    delete_user = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert delete_user.status_code == 200


def test_customer_and_transaction_filters(client) -> None:
    headers = _auth_headers(client)
    client.post(
        "/api/v1/customers",
        json={
            "customer_id": "CUST-200",
            "dob": "1985-01-01",
            "gender": "M",
            "location": "DELHI",
            "account_balance": 10000,
        },
        headers=headers,
    )
    client.post(
        "/api/v1/transactions",
        json={
            "transaction_id": "TX-200",
            "customer_id": "CUST-200",
            "transaction_date": "2026-07-18",
            "transaction_time": "10:00:00",
            "transaction_amount": 500,
        },
        headers=headers,
    )

    response = client.get("/api/v1/transactions?customer_id=CUST-200", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["meta"]["total"] >= 1
