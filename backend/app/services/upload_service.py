from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, date, time
from io import StringIO
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory
from app.models.behavior_profile import BehaviorProfile
from app.models.customer import Customer
from app.models.digital_wealth_twin import DigitalWealthTwin
from app.models.transaction import Transaction
from app.repositories.customer_repository import CustomerRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.upload import ImportSummary
from app.services.runtime_inference_service import RuntimeInferenceService

EXPECTED_HEADERS = {
    "TransactionID",
    "CustomerID",
    "CustomerDOB",
    "CustGender",
    "CustLocation",
    "CustAccountBalance",
    "TransactionDate",
    "TransactionTime",
    "TransactionAmount (INR)",
}


class UploadService:
    def __init__(
        self,
        session: Session,
        customer_repository: CustomerRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self.session = session
        self.customer_repository = customer_repository
        self.transaction_repository = transaction_repository

    async def import_csv(self, upload: UploadFile) -> ImportSummary:
        content = await upload.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")

        normalized_headers = set(reader.fieldnames)
        missing = EXPECTED_HEADERS - normalized_headers
        if missing:
            raise ValueError(f"CSV schema is invalid. Missing columns: {', '.join(sorted(missing))}.")

        customers_created = 0
        customers_updated = 0
        transactions_created = 0
        transactions_skipped = 0
        processed = 0
        seen_transaction_ids: set[str] = set()
        customer_cache: dict[str, Customer] = {}
        created_transactions: list[Transaction] = []

        for row in reader:
            processed += 1
            transaction_id = row["TransactionID"].strip()
            customer_id = row["CustomerID"].strip()
            if not transaction_id or not customer_id:
                transactions_skipped += 1
                continue

            customer = customer_cache.get(customer_id) or self.customer_repository.get_by_customer_id(customer_id)
            customer_dob = self._parse_date(row["CustomerDOB"])
            customer_gender = row["CustGender"].strip() or None
            customer_location = row["CustLocation"].strip() or None
            account_balance = float(row["CustAccountBalance"])

            if customer is None:
                customer = Customer(
                    customer_id=customer_id,
                    dob=customer_dob,
                    gender=customer_gender,
                    location=customer_location,
                    account_balance=account_balance,
                )
                self.session.add(customer)
                self.session.add(BehaviorProfile(customer_id=customer_id))
                self.session.add(DigitalWealthTwin(customer_id=customer_id))
                self.session.add(AgentMemory(customer_id=customer_id))
                customer_cache[customer_id] = customer
                customers_created += 1
            else:
                customer.dob = customer_dob or customer.dob
                customer.gender = customer_gender or customer.gender
                customer.location = customer_location or customer.location
                customer.account_balance = account_balance
                customer_cache[customer_id] = customer
                customers_updated += 1

            if transaction_id in seen_transaction_ids or self.transaction_repository.get_by_transaction_id(transaction_id):
                transactions_skipped += 1
                continue

            transaction = Transaction(
                transaction_id=transaction_id,
                customer_id=customer_id,
                transaction_date=self._parse_date(row["TransactionDate"]),
                transaction_time=self._parse_time(row["TransactionTime"]),
                transaction_amount=float(row["TransactionAmount (INR)"]),
            )
            self.session.add(transaction)
            created_transactions.append(transaction)
            seen_transaction_ids.add(transaction_id)
            transactions_created += 1

        self.session.commit()
        runtime = RuntimeInferenceService(self.session)
        for transaction in created_transactions:
            runtime.assess_transaction(transaction)
        return ImportSummary(
            customers_created=customers_created,
            customers_updated=customers_updated,
            transactions_created=transactions_created,
            transactions_skipped=transactions_skipped,
            rows_processed=processed,
        )

    @staticmethod
    def _parse_date(raw_value: str) -> date:
        raw_value = raw_value.strip()
        if not raw_value:
            raise ValueError("Date value cannot be empty.")
        for fmt in ("%m/%d/%y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw_value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {raw_value}")

    @staticmethod
    def _parse_time(raw_value: str) -> time:
        value = raw_value.strip().zfill(6)
        if len(value) != 6 or not value.isdigit():
            raise ValueError(f"Unsupported time format: {raw_value}")
        return time(hour=int(value[0:2]), minute=int(value[2:4]), second=int(value[4:6]))
