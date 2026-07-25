from io import BytesIO


def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Uploader",
            "email": "upload@example.com",
            "password": "StrongPass123!",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "upload@example.com", "password": "StrongPass123!"},
    )
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def test_csv_upload_imports_customers_and_transactions(client) -> None:
    headers = _auth_headers(client)
    csv_content = (
        "TransactionID,CustomerID,CustomerDOB,CustGender,CustLocation,CustAccountBalance,TransactionDate,TransactionTime,TransactionAmount (INR)\n"
        "T-1,CUST-CSV-1,10/1/94,F,PUNE,10000,2/8/16,143207,250\n"
        "T-2,CUST-CSV-1,10/1/94,F,PUNE,10000,2/8/16,143307,300\n"
    )
    response = client.post(
        "/api/v1/upload/transactions",
        headers=headers,
        files={"file": ("bank_transactions.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["data"]["customers_created"] == 1
    assert payload["data"]["transactions_created"] == 2

    duplicate_response = client.post(
        "/api/v1/upload/transactions",
        headers=headers,
        files={"file": ("bank_transactions.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )
    assert duplicate_response.status_code == 201
    assert duplicate_response.json()["data"]["transactions_skipped"] >= 2
