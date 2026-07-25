from sqlalchemy.orm import Session

from app.models.behavior_profile import BehaviorProfile
from app.repositories.base_repository import BaseRepository


class BehaviorProfileRepository(BaseRepository[BehaviorProfile]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, BehaviorProfile)
