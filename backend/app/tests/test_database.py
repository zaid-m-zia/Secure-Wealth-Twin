from datetime import date, time

from app.models.customer import Customer
from app.models.transaction import Transaction


def test_database_models_and_relationships(db_session) -> None:
    customer = Customer(
        customer_id="CUST-001",
        dob=date(1994, 1, 10),
        gender="F",
        location="PUNE",
        account_balance=25000.0,
    )
    transaction = Transaction(
        transaction_id="TX-001",
        customer_id="CUST-001",
        transaction_date=date(2026, 1, 12),
        transaction_time=time(14, 32, 7),
        transaction_amount=1200.0,
    )
    db_session.add(customer)
    db_session.add(transaction)
    db_session.commit()

    loaded_customer = db_session.get(Customer, "CUST-001")
    assert loaded_customer is not None
    assert len(loaded_customer.transactions) == 1
    assert loaded_customer.transactions[0].transaction_id == "TX-001"
