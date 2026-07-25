from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Transaction)

    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        statement = select(Transaction).where(Transaction.transaction_id == transaction_id)
        return self.session.execute(statement).scalars().first()

    def list_filtered(
        self,
        *,
        customer_id: Optional[str] = None,
        transaction_date_from: Optional[object] = None,
        transaction_date_to: Optional[object] = None,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Transaction], int]:
        filters = []
        if customer_id:
            filters.append(Transaction.customer_id == customer_id)
        if transaction_date_from is not None:
            filters.append(Transaction.transaction_date >= transaction_date_from)
        if transaction_date_to is not None:
            filters.append(Transaction.transaction_date <= transaction_date_to)

        statement = select(Transaction)
        count_statement = select(Transaction)
        if filters:
            statement = statement.where(and_(*filters))
            count_statement = count_statement.where(and_(*filters))

        order_column = getattr(Transaction, sort_by, None)
        if order_column is not None:
            from sqlalchemy import asc, desc

            statement = statement.order_by(desc(order_column) if sort_order.lower() == "desc" else asc(order_column))

        total = len(self.session.execute(count_statement).scalars().all())
        results = self.session.execute(statement.offset(offset).limit(limit)).scalars().all()
        return results, total
