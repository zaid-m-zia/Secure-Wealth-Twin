from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: Session, repository: UserRepository) -> None:
        self.session = session
        self.repository = repository

    def create_user(self, payload: UserCreate) -> User:
        if self.repository.get_by_email(payload.email):
            raise ValueError("A user with this email already exists.")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        self.repository.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("Unable to create user.") from exc
        self.session.refresh(user)
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.repository.get_by_email(email)

    def list_users(self, *, offset: int, limit: int, sort_by: str, sort_order: str) -> tuple[list[User], int]:
        return self.repository.list(offset=offset, limit=limit, sort_by=sort_by, sort_order=sort_order)

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.repository.get(user_id)
        if user is None:
            raise KeyError("User not found.")

        update_data = payload.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != user.email and self.repository.get_by_email(update_data["email"]):
            raise ValueError("A user with this email already exists.")

        if "full_name" in update_data:
            user.full_name = update_data["full_name"]
        if "email" in update_data:
            user.email = update_data["email"]
        if "password" in update_data:
            user.password_hash = hash_password(update_data["password"])

        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.repository.get(user_id)
        if user is None:
            raise KeyError("User not found.")
        self.repository.delete(user)
        self.session.commit()
