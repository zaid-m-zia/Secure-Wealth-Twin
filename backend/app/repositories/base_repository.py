from collections.abc import Iterable
from typing import Generic, Optional, TypeVar

from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model_type: type[ModelType]) -> None:
        self.session = session
        self.model_type = model_type

    def get(self, entity_id: object) -> Optional[ModelType]:
        return self.session.get(self.model_type, entity_id)

    def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.session.delete(instance)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: Optional[dict[str, object]] = None,
    ) -> tuple[list[ModelType], int]:
        statement: Select[tuple[ModelType]] = select(self.model_type)
        count_statement = select(self.model_type)

        if filters:
            for field_name, field_value in filters.items():
                if field_value is None:
                    continue
                column = getattr(self.model_type, field_name, None)
                if column is None:
                    continue
                statement = statement.where(column == field_value)
                count_statement = count_statement.where(column == field_value)

        order_column = getattr(self.model_type, sort_by, None)
        if order_column is not None:
            statement = statement.order_by(desc(order_column) if sort_order.lower() == "desc" else asc(order_column))

        total = len(self.session.execute(count_statement).scalars().all())
        results = self.session.execute(statement.offset(offset).limit(limit)).scalars().all()
        return results, total

    def extend(self, instances: Iterable[ModelType]) -> None:
        self.session.add_all(list(instances))
