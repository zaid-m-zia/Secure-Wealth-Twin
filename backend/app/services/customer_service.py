from typing import Optional

from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory
from app.models.behavior_profile import BehaviorProfile
from app.models.customer import Customer
from app.models.digital_wealth_twin import DigitalWealthTwin
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, session: Session, repository: CustomerRepository) -> None:
        self.session = session
        self.repository = repository

    def create_customer(self, payload: CustomerCreate) -> Customer:
        if self.repository.get_by_customer_id(payload.customer_id):
            raise ValueError("A customer with this ID already exists.")

        customer = Customer(
            customer_id=payload.customer_id,
            dob=payload.dob,
            gender=payload.gender,
            location=payload.location,
            account_balance=payload.account_balance,
        )
        self.session.add(customer)
        self.session.add(BehaviorProfile(customer_id=payload.customer_id))
        self.session.add(DigitalWealthTwin(customer_id=payload.customer_id))
        self.session.add(AgentMemory(customer_id=payload.customer_id))
        self.session.commit()
        self.session.refresh(customer)
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.repository.get_by_customer_id(customer_id)

    def list_customers(self, *, offset: int, limit: int, sort_by: str, sort_order: str, filters: Optional[dict[str, object]] = None) -> tuple[list[Customer], int]:
        return self.repository.list(offset=offset, limit=limit, sort_by=sort_by, sort_order=sort_order, filters=filters)

    def update_customer(self, customer_id: str, payload: CustomerUpdate) -> Customer:
        customer = self.repository.get_by_customer_id(customer_id)
        if customer is None:
            raise KeyError("Customer not found.")

        update_data = payload.model_dump(exclude_unset=True)
        for field_name, field_value in update_data.items():
            setattr(customer, field_name, field_value)

        self.session.commit()
        self.session.refresh(customer)
        return customer

    def delete_customer(self, customer_id: str) -> None:
        customer = self.repository.get_by_customer_id(customer_id)
        if customer is None:
            raise KeyError("Customer not found.")
        self.repository.delete(customer)
        self.session.commit()
