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


def test_all_banking_operations_share_one_persisted_runtime_state(client) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Banking Operations User",
            "email": "banking-operations@example.com",
            "password": "StrongPass123!",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "banking-operations@example.com", "password": "StrongPass123!"},
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    customer_id = "CUST-BANKING-OPS"
    assert client.post(
        "/api/v1/customers",
        json={
            "customer_id": customer_id,
            "dob": "1992-08-10",
            "gender": "F",
            "location": "MUMBAI",
            "account_balance": 50000,
        },
        headers=headers,
    ).status_code == 201

    operations = [
        ("salary", "income", "Employer", 10000),
        ("deposit", "income", "Bank deposit", 1000),
        ("withdrawal", "cash", "ATM", 100),
        ("transfer", "transfer", "Transfer recipient", 200),
        ("merchant_payment", "shopping", "Merchant", 300),
        ("upi_payment", "payments", "UPI merchant", 50),
        ("bill", "utilities", "Electricity", 150),
        ("subscription", "subscriptions", "Netflix", 100),
    ]
    expected_balance = 50000
    for index, (transaction_type, category, merchant, amount) in enumerate(operations):
        response = client.post(
            "/api/v1/transactions",
            json={
                "transaction_id": f"TX-BANKING-OPS-{index}",
                "customer_id": customer_id,
                "transaction_date": "2026-07-29",
                "transaction_time": f"10:{index:02d}:00",
                "transaction_amount": amount,
                "transaction_type": transaction_type,
                "category": category,
                "merchant": merchant,
                "status": "completed",
            },
            headers=headers,
        )
        assert response.status_code == 201
        expected_balance += amount if transaction_type in {"salary", "deposit"} else -amount
        balances = (
            client.get(f"/api/v1/customers/{customer_id}", headers=headers).json()["data"]["account_balance"],
            client.get(f"/api/v1/dashboard/{customer_id}", headers=headers).json()["data"]["cards"]["account_balance"],
            client.get(
                f"/api/v1/analytics/transactions?customer_id={customer_id}", headers=headers
            ).json()["data"]["account_balance"],
            client.get(
                f"/api/v1/analytics/wealth?customer_id={customer_id}", headers=headers
            ).json()["data"]["account_balance"],
        )
        assert balances == (expected_balance,) * 4

    customer = client.get(f"/api/v1/customers/{customer_id}", headers=headers).json()["data"]
    dashboard = client.get(f"/api/v1/dashboard/{customer_id}", headers=headers).json()["data"]
    transactions = client.get(
        f"/api/v1/analytics/transactions?customer_id={customer_id}", headers=headers
    ).json()["data"]
    wealth = client.get(
        f"/api/v1/analytics/wealth?customer_id={customer_id}", headers=headers
    ).json()["data"]
    recommendations = client.get(
        f"/api/v1/recommendations/{customer_id}", headers=headers
    ).json()["data"]

    assert customer["account_balance"] == 60100
    assert dashboard["cards"]["account_balance"] == 60100
    assert transactions["account_balance"] == 60100
    assert wealth["account_balance"] == 60100
    assert transactions["income"] == 11000
    assert transactions["expenses"] == 900
    assert wealth["financial_dna"]["monthly_income"] == 11000
    assert wealth["financial_dna"]["average_monthly_spending"] == 900
    assert any("estimated monthly income of 11000.00" in item["recommendation"] for item in recommendations)

    for path in (
        f"/api/v1/customers/{customer_id}/profile",
        f"/api/v1/customers/{customer_id}/intelligence",
        f"/api/v1/behavior/{customer_id}",
        f"/api/v1/behavioral-intelligence/{customer_id}",
        f"/api/v1/reports/{customer_id}",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
