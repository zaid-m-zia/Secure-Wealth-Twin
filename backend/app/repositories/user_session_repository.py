from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserSession
from app.repositories.base_repository import BaseRepository


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UserSession)

    def get_by_token_id(self, token_id: str) -> Optional[UserSession]:
        return self.session.execute(
            select(UserSession).where(UserSession.token_id == token_id)
        ).scalars().first()
