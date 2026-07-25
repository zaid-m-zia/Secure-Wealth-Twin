from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Customer)

    def get_by_customer_id(self, customer_id: str) -> Optional[Customer]:
        statement = select(Customer).where(Customer.customer_id == customer_id)
        return self.session.execute(statement).scalars().first()
