from datetime import date
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fraud import FraudAnalysis
from app.models.transaction import Transaction
from app.repositories.customer_repository import CustomerRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.runtime_inference_service import RuntimeInferenceService


class TransactionService:
    def __init__(self, session: Session, repository: TransactionRepository, customer_repository: CustomerRepository) -> None:
        self.session = session
        self.repository = repository
        self.customer_repository = customer_repository

    def create_transaction(self, payload: TransactionCreate) -> Transaction:
        if self.repository.get_by_transaction_id(payload.transaction_id):
            raise ValueError("A transaction with this ID already exists.")
        if self.customer_repository.get_by_customer_id(payload.customer_id) is None:
            raise KeyError("Customer not found.")

        transaction = Transaction(**payload.model_dump())
        self.repository.add(transaction)
        self._apply_balance(payload.customer_id, transaction.transaction_type, transaction.transaction_amount)
        self.session.commit()
        self.session.refresh(transaction)
        RuntimeInferenceService(self.session).assess_transaction(transaction)
        return transaction

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return self.repository.get_by_transaction_id(transaction_id)

    def list_transactions(
        self,
        *,
        offset: int,
        limit: int,
        sort_by: str,
        sort_order: str,
        customer_id: Optional[str] = None,
        transaction_date_from: Optional[date] = None,
        transaction_date_to: Optional[date] = None,
    ) -> tuple[list[Transaction], int]:
        return self.repository.list_filtered(
            customer_id=customer_id,
            transaction_date_from=transaction_date_from,
            transaction_date_to=transaction_date_to,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def update_transaction(self, transaction_id: str, payload: TransactionUpdate) -> Transaction:
        transaction = self.repository.get_by_transaction_id(transaction_id)
        if transaction is None:
            raise KeyError("Transaction not found.")

        update_data = payload.model_dump(exclude_unset=True)
        if "customer_id" in update_data and self.customer_repository.get_by_customer_id(update_data["customer_id"]) is None:
            raise KeyError("Customer not found.")

        previous_customer_id = transaction.customer_id
        previous_type, previous_amount = transaction.transaction_type, transaction.transaction_amount
        # Reverse the original posted movement before applying its replacement.
        self._apply_balance(previous_customer_id, previous_type, previous_amount, reverse=True)
        for field_name, field_value in update_data.items():
            setattr(transaction, field_name, field_value)

        self._apply_balance(transaction.customer_id, transaction.transaction_type, transaction.transaction_amount)

        self.session.commit()
        self.session.refresh(transaction)
        runtime = RuntimeInferenceService(self.session)
        runtime.assess_transaction(transaction)
        if previous_customer_id != transaction.customer_id:
            runtime.refresh_customer_intelligence(previous_customer_id)
        return transaction

    def delete_transaction(self, transaction_id: str) -> None:
        transaction = self.repository.get_by_transaction_id(transaction_id)
        if transaction is None:
            raise KeyError("Transaction not found.")
        customer_id = transaction.customer_id
        self._apply_balance(customer_id, transaction.transaction_type, transaction.transaction_amount, reverse=True)
        self.repository.delete(transaction)
        self.session.commit()
        RuntimeInferenceService(self.session).refresh_customer_intelligence(customer_id)

    def get_statistics(self) -> dict[str, Any]:
        total, total_amount, average_amount = self.session.execute(
            select(
                func.count(Transaction.transaction_id),
                func.coalesce(func.sum(Transaction.transaction_amount), 0.0),
                func.coalesce(func.avg(Transaction.transaction_amount), 0.0),
            )
        ).one()
        return {
            "total_transactions": int(total),
            "total_transaction_amount": float(total_amount),
            "average_transaction_amount": round(float(average_amount), 2),
        }

    @staticmethod
    def _is_credit(transaction_type: str) -> bool:
        return transaction_type in {"deposit", "salary", "income", "refund"}

    def _apply_balance(self, customer_id: str, transaction_type: str, amount: float, *, reverse: bool = False) -> None:
        customer = self.customer_repository.get_by_customer_id(customer_id)
        if customer is None:
            raise KeyError("Customer not found.")
        if transaction_type == "legacy":
            return
        delta = float(amount) if self._is_credit(transaction_type) else -float(amount)
        customer.account_balance += -delta if reverse else delta
